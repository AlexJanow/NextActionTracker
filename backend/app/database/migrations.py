"""Database migration system for Next Action Tracker."""

import asyncio
import logging
from pathlib import Path
from typing import List
import asyncpg
from .connection import get_database_connection

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


class Migration:
    """Represents a database migration."""
    
    def __init__(self, version: str, name: str, sql: str):
        self.version = version
        self.name = name
        self.sql = sql
    
    def __str__(self):
        return f"Migration {self.version}: {self.name}"


async def create_migrations_table(connection: asyncpg.Connection):
    """Create the migrations tracking table if it doesn't exist."""
    await connection.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)


async def get_applied_migrations(connection: asyncpg.Connection) -> List[str]:
    """Get list of already applied migration versions."""
    await create_migrations_table(connection)
    
    rows = await connection.fetch("SELECT version FROM schema_migrations ORDER BY version")
    return [row['version'] for row in rows]


async def apply_migration(connection: asyncpg.Connection, migration: Migration):
    """Apply a single migration."""
    logger.info(f"Applying {migration}")
    
    async with connection.transaction():
        # Execute the migration SQL
        await connection.execute(migration.sql)
        
        # Record the migration as applied
        await connection.execute(
            "INSERT INTO schema_migrations (version, name) VALUES ($1, $2)",
            migration.version, migration.name
        )
    
    logger.info(f"Successfully applied {migration}")


def load_migrations() -> List[Migration]:
    """Load all migration files from the migrations directory."""
    migrations = []
    
    if not MIGRATIONS_DIR.exists():
        logger.warning(f"Migrations directory {MIGRATIONS_DIR} does not exist")
        return migrations
    
    for migration_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
        # Parse filename: 001_create_tenants.sql -> version=001, name=create_tenants
        filename = migration_file.stem
        parts = filename.split("_", 1)
        
        if len(parts) != 2:
            logger.warning(f"Skipping migration file with invalid name: {migration_file}")
            continue
        
        version, name = parts
        sql = migration_file.read_text()
        
        migrations.append(Migration(version, name, sql))
    
    return migrations


async def run_migrations():
    """Run all pending migrations."""
    logger.info("Starting database migrations")
    
    async for connection in get_database_connection():
        applied_versions = await get_applied_migrations(connection)
        all_migrations = load_migrations()
        
        pending_migrations = [
            migration for migration in all_migrations
            if migration.version not in applied_versions
        ]
        
        if not pending_migrations:
            logger.info("No pending migrations")
            return
        
        logger.info(f"Found {len(pending_migrations)} pending migrations")
        
        for migration in pending_migrations:
            await apply_migration(connection, migration)
        
        logger.info("All migrations completed successfully")


if __name__ == "__main__":
    asyncio.run(run_migrations())