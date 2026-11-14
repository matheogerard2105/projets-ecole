"""
Ingestion de l'entité `flights`, découpée en 3 fonctions bronze/silver/gold (même structure que
`ingest_airports.py`).

Les fichiers flights sont des extraits COMPLETS (toutes les lignes connues à la fin du jour) qui
changent souvent : ajouts, modifications (horaire, avion, date) et suppressions. C'est un
référentiel évolutif, donc une dimension :
- silver_flights : état courant, upsert par flight_id + soft delete (is_active / deleted_date) ;
- silver_flights_history : historisation SCD2 (bonus), une ligne par version d'un vol.
"""
from datetime import date

from common import (
    fetch_csv,
    get_connection,
    is_stale_snapshot,
    log_load,
    scd2_snapshot,
    snapshot_date,
    upsert_snapshot,
)

FLIGHT_COLS = [
    "flight_number",
    "airline",
    "origin_airport_id",
    "destination_airport_id",
    "flight_date",
    "departure_time",
    "arrival_time",
    "aircraft_type",
]


def _snapshot_file(day: date = None, init: bool = False):
    if init:
        return "init", "flights.csv"
    assert day is not None
    return "2025-09", f"flights_{day.isoformat()}.csv"


def ingest_bronze(day: date = None, init: bool = False):
    """Télécharge le snapshot flights du jour (ou de init/) vers bronze/."""
    subdir, filename = _snapshot_file(day, init)
    fetch_csv(subdir, filename)


def create_silver_table(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_flights (
            flight_id VARCHAR PRIMARY KEY,
            flight_number VARCHAR,
            airline VARCHAR,
            origin_airport_id VARCHAR,
            destination_airport_id VARCHAR,
            flight_date DATE,
            departure_time TIME,
            arrival_time TIME,
            aircraft_type VARCHAR,
            is_active BOOLEAN,
            deleted_date DATE,
            insert_timestamp TIMESTAMP,
            update_timestamp TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_flights_history (
            flight_id VARCHAR,
            flight_number VARCHAR,
            airline VARCHAR,
            origin_airport_id VARCHAR,
            destination_airport_id VARCHAR,
            flight_date DATE,
            departure_time TIME,
            arrival_time TIME,
            aircraft_type VARCHAR,
            valid_from DATE,
            valid_to DATE,
            is_current BOOLEAN,
            insert_timestamp TIMESTAMP,
            update_timestamp TIMESTAMP
        )
    """)


def ingest_silver(day: date = None, init: bool = False):
    """Relit le snapshot depuis bronze/, le type, puis l'upsert (état courant) et l'historise (SCD2)."""
    subdir, filename = _snapshot_file(day, init)
    df = fetch_csv(subdir, filename)
    snap_date = snapshot_date(day, init)

    con = get_connection()
    create_silver_table(con)
    if is_stale_snapshot(con, "flights", snap_date):
        con.close()
        return
    con.register("raw_snapshot", df)
    con.execute("BEGIN TRANSACTION")
    # Typage et nettoyage léger : dates/heures en vrais types, espaces parasites retirés.
    con.execute("""
        CREATE OR REPLACE TEMP TABLE snapshot AS
        SELECT
            trim(flight_id) AS flight_id,
            trim(flight_number) AS flight_number,
            trim(airline) AS airline,
            trim(origin_airport_id) AS origin_airport_id,
            trim(destination_airport_id) AS destination_airport_id,
            CAST(flight_date AS DATE) AS flight_date,
            CAST(departure_time AS TIME) AS departure_time,
            CAST(arrival_time AS TIME) AS arrival_time,
            trim(aircraft_type) AS aircraft_type
        FROM raw_snapshot
    """)
    upsert_snapshot(con, "silver_flights", "flight_id", FLIGHT_COLS, snap_date)
    scd2_snapshot(con, "silver_flights_history", "flight_id", FLIGHT_COLS, snap_date)
    log_load(con, "flights", snap_date, len(df))
    con.execute("COMMIT")
    con.execute("DROP TABLE snapshot")
    con.unregister("raw_snapshot")
    con.close()


# Durée en minutes à partir des heures locales de départ/arrivée. Une arrivée "avant" le départ
# signifie une arrivée le lendemain (vol de nuit) : on ajoute alors 24 h.
_DURATION_SQL = """
    CASE
        WHEN arrival_time >= departure_time THEN date_diff('minute', departure_time, arrival_time)
        ELSE date_diff('minute', departure_time, arrival_time) + 1440
    END
"""


def ingest_gold():
    """Reconstruit dim_flight (état courant) et dim_flight_history (SCD2) depuis le silver."""
    con = get_connection()
    con.execute(f"""
        CREATE OR REPLACE TABLE dim_flight AS
        SELECT
            flight_id, flight_number, airline, origin_airport_id, destination_airport_id,
            flight_date, departure_time, arrival_time,
            {_DURATION_SQL} AS duration_minutes,
            arrival_time < departure_time AS is_overnight,
            aircraft_type, is_active, deleted_date, insert_timestamp, update_timestamp
        FROM silver_flights
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE dim_flight_history AS
        SELECT
            flight_id || '#' || strftime(valid_from, '%Y%m%d') AS flight_version_key,
            flight_id, flight_number, airline, origin_airport_id, destination_airport_id,
            flight_date, departure_time, arrival_time,
            {_DURATION_SQL} AS duration_minutes,
            arrival_time < departure_time AS is_overnight,
            aircraft_type, valid_from, valid_to, is_current, insert_timestamp, update_timestamp
        FROM silver_flights_history
    """)
    con.close()


def init():
    ingest_bronze(init=True)
    ingest_silver(init=True)
    ingest_gold()
    print("Vols (init) ingérés.")


if __name__ == "__main__":
    init()
