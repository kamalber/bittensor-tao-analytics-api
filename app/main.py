import logging
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.tao_dividends import router as tao_router
from app.db import init_db
from app.services.cache_service import cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app
    Initializes database and Redis cache
    """
    # Skip DB initialization during testing
    if "PYTEST_CURRENT_TEST" not in os.environ:
        # Initialize database
        logging.info("Initializing database")
        await init_db()

    # Initialize Redis
    logging.info("Initializing Redis cache")
    await cache.init_redis()

    yield

    # Cleanup
    logging.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Bittensor TAO Dividends API",
    description="API for querying TAO dividends from Bittensor blockchain",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(tao_router, prefix="/api/v1", tags=["tao"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Bittensor TAO Dividends API",
        "documentation": "/docs",
    }

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )