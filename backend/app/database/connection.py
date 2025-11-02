"""Database connection management for Next Action Tracker."""

import os
import time
from typing import AsyncGenerator
import asyncpg
from asyncpg import Pool
import structlog
from contextlib import asynccontextmanager

logger = structlog.get_logger(__name__)

# Database connection pool
_pool: Pool = None


async def get_database_pool() -> Pool:
    """Get or create the database connection pool with optimized settings."""
    global _pool
    
    if _pool is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nat_dev")
        
        try:
            _pool = await asyncpg.create_pool(
                database_url,
                min_size=2,  # Increased minimum connections
                max_size=20,  # Increased maximum connections for better concurrency
                max_queries=50000,  # Limit queries per connection
                max_inactive_connection_lifetime=300,  # 5 minutes
                command_timeout=30,  # Reduced timeout for faster failure detection
                server_settings={
                    'application_name': 'next_action_tracker',
                    'jit': 'off',  # Disable JIT for consistent performance
                }
            )
            
            # Log pool statistics
            logger.info(
                "Database connection pool created",
                min_size=2,
                max_size=20,
                database_url=database_url.split('@')[1] if '@' in database_url else 'unknown'
            )
            
        except Exception as e:
            logger.error("Failed to create database pool", error=str(e))
            raise
    
    return _pool


@asynccontextmanager
async def get_database_connection_with_monitoring() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get a database connection with performance monitoring."""
    pool = await get_database_pool()
    start_time = time.time()
    
    try:
        async with pool.acquire() as connection:
            acquire_time = time.time() - start_time
            
            # Log slow connection acquisitions
            if acquire_time > 0.1:  # 100ms threshold
                logger.warning(
                    "Slow database connection acquisition",
                    acquire_time=acquire_time,
                    pool_size=pool.get_size(),
                    pool_idle=pool.get_idle_size()
                )
            
            yield connection
            
    except Exception as e:
        logger.error(
            "Database connection error",
            error=str(e),
            connection_time=time.time() - start_time
        )
        raise


async def get_database_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Get a database connection from the pool (legacy interface)."""
    async with get_database_connection_with_monitoring() as connection:
        yield connection


async def get_pool_stats() -> dict:
    """Get database pool statistics for monitoring."""
    pool = await get_database_pool()
    return {
        "size": pool.get_size(),
        "idle": pool.get_idle_size(),
        "max_size": pool.get_max_size(),
        "min_size": pool.get_min_size()
    }


async def close_database_pool():
    """Close the database connection pool."""
    global _pool
    
    if _pool:
        # Log final pool statistics
        stats = {
            "size": _pool.get_size(),
            "idle": _pool.get_idle_size()
        }
        
        await _pool.close()
        _pool = None
        
        logger.info("Database connection pool closed", final_stats=stats)