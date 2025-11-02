"""Demo control endpoints for Next Action Tracker."""

import time
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Request, HTTPException, Depends
import structlog

from app.database.connection import get_database_connection
from app.models.base import BaseResponse
from app.database.seed import clear_data, seed_tenants, seed_opportunities


router = APIRouter(prefix="/demo", tags=["demo"])
logger = structlog.get_logger(__name__)


async def get_tenant_id(request: Request) -> UUID:
    """Extract tenant ID from request state (set by middleware)."""
    if not hasattr(request.state, 'tenant_id'):
        raise HTTPException(status_code=400, detail="Mandanten-ID nicht in der Anfrage gefunden")
    return request.state.tenant_id


@router.post("/reset", response_model=BaseResponse)
async def reset_demo_data(
    request: Request,
    tenant_id: UUID = Depends(get_tenant_id)
):
    """
    Reset demo data to initial seed state for repeatable demonstrations.
    
    This endpoint clears all existing data and recreates the seed data,
    making it perfect for interview demos where you need to reset the state
    multiple times.
    
    Note: This is a demo-only endpoint and should be disabled in production.
    """
    start_time = time.time()
    logger.info("Starting demo data reset", tenant_id=str(tenant_id))
    
    async for connection in get_database_connection():
        try:
            # Start a transaction for atomic reset
            async with connection.transaction():
                # Clear existing data
                await clear_data(connection)
                
                # Seed tenants
                tenants = await seed_tenants(connection)
                
                # Seed opportunities
                opportunities = await seed_opportunities(connection)
                
                total_duration = time.time() - start_time
                
                logger.info(
                    "Demo data reset successfully",
                    tenant_id=str(tenant_id),
                    tenants_created=len(tenants),
                    opportunities_created=len(opportunities),
                    duration=total_duration,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                
                return BaseResponse(
                    success=True,
                    message=f"Demo-Daten erfolgreich zurückgesetzt. {len(opportunities)} Opportunities erstellt."
                )
                
        except Exception as e:
            logger.error(
                "Failed to reset demo data",
                tenant_id=str(tenant_id),
                error=str(e),
                error_type=type(e).__name__,
                duration=time.time() - start_time
            )
            raise HTTPException(
                status_code=500,
                detail="Demo-Daten konnten nicht zurückgesetzt werden"
            )

