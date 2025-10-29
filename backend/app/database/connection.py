"""Database connection management for Next Action Tracker."""

import os
from typing import AsyncGenerator
import asyncpg
from asyncpg import Pool
import logging

logger = logging.getLogger(__name__)

# Database connection pool
_pool: Pool = None


async def get_database_pool() -> Pool:
    """Get or create the database connection pool."""
    global _pool
    
    if _pool is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nat_dev")
        
        try:
            _pool = await asyncpg.create_pool(
                database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    return _pool


async def get_database_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get a database connection from the pool."""
    pool = await get_database_pool()
    
    async with pool.acquire() as connection:
        yield connection


async def close_database_pool():
    """Close the database connection pool."""
    global _pool
    
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")