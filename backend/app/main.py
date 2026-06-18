"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api import health, import_api, indicator_api, audit_api, admin_division_api, auth_api
from app.api import village_detail_api, cert_api, snapshot_api, quality_api
# Import all models to register them with Base.metadata
from app.models import *  # noqa: F401, F403

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="农经权二轮延包数据监控可视化平台后端服务",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(import_api.router, prefix="/api", tags=["import"])
app.include_router(indicator_api.router, prefix="/api", tags=["indicators"])
app.include_router(audit_api.router, prefix="/api", tags=["audit"])
app.include_router(admin_division_api.router, prefix="/api", tags=["admin-divisions"])
app.include_router(auth_api.router, prefix="/api", tags=["auth"])
# P1 增强功能路由
app.include_router(village_detail_api.router, prefix="/api", tags=["village-detail"])
app.include_router(cert_api.router, prefix="/api", tags=["cert-progress"])
app.include_router(snapshot_api.router, prefix="/api", tags=["snapshot"])
app.include_router(quality_api.router, prefix="/api", tags=["quality"])


@app.on_event("startup")
async def startup_event():
    """
    Application startup: create database tables if they don't exist.
    For production, use Alembic migrations instead.
    """
    # Create tables (useful for SQLite development)
    # In production, use: alembic upgrade head
    Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown cleanup.
    """
    pass


@app.get("/")
async def root():
    """Root endpoint redirecting to API documentation."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "version": settings.APP_VERSION,
    }