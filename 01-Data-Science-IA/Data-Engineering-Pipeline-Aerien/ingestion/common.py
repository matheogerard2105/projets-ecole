"""
Utilitaires partagés par les scripts d'ingestion : téléchargement bronze (`fetch_csv`),
connexion à l'entrepôt (`get_connection`) et journal de chargement silver (`silver_load_log`).
"""
import os
import urllib.request
from datetime import date

import duckdb
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRONZE_DIR = os.path.join(BASE_DIR, "bronze")
DB_PATH = os.path.join(BASE_DIR, "warehouse.duckdb")
RAW_BASE = "https://raw.githubusercontent.com/kevinl75/tp-polytech-dataset/main"

# Date "logique" de l'état init/ : la veille du premier jour simulé.
INIT_DATE = date(2025, 8, 31)
# Début de validité des versions SCD2 issues de init/ : on ne connaît rien d'antérieur à cet
# état, on le considère donc valable "depuis toujours" (les réservations d'août s'y rattachent).
HISTORY_START = date(1900, 1, 1)


def fetch_csv(subdir: str, filename: str) -> pd.DataFrame:
    """Renvoie le contenu de <subdir>/<filename> sous forme de DataFrame pandas.

    Le fichier est d'abord téléchargé octet pour octet vers BRONZE_DIR/<subdir>/<filename> s'il
    n'y est pas déjà (bronze = copie brute, sans transformation), puis toujours relu depuis le
    disque : le bronze est la seule source de vérité des couches suivantes, et rejouer
    l'historique ne retélécharge rien.
    """
    local_path = os.path.join(BRONZE_DIR, subdir, filename)
    if not os.path.exists(local_path):
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        url = f"{RAW_BASE}/{subdir}/{filename}"
        # Écriture dans un fichier temporaire puis renommage atomique : un téléchargement
        # interrompu ne laisse jamais un fichier bronze tronqué qui serait pris pour valide.
        tmp_path = local_path + ".part"
        with urllib.request.urlopen(url, timeout=60) as resp, open(tmp_path, "wb") as out:
            out.write(resp.read())
        os.replace(tmp_path, local_path)

    # dtype=str + keep_default_na=False : on relit les valeurs telles quelles (pas de "NA"
    # transformé en NaN, pas d'identifiant réinterprété en nombre). Le typage se fait en silver.
    return pd.read_csv(local_path, dtype=str, keep_default_na=False)


def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DB_PATH)


def snapshot_date(day: date = None, init: bool = False) -> date:
    if init:
        return INIT_DATE
    assert day is not None, "day est obligatoire hors init"
    return day


def create_load_log(con):
    """Journal des snapshots chargés en silver, une ligne par (entité, date de snapshot)."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver_load_log (
            entity VARCHAR,
            snapshot_date DATE,
            row_count INTEGER,
            insert_timestamp TIMESTAMP,
            update_timestamp TIMESTAMP,
            PRIMARY KEY (entity, snapshot_date)
        )
    """)


def last_loaded_date(con, entity: str):
    create_load_log(con)
    return con.execute(
        "SELECT max(snapshot_date) FROM silver_load_log WHERE entity = ?", [entity]
    ).fetchone()[0]


def is_stale_snapshot(con, entity: str, day: date) -> bool:
    """Vrai si un snapshot PLUS RÉCENT a déjà été chargé pour cette entité.

    Les fichiers airports/flights/passengers sont des extraits complets : recharger le 5
    septembre après le 30 ramènerait l'entrepôt dans l'état du 5 (vols réactivés, historique SCD2
    faussé). On ignore donc un snapshot plus ancien que le dernier chargé ; recharger le MÊME
    jour reste possible et ne change rien (idempotence). Pour tout rejouer depuis zéro :
    `python run_month.py --full-refresh` (reconstruit l'entrepôt depuis bronze/).
    """
    last = last_loaded_date(con, entity)
    if last is not None and day < last:
        print(f"  [{entity}] snapshot {day} ignoré : {last} est déjà chargé")
        return True
    return False


def log_load(con, entity: str, day: date, row_count: int):
    create_load_log(con)
    con.execute(
        """
        INSERT INTO silver_load_log VALUES (?, ?, ?, now(), now())
        ON CONFLICT (entity, snapshot_date)
        DO UPDATE SET row_count = excluded.row_count, update_timestamp = now()
        """,
        [entity, day, row_count],
    )


def upsert_snapshot(con, table: str, key: str, cols: list, snap_date: date):
    """Upsert d'un extrait complet (table temporaire `snapshot`) + soft delete des clés absentes.

    Contrairement au modèle d'`ingest_airports.py`, la mise à jour n'a lieu que si une valeur a
    réellement changé : update_timestamp signale donc un vrai changement, et rejouer un jour ne
    retouche aucune ligne.
    """
    col_list = ", ".join(cols)
    set_clause = ", ".join(f"{c} = excluded.{c}" for c in cols)
    old_row = ", ".join(f"{table}.{c}" for c in cols)
    new_row = ", ".join(f"excluded.{c}" for c in cols)
    con.execute(f"""
        INSERT INTO {table} ({key}, {col_list}, is_active, deleted_date, insert_timestamp, update_timestamp)
        SELECT {key}, {col_list}, true, NULL, now(), now()
        FROM snapshot
        ON CONFLICT ({key}) DO UPDATE
        SET {set_clause}, is_active = true, deleted_date = NULL, update_timestamp = now()
        WHERE ({old_row}, {table}.is_active) IS DISTINCT FROM ({new_row}, true)
    """)
    # Clés disparues de l'extrait : désactivation, jamais de suppression physique.
    con.execute(
        f"""
        UPDATE {table} SET is_active = false, deleted_date = ?, update_timestamp = now()
        WHERE is_active = true AND {key} NOT IN (SELECT {key} FROM snapshot)
        """,
        [snap_date],
    )


def scd2_snapshot(con, table: str, key: str, cols: list, snap_date: date):
    """Historisation SCD2 d'un extrait complet (table temporaire `snapshot`).

    Une version = une ligne avec [valid_from, valid_to[ ; valid_to NULL = version courante.
    1. on ferme les versions courantes dont la clé a disparu ou dont une valeur a changé ;
    2. on ouvre une version pour chaque clé de l'extrait qui n'a plus de version courante.
    Rejouer le même jour ne ferme ni n'ouvre rien : les versions courantes correspondent déjà.
    """
    open_date = HISTORY_START if snap_date == INIT_DATE else snap_date
    col_list = ", ".join(cols)
    hist_row = ", ".join(f"h.{c}" for c in cols)
    snap_row = ", ".join(f"s.{c}" for c in cols)
    con.execute(
        f"""
        UPDATE {table} AS h SET valid_to = ?, is_current = false, update_timestamp = now()
        WHERE h.is_current AND NOT EXISTS (
            SELECT 1 FROM snapshot s
            WHERE s.{key} = h.{key} AND ({snap_row}) IS NOT DISTINCT FROM ({hist_row})
        )
        """,
        [snap_date],
    )
    con.execute(
        f"""
        INSERT INTO {table} ({key}, {col_list}, valid_from, valid_to, is_current, insert_timestamp, update_timestamp)
        SELECT {key}, {col_list}, ?, NULL, true, now(), now()
        FROM snapshot s
        WHERE NOT EXISTS (SELECT 1 FROM {table} h WHERE h.is_current AND h.{key} = s.{key})
        """,
        [open_date],
    )
