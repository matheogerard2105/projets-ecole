"""
Ingestion de l'entité `passengers`, découpée en 3 fonctions bronze/silver/gold (même structure que
`ingest_airports.py`).

Deux systèmes sources (CRM anglophone et francophone) livrent chacun un extrait COMPLET avec un
schéma différent (noms de colonnes, valeurs de genre, format de date). Le silver les unifie en un
schéma unique ; les passenger_id ne se chevauchent pas entre les deux sources, la consolidation
est donc un UNION ALL après normalisation. Dimension évolutive (corrections, suppressions) :
- silver_passengers : état courant, upsert par passenger_id + soft delete ;
- silver_passengers_history : historisation SCD2 (bonus).
"""
from datetime import date

from common import (
    fetch_csv,
    get_connection,
    is_stale_snapshot,
    last_loaded_date,
    log_load,
    scd2_snapshot,
    snapshot_date,
    upsert_snapshot,
)

PASSENGER_COLS = [
    "first_name",
    "last_name",
    "gender",
    "nationality",
    "email",
    "birth_date",
    "signup_date",
    "source_system",
]


def _snapshot_files(day: date = None, init: bool = False):
    if init:
        return [("init", "passengers_en.csv"), ("init", "passengers_fr.csv")]
    assert day is not None
    return [
        ("2025-09", f"passengers_en_{day.isoformat()}.csv"),
        ("2025-09", f"passengers_fr_{day.isoformat()}.csv"),
    ]


def ingest_bronze(day: date = None, init: bool = False):
    """Télécharge les deux snapshots du jour (EN et FR, ou ceux de init/) vers bronze/."""
    for subdir, filename in _snapshot_files(day, init):
        fetch_csv(subdir, filename)


def create_silver_table(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_passengers (
            passenger_id VARCHAR PRIMARY KEY,
            first_name VARCHAR,
            last_name VARCHAR,
            gender VARCHAR,
            nationality VARCHAR,
            email VARCHAR,
            birth_date DATE,
            signup_date DATE,
            source_system VARCHAR,
            is_active BOOLEAN,
            deleted_date DATE,
            insert_timestamp TIMESTAMP,
            update_timestamp TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_passengers_history (
            passenger_id VARCHAR,
            first_name VARCHAR,
            last_name VARCHAR,
            gender VARCHAR,
            nationality VARCHAR,
            email VARCHAR,
            birth_date DATE,
            signup_date DATE,
            source_system VARCHAR,
            valid_from DATE,
            valid_to DATE,
            is_current BOOLEAN,
            insert_timestamp TIMESTAMP,
            update_timestamp TIMESTAMP
        )
    """)


def ingest_silver(day: date = None, init: bool = False):
    """Relit les deux snapshots depuis bronze/, les unifie, puis upsert + SCD2 par passenger_id."""
    (en_dir, en_file), (fr_dir, fr_file) = _snapshot_files(day, init)
    df_en = fetch_csv(en_dir, en_file)
    df_fr = fetch_csv(fr_dir, fr_file)
    snap_date = snapshot_date(day, init)

    con = get_connection()
    create_silver_table(con)
    if is_stale_snapshot(con, "passengers", snap_date):
        con.close()
        return
    con.register("raw_en", df_en)
    con.register("raw_fr", df_fr)
    con.execute("BEGIN TRANSACTION")
    # Schéma unique : noms de colonnes anglais, genre en Male/Female, dates ISO typées,
    # email en minuscules, et une colonne source_system pour garder la traçabilité.
    con.execute("""
        CREATE OR REPLACE TEMP TABLE snapshot AS
        SELECT
            trim(passenger_id) AS passenger_id,
            trim(first_name) AS first_name,
            trim(last_name) AS last_name,
            CASE trim(gender) WHEN 'Male' THEN 'Male' WHEN 'Female' THEN 'Female' END AS gender,
            trim(nationality) AS nationality,
            lower(trim(email)) AS email,
            CAST(birth_date AS DATE) AS birth_date,
            CAST(signup_date AS DATE) AS signup_date,
            'EN' AS source_system
        FROM raw_en
        UNION ALL
        SELECT
            trim(id_passager),
            trim(prenom),
            trim(nom),
            CASE trim(genre) WHEN 'Homme' THEN 'Male' WHEN 'Femme' THEN 'Female' END,
            trim(nationalite),
            lower(trim(email)),
            CAST(strptime(date_naissance, '%d/%m/%Y') AS DATE),
            CAST(strptime(date_inscription, '%d/%m/%Y') AS DATE),
            'FR'
        FROM raw_fr
    """)
    dup = con.execute(
        "SELECT count(*) - count(DISTINCT passenger_id) FROM snapshot"
    ).fetchone()[0]
    if dup:
        con.execute("ROLLBACK")
        con.close()
        raise ValueError(f"{dup} passenger_id présents dans les deux sources le {snap_date}")

    upsert_snapshot(con, "silver_passengers", "passenger_id", PASSENGER_COLS, snap_date)
    scd2_snapshot(con, "silver_passengers_history", "passenger_id", PASSENGER_COLS, snap_date)
    log_load(con, "passengers", snap_date, len(df_en) + len(df_fr))
    con.execute("COMMIT")
    con.execute("DROP TABLE snapshot")
    con.unregister("raw_en")
    con.unregister("raw_fr")
    con.close()


# Tranches d'âge classiques du transport aérien / marketing.
_AGE_GROUP_SQL = """
    CASE
        WHEN age < 18 THEN '0-17'
        WHEN age < 25 THEN '18-24'
        WHEN age < 35 THEN '25-34'
        WHEN age < 45 THEN '35-44'
        WHEN age < 55 THEN '45-54'
        WHEN age < 65 THEN '55-64'
        ELSE '65+'
    END
"""


def ingest_gold():
    """Reconstruit dim_passenger (état courant, âge et tranche d'âge) et dim_passenger_history.

    L'âge est calculé à la date du dernier snapshot passagers chargé, et non à la date système :
    la gold reste ainsi déterministe (rejouer le pipeline un autre jour donne le même résultat).
    """
    con = get_connection()
    ref_date = last_loaded_date(con, "passengers")
    con.execute(
        f"""
        CREATE OR REPLACE TABLE dim_passenger AS
        WITH p AS (
            SELECT *, CAST(date_part('year', age(CAST(? AS DATE), birth_date)) AS INTEGER) AS age
            FROM silver_passengers
        )
        SELECT
            passenger_id, first_name, last_name, first_name || ' ' || last_name AS full_name,
            gender, nationality, email, birth_date, signup_date,
            CAST(? AS DATE) AS age_reference_date, age, {_AGE_GROUP_SQL} AS age_group,
            source_system, is_active, deleted_date, insert_timestamp, update_timestamp
        FROM p
        """,
        [ref_date, ref_date],
    )
    con.execute("""
        CREATE OR REPLACE TABLE dim_passenger_history AS
        SELECT
            passenger_id || '#' || strftime(valid_from, '%Y%m%d') AS passenger_version_key,
            *
        FROM silver_passengers_history
    """)
    con.close()


def init():
    ingest_bronze(init=True)
    ingest_silver(init=True)
    ingest_gold()
    print("Passagers (init) ingérés.")


if __name__ == "__main__":
    init()
