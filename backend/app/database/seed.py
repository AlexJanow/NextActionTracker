"""Database seeding script for Next Action Tracker development."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from typing import List, Dict, Any
import asyncpg
from .connection import get_database_connection

logger = logging.getLogger(__name__)

# Demo tenant IDs for consistent testing
DEMO_TENANT_ID = UUID('550e8400-e29b-41d4-a716-446655440000')
SECOND_TENANT_ID = UUID('550e8400-e29b-41d4-a716-446655440001')


async def clear_data(connection: asyncpg.Connection):
    """Clear all existing data for fresh seeding."""
    logger.info("Clearing existing data...")
    
    await connection.execute("DELETE FROM opportunities")
    await connection.execute("DELETE FROM tenants")
    
    logger.info("Data cleared successfully")


async def seed_tenants(connection: asyncpg.Connection) -> List[Dict[str, Any]]:
    """Seed demo tenants."""
    logger.info("Seeding tenants...")
    
    tenants = [
        {
            'id': DEMO_TENANT_ID,
            'name': 'Demo Company',
        },
        {
            'id': SECOND_TENANT_ID,
            'name': 'Test Organization',
        }
    ]
    
    for tenant in tenants:
        await connection.execute(
            "INSERT INTO tenants (id, name) VALUES ($1, $2)",
            tenant['id'], tenant['name']
        )
    
    logger.info(f"Seeded {len(tenants)} tenants")
    return tenants


async def seed_opportunities(connection: asyncpg.Connection) -> List[Dict[str, Any]]:
    """Seed demo opportunities with varied urgency levels for compelling demo."""
    logger.info("Seeding opportunities...")
    
    now = datetime.now(timezone.utc)
    
    opportunities = [
        # High urgency: 7 days overdue (red indicator)
        {
            'id': uuid4(),
            'tenant_id': DEMO_TENANT_ID,
            'name': 'Enterprise Deal - Acme Corp',
            'value': 50000,
            'stage': 'Proposal',
            'next_action_at': now - timedelta(days=7),
            'next_action_details': 'Follow up on proposal feedback',
            'last_activity_at': now - timedelta(days=8),
        },
        
        # Medium urgency: 2 days overdue (yellow indicator)
        {
            'id': uuid4(),
            'tenant_id': DEMO_TENANT_ID,
            'name': 'Mid-Market - TechStart Inc',
            'value': 25000,
            'stage': 'Negotiation',
            'next_action_at': now - timedelta(days=2),
            'next_action_details': 'Send revised pricing',
            'last_activity_at': now - timedelta(days=3),
        },
        
        # Low urgency: Due today (blue indicator)
        {
            'id': uuid4(),
            'tenant_id': DEMO_TENANT_ID,
            'name': 'SMB Deal - Local Business',
            'value': 5000,
            'stage': 'Discovery',
            'next_action_at': now,
            'next_action_details': 'Schedule demo call',
            'last_activity_at': now - timedelta(hours=6),
        },
        
        # For demo completion workflow: 1 day overdue
        {
            'id': uuid4(),
            'tenant_id': DEMO_TENANT_ID,
            'name': 'Renewal - Existing Customer',
            'value': 15000,
            'stage': 'Closed Won',
            'next_action_at': now - timedelta(days=1),
            'next_action_details': 'Send renewal contract',
            'last_activity_at': now - timedelta(days=2),
        },
        
        # Future action: 3 days in future (should NOT appear on dashboard)
        {
            'id': uuid4(),
            'tenant_id': DEMO_TENANT_ID,
            'name': 'Future Opportunity',
            'value': 30000,
            'stage': 'Qualification',
            'next_action_at': now + timedelta(days=3),
            'next_action_details': 'Initial discovery call',
            'last_activity_at': now - timedelta(hours=2),
        },
        
        # Additional opportunity for variety
        {
            'id': uuid4(),
            'tenant_id': DEMO_TENANT_ID,
            'name': 'Healthcare Solutions Inc',
            'value': 120000,
            'stage': 'Negotiation',
            'next_action_at': now - timedelta(days=5),
            'next_action_details': 'Review contract terms and prepare counter-proposal',
            'last_activity_at': now - timedelta(days=6),
        },
        
        # Second tenant data (for testing tenant isolation)
        {
            'id': uuid4(),
            'tenant_id': SECOND_TENANT_ID,
            'name': 'Different Tenant Deal',
            'value': 40000,
            'stage': 'Discovery',
            'next_action_at': now - timedelta(hours=2),
            'next_action_details': 'This should not appear for Demo Company tenant',
            'last_activity_at': now - timedelta(hours=3),
        },
    ]
    
    for opp in opportunities:
        await connection.execute("""
            INSERT INTO opportunities (
                id, tenant_id, name, value, stage, 
                next_action_at, next_action_details, last_activity_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, 
            opp['id'], opp['tenant_id'], opp['name'], opp['value'], 
            opp['stage'], opp['next_action_at'], opp['next_action_details'], 
            opp['last_activity_at']
        )
    
    logger.info(f"Seeded {len(opportunities)} opportunities")
    return opportunities


async def verify_seed_data(connection: asyncpg.Connection):
    """Verify that seed data was created correctly."""
    logger.info("Verifying seed data...")
    
    # Check tenant count
    tenant_count = await connection.fetchval("SELECT COUNT(*) FROM tenants")
    logger.info(f"Total tenants: {tenant_count}")
    
    # Check opportunity count by tenant
    demo_opp_count = await connection.fetchval(
        "SELECT COUNT(*) FROM opportunities WHERE tenant_id = $1", 
        DEMO_TENANT_ID
    )
    logger.info(f"Demo Company opportunities: {demo_opp_count}")
    
    # Check due actions for demo tenant
    due_count = await connection.fetchval("""
        SELECT COUNT(*) FROM opportunities 
        WHERE tenant_id = $1 
        AND next_action_at IS NOT NULL 
        AND next_action_at <= NOW()
    """, DEMO_TENANT_ID)
    logger.info(f"Due actions for Demo Company: {due_count}")
    
    # Check overdue actions
    overdue_count = await connection.fetchval("""
        SELECT COUNT(*) FROM opportunities 
        WHERE tenant_id = $1 
        AND next_action_at IS NOT NULL 
        AND next_action_at < NOW() - INTERVAL '1 hour'
    """, DEMO_TENANT_ID)
    logger.info(f"Overdue actions for Demo Company: {overdue_count}")


async def seed_database():
    """Main seeding function."""
    logger.info("Starting database seeding...")
    
    async for connection in get_database_connection():
        try:
            # Clear existing data
            await clear_data(connection)
            
            # Seed new data
            await seed_tenants(connection)
            await seed_opportunities(connection)
            
            # Verify the seeded data
            await verify_seed_data(connection)
            
            logger.info("Database seeding completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during database seeding: {e}")
            raise


async def cleanup_database():
    """Utility function to clean up all data."""
    logger.info("Cleaning up database...")
    
    async for connection in get_database_connection():
        await clear_data(connection)
        logger.info("Database cleanup completed")


if __name__ == "__main__":
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        asyncio.run(cleanup_database())
    else:
        asyncio.run(seed_database())