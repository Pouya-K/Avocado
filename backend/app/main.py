"""
FastAPI application entry point.
Initializes the app, configures middleware, and includes routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.v1 import check

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS for browser extension
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(
        check.router,
        prefix=settings.API_V1_PREFIX,
        tags=["fact-check"]
    )
    
    @app.on_event("startup")
    async def startup_event():
        """Log startup information."""
        logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
        logger.info(f"Debug mode: {settings.DEBUG}")
        logger.info(f"API Documentation: http://localhost:8000/docs")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        logger.info("Shutting down application")
    
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint."""
        return {
            "message": "Avocado TikTok Fact Checker API",
            "version": settings.VERSION,
            "docs": "/docs"
        }
    
    return app


# Create the app instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
