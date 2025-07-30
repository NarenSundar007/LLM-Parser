from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import Dict, Any

# Initialize FastAPI app
app = FastAPI(
    title="LLM-Powered Intelligent Query-Retrieval System",
    description="A system for semantic document retrieval and intelligent query processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    print("🚀 Starting LLM-Powered Query-Retrieval System (Minimal Version)...")
    print(f"🌐 Running on port: {os.getenv('PORT', 8000)}")

@app.get("/")
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": "Welcome to LLM-Powered Intelligent Query-Retrieval System",
        "status": "running",
        "version": "1.0.0-minimal",
        "docs": "/docs"
    }

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {
        "status": "healthy",
        "service": "llm-query-system",
        "version": "1.0.0-minimal",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/Container orchestration."""
    return {"status": "ready", "message": "Service is ready to accept requests"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main-minimal:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
