#! /bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "postgres" --dbname "postgres" <<-EOSQL
    CREATE DATABASE db_intro;
    CREATE USER matej with password 'passwrd';
    ALTER ROLE matej SET client_encoding TO 'utf8';
    ALTER ROLE matej SET default_transaction_isolation TO 'read committed';
    ALTER ROLE matej SET timezone TO 'UTC';
    GRANT ALL PRIVILEGES ON DATABASE db_intro TO matej;
EOSQL 