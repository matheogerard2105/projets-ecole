#!/usr/bin/env bash
set -e

#####################################################

#         OS : Linux (Debian/Ubuntu)
#         PostgreSQL : 15.xpostgres
#         PHP : 8.x, php-pgsql
#         Composer : 2.x
#

#####################################################

#####################################################
#
#       Base de données
#       - Prérequis : un utilisateur PostgreSQL
#       avec droits de création de base et de rôle
#
#####################################################

DB_USER="${USER:-$(whoami)}"
DB_NAME="sos-salle-${DB_USER}"

PG_HOST="localhost"
PG_PORT="5432"
PG_USER="${DB_USER}"

# Base de maintenance universelle pour établir la première connexion :
PG_INIT_DB="template1"
# Identifiants de l'utilisateur d'insertion
APP_USER_WRITER="app_writer"
APP_USER_READER="app_reader"
# Mot de passe temporaire
APP_PASS="postgres"

# 2. Vérification de l'existence de la base
# On ajoute : -d "$PG_INIT_DB"
DB_EXISTS=$(psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_INIT_DB" -tAc \
  "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'")

if [ "$DB_EXISTS" = "1" ]; then
  echo "ℹ️  La base de données \"$DB_NAME\" existe déjà. Aucune action requise."
else
  echo "🚀 Création de la base de données \"$DB_NAME\"..."
  # On se connecte également à template1 pour exécuter le CREATE DATABASE
  createdb "${DB_NAME}"
  echo "✅ Base de données \"$DB_NAME\" créée avec succès."
fi

# Modifications supplémentaires nécessaires pour l'utilisateur chargé d'ajouter
# l'utilisateur à l'installation (DB_USER) de la base de données,
# permissions: createRole, creteDB, ...etc (liste non exhaustive pour le moment)

# 3.1 Ajout de l'utilisateur à la base de données de modification

USER_EXISTS=$(psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_INIT_DB" -tAc \
  "SELECT 1 FROM pg_roles WHERE rolname = '$APP_USER_WRITER'")

if [ "$USER_EXISTS" = "1" ]; then
  echo "ℹ️  L'utilisateur \"$APP_USER_WRITER\" existe déjà."
else
  echo "🚀 Création du rôle \"$APP_USER_WRITER\"..."
  psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_INIT_DB" -c \
    "CREATE ROLE \"$APP_USER_WRITER\" WITH LOGIN PASSWORD '$APP_PASS';"
  echo "✅ Rôle \"$APP_USER_WRITER\" créé avec succès."
fi

# 3.2 Ajout de l'utilisateur à la base de données de lecture

USER_EXISTS=$(psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_INIT_DB" -tAc \
  "SELECT 1 FROM pg_roles WHERE rolname = '$APP_USER_READER'")

if [ "$USER_EXISTS" = "1" ]; then
  echo "ℹ️  L'utilisateur \"$APP_USER_READER\" existe déjà."
else
  echo "🚀 Création du rôle \"$APP_USER_READER\"..."
  psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_INIT_DB" -c \
    "CREATE ROLE \"$APP_USER_READER\" WITH LOGIN PASSWORD '$APP_PASS';"
  echo "✅ Rôle \"$APP_USER_READER\" créé avec succès."
fi

# 4.1 Attribution des privilèges d'écriture à l'utilisateur d'insertion sur la base de données

echo "🔒 Configuration des privilèges pour \"$APP_USER_WRITER\" sur \"$DB_NAME\"..."

psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 <<EOSQL
-- Droit de se connecter et d'accéder au schéma
GRANT CONNECT ON DATABASE "$DB_NAME" TO "$APP_USER_WRITER";
GRANT USAGE ON SCHEMA public TO "$APP_USER_WRITER";

-- Droits d'insertion et de lecture (nécessaire si tu utilises RETURNING id)
GRANT INSERT, DELETE, SELECT, UPDATE ON ALL TABLES IN SCHEMA public TO "$APP_USER_WRITER";

-- Indispensable pour incrémenter les colonnes SERIAL
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "$APP_USER_WRITER";

--
-- Modifications Eventuelles des tables et séquences existantes
--

-- Application automatique sur les futures tables et séquences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT INSERT, DELETE, SELECT, UPDATE ON TABLES TO "$APP_USER_WRITER";

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO "$APP_USER_WRITER";
EOSQL

# 4.2 Attribution des privilèges de lecture à l'utilisateur de consultation sur la base de données

echo "🔒 Configuration des privilèges pour \"$APP_USER_READER\" sur \"$DB_NAME\"..."

psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 <<EOSQL
-- Droit de se connecter et d'accéder au schéma
GRANT CONNECT ON DATABASE "$DB_NAME" TO "$APP_USER_READER";
GRANT USAGE ON SCHEMA public TO "$APP_USER_READER";

-- Droits de lecture
GRANT SELECT ON ALL TABLES IN SCHEMA public TO "$APP_USER_READER";

--
-- Modifications Eventuelles des tables et séquences existantes
--

-- Application automatique sur les futures tables et séquences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO "$APP_USER_READER";

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON SEQUENCES TO "$APP_USER_READER";
EOSQL

echo "✅ Privilèges accordés avec succès."

####################################################
#
#       Compilation & Exécution
#
####################################################

mkdir -p uploads
mkdir -p lib


