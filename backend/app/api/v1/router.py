"""Main API v1 router for Next Action Tracker."""

from fastapi import APIRouter

from app.api.v1.opportunities import router as opportunities_router


# Create the main v1 API router
api_router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
api_router.include_router(opportunities_router)