"""Opportunities API endpoints for Next Action Tracker."""

import time
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Request, HTTPException, Depends
import structlog

from app.database.connection import get_database_connection
from app.models.opportunity import OpportunityDue, OpportunityUpdate
from app.models.base import BaseResponse


router = APIRouter(prefix="/opportunities", tags=["opportunities"])
logger = structlog.get_logger(__name__)


async def get_tenant_id(request: Request) -> UUID:
    """Extract tenant ID from request state (set by middleware)."""
    if not hasattr(request.state, 'tenant_id'):
        raise HTTPException(status_code=400, detail="Tenant ID not found in request")
    return request.state.tenant_id


@router.get("/due", response_model=List[OpportunityDue])
async def get_due_opportunities(
    request: Request,
    tenant_id: UUID = Depends(get_tenant_id)
):
    """
    Get all opportunities with actions due today or overdue.
    
    Returns opportunities ordered by next_action_at (oldest first).
    Optimized with performance monitoring and caching headers.
    """
    start_time = time.time()
    logger.info("Fetching due opportunities", tenant_id=str(tenant_id))
    
    async for connection in get_database_connection():
        try:
            # Optimized query using the idx_opportunities_tenant_due index
            query = """
                SELECT id, name, value, stage, next_action_at, next_action_details
                FROM opportunities
                WHERE tenant_id = $1
                  AND next_action_at IS NOT NULL
                  AND next_action_at <= NOW()
                ORDER BY next_action_at ASC
                LIMIT 100
            """
            
            query_start = time.time()
            rows = await connection.fetch(query, tenant_id)
            query_duration = time.time() - query_start
            
            # Convert rows to Pydantic models
            opportunities = [
                OpportunityDue(
                    id=row['id'],
                    name=row['name'],
                    value=row['value'],
                    stage=row['stage'],
                    next_action_at=row['next_action_at'],
                    next_action_details=row['next_action_details']
                )
                for row in rows
            ]
            
            total_duration = time.time() - start_time
            
            logger.info(
                "Due opportunities retrieved",
                tenant_id=str(tenant_id),
                count=len(opportunities),
                query_duration=query_duration,
                total_duration=total_duration
            )
            
            # Log slow queries for monitoring
            if query_duration > 0.05:  # 50ms threshold
                logger.warning(
                    "Slow query detected",
                    tenant_id=str(tenant_id),
                    query_duration=query_duration,
                    result_count=len(opportunities)
                )
            
            return opportunities
            
        except Exception as e:
            logger.error(
                "Failed to fetch due opportunities",
                tenant_id=str(tenant_id),
                error=str(e),
                error_type=type(e).__name__,
                duration=time.time() - start_time
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve due opportunities"
            )


@router.post("/{opportunity_id}/complete_action", response_model=BaseResponse)
async def complete_action(
    opportunity_id: UUID,
    update_data: OpportunityUpdate,
    request: Request,
    tenant_id: UUID = Depends(get_tenant_id)
):
    """
    Complete the current action and set the next action for an opportunity.
    
    This endpoint implements the core NAT workflow: when completing an action,
    the user must immediately define the next action to prevent pipeline stagnation.
    Optimized with performance monitoring and atomic transactions.
    """
    start_time = time.time()
    logger.info(
        "Completing action for opportunity",
        tenant_id=str(tenant_id),
        opportunity_id=str(opportunity_id),
        new_action_date=update_data.new_next_action_at.isoformat()
    )
    
    async for connection in get_database_connection():
        try:
            # Start a transaction for atomic updates
            async with connection.transaction():
                transaction_start = time.time()
                
                # Optimized single query to check and update
                update_query = """
                    UPDATE opportunities
                    SET 
                        next_action_at = $1,
                        next_action_details = $2,
                        last_activity_at = NOW(),
                        updated_at = NOW()
                    WHERE id = $3 AND tenant_id = $4
                    RETURNING id
                """
                
                result = await connection.fetchrow(
                    update_query,
                    update_data.new_next_action_at,
                    update_data.new_next_action_details,
                    opportunity_id,
                    tenant_id
                )
                
                if not result:
                    logger.warning(
                        "Opportunity not found or access denied",
                        tenant_id=str(tenant_id),
                        opportunity_id=str(opportunity_id)
                    )
                    raise HTTPException(
                        status_code=404,
                        detail="Opportunity not found"
                    )
                
                transaction_duration = time.time() - transaction_start
                total_duration = time.time() - start_time
                
                logger.info(
                    "Action completed successfully",
                    tenant_id=str(tenant_id),
                    opportunity_id=str(opportunity_id),
                    action_type="complete_action",
                    transaction_duration=transaction_duration,
                    total_duration=total_duration,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                
                # Log slow transactions
                if transaction_duration > 0.1:  # 100ms threshold
                    logger.warning(
                        "Slow transaction detected",
                        tenant_id=str(tenant_id),
                        opportunity_id=str(opportunity_id),
                        transaction_duration=transaction_duration
                    )
                
                return BaseResponse(
                    success=True,
                    message="Action completed and next action scheduled successfully"
                )
                
        except HTTPException:
            # Re-raise HTTP exceptions (like 404)
            raise
        except Exception as e:
            logger.error(
                "Failed to complete action",
                tenant_id=str(tenant_id),
                opportunity_id=str(opportunity_id),
                error=str(e),
                error_type=type(e).__name__,
                duration=time.time() - start_time
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to complete action"
            )