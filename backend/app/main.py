"""
FastAPI Main Application
Entry point for the KYC/AML Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

# Add parent directory to path to import core modules
sys.path.append('..')

from backend.app.api import routes
from backend.app.middleware.cors import get_cors_config

# Initialize FastAPI app
app = FastAPI(
    title="KYC/AML Multi-Agent System API",
    description="Intelligent KYC/AML compliance system with real-time agent reasoning",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
cors_config = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
)

# Include routers
app.include_router(routes.router, prefix="/api")

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
    level="INFO"
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 KYC/AML Backend starting up...")
    logger.info("📡 SSE streaming enabled")
    logger.info("✅ Backend ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 KYC/AML Backend shutting down...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KYC/AML Multi-Agent System API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "kyc-aml-backend",
        "agents": ["extraction", "verification", "reasoning", "assessment", "decision"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )