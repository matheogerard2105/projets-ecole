-- F16 : désactivation d'une formation sans la supprimer.
-- À exécuter une fois sur une base existante :
--   psql -d sos-salle-<user> -f sql/migrations/001_groupe_actif.sql
ALTER TABLE GROUPE ADD COLUMN IF NOT EXISTS ACTIF BOOLEAN NOT NULL DEFAULT TRUE;
