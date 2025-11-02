#!/bin/bash
# PostgreSQL startup script for Docker container

set -e

# Add PostgreSQL to PATH
export PATH="/usr/lib/postgresql/15/bin:$PATH"

PGDATA="${PGDATA:-/var/lib/postgresql/data/pgdata}"
PGUSER="${POSTGRES_USER:-nat_user}"
PGPASSWORD="${POSTGRES_PASSWORD:-nat_password}"
PGDB="${POSTGRES_DB:-nat_dev}"

# Initialize PostgreSQL if not already done
if [ ! -f "$PGDATA/PG_VERSION" ]; then
    echo "Initializing PostgreSQL database in $PGDATA..."
    /usr/lib/postgresql/15/bin/initdb -D "$PGDATA"
    
    # Start PostgreSQL temporarily to create user and database
    echo "Starting PostgreSQL for initialization..."
    /usr/lib/postgresql/15/bin/pg_ctl -D "$PGDATA" -l /var/log/postgresql.log start
    
    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if /usr/lib/postgresql/15/bin/pg_isready -q; then
            break
        fi
        sleep 1
    done
    
    # Create user and database
    echo "Creating user $PGUSER and database $PGDB..."
    /usr/lib/postgresql/15/bin/psql -v ON_ERROR_STOP=1 <<-EOSQL
        CREATE USER $PGUSER WITH PASSWORD '$PGPASSWORD';
        CREATE DATABASE $PGDB OWNER $PGUSER;
        GRANT ALL PRIVILEGES ON DATABASE $PGDB TO $PGUSER;
EOSQL
    
    # Run init script
    if [ -f /docker-entrypoint-initdb.d/init.sql ]; then
        echo "Running init.sql..."
        /usr/lib/postgresql/15/bin/psql -d "$PGDB" -f /docker-entrypoint-initdb.d/init.sql
    fi
    
    # Stop temporary PostgreSQL
    echo "Stopping temporary PostgreSQL instance..."
    /usr/lib/postgresql/15/bin/pg_ctl -D "$PGDATA" stop
fi

# Start PostgreSQL
echo "Starting PostgreSQL server..."
exec /usr/lib/postgresql/15/bin/postgres -D "$PGDATA"

