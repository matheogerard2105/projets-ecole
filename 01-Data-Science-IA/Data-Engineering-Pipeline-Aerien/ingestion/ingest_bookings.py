"""
Ingestion de l'entité `bookings`, découpée en 3 fonctions bronze/silver/gold (même structure que
`ingest_airports.py`).

Contrairement aux autres fichiers, bookings_<date>.csv ne contient QUE les réservations du jour :
ce sont des évènements immuables, donc la table de fait. Chargement en insert simple (une
réservation déjà connue est ignorée, jamais mise à jour), ce qui rend le chargement idempotent et
insensible à l'ordre des jours.

La gold de cette entité dépend des dimensions (dim_flight pour la compagnie, dim_currency pour la
conversion) : elle construit aussi dim_date et la table d'agrégation agg_daily_airline_revenue.
C'est pour ça que run_month.py lance le gold des bookings en dernier.
"""
from datetime import date

from common import fetch_csv, get_connection, log_load, snapshot_date


def _snapshot_file(day: date = None, init: bool = False):
    if init:
        return "init", "bookings.csv"
    assert day is not None
    return "2025-09", f"bookings_{day.isoformat()}.csv"


def ingest_bronze(day: date = None, init: bool = False):
    """Télécharge le fichier bookings du jour (ou de init/) vers bronze/."""
    subdir, filename = _snapshot_file(day, init)
    fetch_csv(subdir, filename)


def create_silver_table(con):
    # Pas de is_active / deleted_date : une réservation ne disparaît jamais de la source.
    # snapshot_date garde la trace du fichier qui a apporté la ligne (lineage).
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_bookings (
            booking_id VARCHAR PRIMARY KEY,
            passenger_id VARCHAR,
            flight_id VARCHAR,
            airport_id VARCHAR,
            seat_class VARCHAR,
            amount DECIMAL(12, 2),
            currency VARCHAR,
            booking_date DATE,
            booking_channel VARCHAR,
            snapshot_date DATE,
            insert_timestamp TIMESTAMP,
            update_timestamp TIMESTAMP
        )
    """)


def ingest_silver(day: date = None, init: bool = False):
    """Relit le fichier du jour depuis bronze/ et insère les nouvelles réservations."""
    subdir, filename = _snapshot_file(day, init)
    df = fetch_csv(subdir, filename)
    snap_date = snapshot_date(day, init)

    con = get_connection()
    create_silver_table(con)
    con.register("raw_snapshot", df)
    con.execute("BEGIN TRANSACTION")
    # Insert simple : ON CONFLICT DO NOTHING ignore une réservation déjà chargée (rejeu d'un
    # jour). QUALIFY protège d'un doublon éventuel à l'intérieur du fichier lui-même.
    con.execute(
        """
        INSERT INTO silver_bookings
        SELECT
            trim(booking_id),
            trim(passenger_id),
            trim(flight_id),
            trim(airport_id),
            trim(seat_class),
            CAST(amount AS DECIMAL(12, 2)),
            upper(trim(currency)),
            CAST(booking_date AS DATE),
            trim(booking_channel),
            CAST(? AS DATE),
            now(),
            now()
        FROM raw_snapshot
        QUALIFY row_number() OVER (PARTITION BY trim(booking_id) ORDER BY booking_date) = 1
        ON CONFLICT (booking_id) DO NOTHING
        """,
        [snap_date],
    )
    log_load(con, "bookings", snap_date, len(df))
    con.execute("COMMIT")
    con.unregister("raw_snapshot")
    con.close()


def ingest_gold():
    """Reconstruit fact_booking, dim_date et agg_daily_airline_revenue depuis le silver/gold."""
    con = get_connection()

    # Fait au grain "une réservation". Clés vers les dimensions (naturelles pour l'état courant,
    # *_version_key pour la version SCD2 valable au jour de la réservation), mesures amount et
    # amount_eur. seat_class / booking_channel / currency restent dans le fait comme dimensions
    # dégénérées (quelques valeurs, aucun attribut propre).
    con.execute("""
        CREATE OR REPLACE TABLE fact_booking AS
        SELECT
            b.booking_id,
            CAST(strftime(b.booking_date, '%Y%m%d') AS INTEGER) AS date_key,
            b.booking_date,
            b.passenger_id,
            ph.passenger_version_key,
            b.flight_id,
            fh.flight_version_key,
            b.airport_id,
            b.seat_class,
            b.booking_channel,
            b.currency,
            b.amount,
            c.rate_to_eur,
            CAST(round(b.amount * c.rate_to_eur, 2) AS DECIMAL(12, 2)) AS amount_eur,
            b.insert_timestamp,
            b.update_timestamp
        FROM silver_bookings b
        LEFT JOIN dim_currency c ON c.currency = b.currency
        LEFT JOIN dim_flight_history fh
            ON fh.flight_id = b.flight_id
            AND fh.valid_from <= b.booking_date
            AND (fh.valid_to IS NULL OR b.booking_date < fh.valid_to)
        LEFT JOIN dim_passenger_history ph
            ON ph.passenger_id = b.passenger_id
            AND ph.valid_from <= b.booking_date
            AND (ph.valid_to IS NULL OR b.booking_date < ph.valid_to)
    """)

    # Dimension calendrier, couvrant les dates de réservation ET de vol (les vols peuvent être
    # programmés après le dernier jour de réservation).
    con.execute("""
        CREATE OR REPLACE TABLE dim_date AS
        WITH bounds AS (
            SELECT
                least((SELECT min(booking_date) FROM silver_bookings),
                      (SELECT min(flight_date) FROM silver_flights)) AS d_min,
                greatest((SELECT max(booking_date) FROM silver_bookings),
                         (SELECT max(flight_date) FROM silver_flights)) AS d_max
        ),
        days AS (
            SELECT CAST(unnest(generate_series(d_min, d_max, INTERVAL 1 DAY)) AS DATE) AS d
            FROM bounds
        )
        SELECT
            CAST(strftime(d, '%Y%m%d') AS INTEGER) AS date_key,
            d AS full_date,
            year(d) AS year,
            month(d) AS month,
            day(d) AS day,
            isodow(d) AS day_of_week,
            dayname(d) AS day_name,
            isodow(d) >= 6 AS is_weekend,
            CAST(now() AS TIMESTAMP) AS insert_timestamp,
            CAST(now() AS TIMESTAMP) AS update_timestamp
        FROM days
    """)

    # Agrégat métier : chiffre d'affaires (EUR) par jour de réservation et par compagnie.
    # Les timestamps techniques reprennent ceux des réservations agrégées, ce qui les garde
    # stables d'une reconstruction à l'autre.
    con.execute("""
        CREATE OR REPLACE TABLE agg_daily_airline_revenue AS
        SELECT
            f.date_key,
            f.booking_date,
            d.airline,
            count(*) AS nb_bookings,
            sum(f.amount_eur) AS revenue_eur,
            CAST(round(avg(f.amount_eur), 2) AS DECIMAL(12, 2)) AS avg_booking_eur,
            min(f.insert_timestamp) AS insert_timestamp,
            max(f.update_timestamp) AS update_timestamp
        FROM fact_booking f
        JOIN dim_flight d ON d.flight_id = f.flight_id
        GROUP BY ALL
    """)
    con.close()


def init():
    ingest_bronze(init=True)
    ingest_silver(init=True)
    ingest_gold()
    print("Réservations (init) ingérés.")


if __name__ == "__main__":
    init()
