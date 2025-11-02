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
    /usr/lib/postgresql/15/bin/pg_ctl -D "$PGDATA" -l /var/log/postgresql.log -w start
    
    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if /usr/lib/postgresql/15/bin/pg_isready -q; then
            break
        fi
        sleep 1
    done
    
    # Create user if it doesn't exist
    echo "Ensuring user $PGUSER exists..."
    /usr/lib/postgresql/15/bin/psql -v ON_ERROR_STOP=1 -U postgres -d postgres <<-EOSQL || true
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$PGUSER') THEN
                CREATE USER $PGUSER WITH PASSWORD '$PGPASSWORD';
            ELSE
                ALTER USER $PGUSER WITH PASSWORD '$PGPASSWORD';
            END IF;
        END
        \$\$;
EOSQL
    
    # Create database if it doesn't exist
    echo "Ensuring database $PGDB exists..."
    /usr/lib/postgresql/15/bin/psql -v ON_ERROR_STOP=1 -U postgres -d postgres <<-EOSQL || true
        SELECT 'CREATE DATABASE $PGDB OWNER $PGUSER'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$PGDB')\\gexec
EOSQL
    
    # Grant privileges
    /usr/lib/postgresql/15/bin/psql -v ON_ERROR_STOP=1 -U postgres -d "$PGDB" <<-EOSQL || true
        GRANT ALL PRIVILEGES ON DATABASE $PGDB TO $PGUSER;
EOSQL
    
    # Run init script if it exists and database is empty
    if [ -f /docker-entrypoint-initdb.d/init.sql ]; then
        echo "Running init.sql..."
        /usr/lib/postgresql/15/bin/psql -d "$PGDB" -f /docker-entrypoint-initdb.d/init.sql || true
    fi
    
    # Stop temporary PostgreSQL
    echo "Stopping temporary PostgreSQL instance..."
    /usr/lib/postgresql/15/bin/pg_ctl -D "$PGDATA" -w stop
else
    # PostgreSQL already initialized - ensure user and database exist
    echo "PostgreSQL already initialized, ensuring user and database exist..."
    
    # Start PostgreSQL temporarily to check/create user and database
    /usr/lib/postgresql/15/bin/pg_ctl -D "$PGDATA" -l /var/log/postgresql.log -w start
    
    # Wait for PostgreSQL to be ready
    for i in {1..30}; do
        if /usr/lib/postgresql/15/bin/pg_isready -q; then
            break
        fi
        sleep 1
    done
    
    # Create user if it doesn't exist
    echo "Checking if user $PGUSER exists..."
    /usr/lib/postgresql/15/bin/psql -v ON_ERROR_STOP=1 -U postgres -d postgres <<-EOSQL || true
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$PGUSER') THEN
                CREATE USER $PGUSER WITH PASSWORD '$PGPASSWORD';
                RAISE NOTICE 'User $PGUSER created';
            ELSE
                ALTER USER $PGUSER WITH PASSWORD '$PGPASSWORD';
                RAISE NOTICE 'User $PGUSER already exists, password updated';
            END IF;
        END
        \$\$;
EOSQL
    
    # Create database if it doesn't exist
    echo "Checking if database $PGDB exists..."
    /usr/lib/postgresql/15/bin/psql -v ON_ERROR_STOP=1 -U postgres -d postgres <<-EOSQL || true
        SELECT 'CREATE DATABASE $PGDB OWNER $PGUSER'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$PGDB')\\gexec
EOSQL
    
    # Grant privileges
    /usr/lib/postgresql/15/bin/psql -v ON_ERROR_STOP=1 -U postgres -d "$PGDB" <<-EOSQL || true
        GRANT ALL PRIVILEGES ON DATABASE $PGDB TO $PGUSER;
EOSQL
    
    # Stop temporary PostgreSQL
    /usr/lib/postgresql/15/bin/pg_ctl -D "$PGDATA" -w stop
fi

# Start PostgreSQL
echo "Starting PostgreSQL server..."
exec /usr/lib/postgresql/15/bin/postgres -D "$PGDATA"

