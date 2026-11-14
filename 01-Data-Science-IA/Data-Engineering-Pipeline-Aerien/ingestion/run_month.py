"""
Rejoue l'ingestion sur tout le mois de septembre 2025, jour par jour, comme si le pipeline avait
tourné quotidiennement.

Ordre d'exécution, pour l'init comme pour chaque jour : bronze des 4 entités, PUIS silver des 4
entités, PUIS gold des 4 entités — pas entité par entité. Pourquoi : le gold des réservations a
besoin que le silver/gold des vols du même jour soit déjà à jour (cohérence entre `airport_id` et
l'aéroport de départ du vol réservé). C'est exactement le genre de dépendance qu'un orchestrateur
comme Dagster gère pour vous (cf. section Bonus du README).

Options :
  --full-refresh        supprime warehouse.duckdb avant de commencer (bronze/ est conservé, rien
                        n'est retéléchargé) : reconstruit tout l'historique depuis zéro.
  --check-idempotence   rejoue chaque jour une deuxième fois et vérifie que l'entrepôt n'a pas
                        bougé (mêmes lignes, timestamps techniques exclus).

Dans tous les cas, le dernier jour est rejoué à la fin et comparé, et un résumé (comptes par table
+ contrôles d'intégrité) est affiché.
"""
import argparse
import os
from datetime import date, timedelta

import ingest_airports
import ingest_bookings
import ingest_flights
import ingest_passengers
from common import DB_PATH, get_connection

START = date(2025, 9, 1)
N_DAYS = 30

ENTITIES = [ingest_airports, ingest_flights, ingest_passengers, ingest_bookings]

TECH_COLS = {"insert_timestamp", "update_timestamp"}


def init_dim_currency():
    sql_path = os.path.join(os.path.dirname(__file__), "..", "sql", "init", "dim_currency.sql")
    con = get_connection()
    con.execute(open(sql_path).read())
    con.close()


def run_day(day: date = None, init: bool = False):
    for entity in ENTITIES:
        entity.ingest_bronze(day, init=init)
    for entity in ENTITIES:
        entity.ingest_silver(day, init=init)
    for entity in ENTITIES:
        entity.ingest_gold()


def fingerprint() -> dict:
    """{table: (nb_lignes, empreinte)} pour toutes les tables silver/gold, hors colonnes techniques.

    L'empreinte est une somme de hash ligne à ligne : insensible à l'ordre, mais change dès qu'une
    ligne est ajoutée, supprimée ou modifiée.
    """
    con = get_connection()
    tables = [
        r[0]
        for r in con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name <> 'silver_load_log' "
            "ORDER BY table_name"
        ).fetchall()
    ]
    result = {}
    for table in tables:
        cols = [
            r[0]
            for r in con.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = ? "
                "ORDER BY ordinal_position",
                [table],
            ).fetchall()
            if r[0] not in TECH_COLS
        ]
        col_list = ", ".join(f'"{c}"' for c in cols)
        result[table] = con.execute(
            f"SELECT count(*), coalesce(sum(hash({col_list})), 0) FROM {table}"
        ).fetchone()
    con.close()
    return result


def assert_same(before: dict, after: dict, label: str):
    diff = [t for t in sorted(set(before) | set(after)) if before.get(t) != after.get(t)]
    if diff:
        for t in diff:
            print(f"  {t}: {before.get(t)} -> {after.get(t)}")
        raise AssertionError(f"Pipeline NON idempotent ({label}) : {', '.join(diff)}")


def integrity_report():
    con = get_connection()
    checks = {
        "réservations sans passager connu": """
            SELECT count(*) FROM fact_booking f
            LEFT JOIN dim_passenger p USING (passenger_id) WHERE p.passenger_id IS NULL""",
        "réservations sans vol connu": """
            SELECT count(*) FROM fact_booking f
            LEFT JOIN dim_flight d USING (flight_id) WHERE d.flight_id IS NULL""",
        "réservations sans aéroport connu": """
            SELECT count(*) FROM fact_booking f
            LEFT JOIN dim_airport a USING (airport_id) WHERE a.airport_id IS NULL""",
        "airport_id <> départ du vol": """
            SELECT count(*) FROM fact_booking f
            JOIN dim_flight d USING (flight_id) WHERE f.airport_id <> d.origin_airport_id""",
        "réservations sans version de vol (SCD2)":
            "SELECT count(*) FROM fact_booking WHERE flight_version_key IS NULL",
        "réservations sans amount_eur":
            "SELECT count(*) FROM fact_booking WHERE amount_eur IS NULL",
        "CA agrégé <> CA du fait": """
            SELECT CAST((SELECT sum(amount_eur) FROM fact_booking)
                   <> (SELECT sum(revenue_eur) FROM agg_daily_airline_revenue) AS INTEGER)""",
    }
    print("\nContrôles d'intégrité (0 attendu) :")
    for label, sql in checks.items():
        print(f"  {label:<42} {con.execute(sql).fetchone()[0]}")
    con.close()


def print_counts(fp: dict):
    print("\nComptes par table :")
    for table, (n, _) in fp.items():
        print(f"  {table:<28} {n:>7}")


def run(full_refresh: bool = False, check_idempotence: bool = False):
    if full_refresh and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Entrepôt supprimé, reconstruction complète depuis bronze/.")

    init_dim_currency()
    run_day(init=True)
    print("Init ingérée.")

    for i in range(N_DAYS):
        day = START + timedelta(days=i)
        run_day(day)
        if check_idempotence:
            before = fingerprint()
            run_day(day)
            assert_same(before, fingerprint(), f"rejeu du {day}")
        print(f"{day.isoformat()} ingéré.")

    # Test d'idempotence systématique : rejouer le dernier jour ne doit rien changer.
    last_day = START + timedelta(days=N_DAYS - 1)
    before = fingerprint()
    run_day(last_day)
    after = fingerprint()
    assert_same(before, after, f"rejeu du {last_day}")
    print(f"Rejeu du {last_day} : entrepôt inchangé, pipeline idempotent.")

    print_counts(after)
    integrity_report()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--full-refresh", action="store_true")
    parser.add_argument("--check-idempotence", action="store_true")
    args = parser.parse_args()
    run(full_refresh=args.full_refresh, check_idempotence=args.check_idempotence)
