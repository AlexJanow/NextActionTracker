# Database Setup for Next Action Tracker

This directory contains the database schema, migrations, and seeding utilities for the Next Action Tracker application.

## Structure

- `connection.py` - Database connection pool management
- `migrations.py` - Migration system for schema changes
- `migrations/` - SQL migration files
- `seed.py` - Database seeding with demo data

## Usage

### Running Migrations

```python
from app.database import run_migrations
await run_migrations()
```

### Seeding Database

From the backend directory:

```bash
# Seed with demo data
python seed_db.py

# Clean up all data
python seed_db.py cleanup
```

### Database Connection

```python
from app.database import get_database_connection

async for connection in get_database_connection():
    # Use connection for queries
    result = await connection.fetch("SELECT * FROM opportunities")
```

## Migration Files

Migration files follow the naming convention: `{version}_{description}.sql`

- `001_create_tenants.sql` - Creates tenants table
- `002_create_opportunities.sql` - Creates opportunities table  
- `003_create_indexes.sql` - Creates optimized indexes

## Demo Data

The seed script creates:
- 2 demo tenants
- 8 opportunities with various states (overdue, due today, future)
- Mix of data for testing tenant isolation and dashboard functionality

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (default: `postgresql://postgres:postgres@localhost:5432/nat_dev`)