from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import structlog
from uuid import UUID
from contextlib import asynccontextmanager

from app.database.connection import get_database_pool, close_database_pool
from app.core.middleware import TenantValidationMiddleware
from app.core.logging import setup_logging
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    setup_logging()
    logger = structlog.get_logger()
    logger.info("Starting Next Action Tracker API")
    
    # Initialize database pool (non-blocking - allow app to start even if DB fails)
    try:
        await get_database_pool()
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error("Failed to initialize database pool", error=str(e))
        logger.warning("Application will start but database operations will fail")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Next Action Tracker API")
    try:
        await close_database_pool()
        logger.info("Database connection pool closed")
    except Exception as e:
        logger.error("Error closing database pool", error=str(e))


app = FastAPI(
    title="Next Action Tracker API",
    description="API for managing sales opportunities and next actions",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant validation middleware
app.add_middleware(TenantValidationMiddleware)

# Include API routes
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with structured logging."""
    logger = structlog.get_logger()
    logger.warning(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "details": {}
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unhandled exceptions."""
    logger = structlog.get_logger()
    logger.error(
        "Unhandled exception occurred",
        exception=str(exc),
        exception_type=type(exc).__name__,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "details": {}
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker health checks"""
    return {"status": "healthy", "service": "next-action-tracker-api"}


@app.get("/metrics")
async def get_metrics():
    """Get application metrics for monitoring"""
    try:
        from app.database.connection import get_pool_stats
        pool_stats = await get_pool_stats()
        return {
            "status": "healthy",
            "database": {
                "pool_size": pool_stats["size"],
                "pool_idle": pool_stats["idle"],
                "pool_max": pool_stats["max_size"],
                "pool_min": pool_stats["min_size"]
            },
            "service": "next-action-tracker-api",
            "version": "1.0.0"
        }
    except Exception as e:
        logger = structlog.get_logger()
        logger.error("Metrics endpoint error", error=str(e))
        return {
            "status": "degraded",
            "error": str(e),
            "service": "next-action-tracker-api",
            "version": "1.0.0"
        }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Next Action Tracker API", "version": "1.0.0"}