"""Middleware for Next Action Tracker API."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from uuid import UUID
import structlog


class TenantValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate tenant ID in request headers."""
    
    # Paths that don't require tenant validation
    EXEMPT_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json"}
    
    async def dispatch(self, request: Request, call_next):
        """Process request and validate tenant ID for protected endpoints."""
        logger = structlog.get_logger()
        
        # Skip validation for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Skip validation for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Extract tenant ID from header
        tenant_id_header = request.headers.get("X-Tenant-ID")
        
        if not tenant_id_header:
            logger.warning(
                "Missing tenant ID header",
                path=request.url.path,
                method=request.method
            )
            raise HTTPException(
                status_code=400,
                detail="X-Tenant-ID header is required"
            )
        
        # Validate tenant ID format
        try:
            tenant_id = UUID(tenant_id_header)
        except ValueError:
            logger.warning(
                "Invalid tenant ID format",
                tenant_id=tenant_id_header,
                path=request.url.path,
                method=request.method
            )
            raise HTTPException(
                status_code=400,
                detail="X-Tenant-ID must be a valid UUID"
            )
        
        # Add tenant ID to request state for use in route handlers
        request.state.tenant_id = tenant_id
        
        # Log request with tenant context
        logger.info(
            "Processing request",
            tenant_id=str(tenant_id),
            path=request.url.path,
            method=request.method
        )
        
        response = await call_next(request)
        return response