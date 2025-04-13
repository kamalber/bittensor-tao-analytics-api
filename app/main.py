import logging
from fastapi import FastAPI

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create FastAPI app
app = FastAPI(
    title="Bittensor TAO Dividends API",
    description="API for querying TAO dividends from Bittensor blockchain",
    version="0.1.0",
)

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


