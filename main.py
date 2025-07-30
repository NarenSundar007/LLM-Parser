from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import List, Dict, Any
from loguru import logger

from src.models import QueryRequest, QueryResponse, SystemHealth, BatchQueryRequest, BatchQueryResponse
from src.query_retrieval_system import QueryRetrievalSystem
from src.config import settings

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

# Initialize the main system
query_system = QueryRetrievalSystem()

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    print("🚀 Starting LLM-Powered Query-Retrieval System...")
    print(f"📊 Vector Store: {'Pinecone' if settings.use_pinecone else 'FAISS'}")
    print(f"🤖 LLM Provider: {settings.llm_provider.upper()}")
    print(f"🧠 LLM Model: {settings.llm_model}")
    print(f"🔗 Embedding Model: {settings.embedding_model}")
    if settings.llm_provider == "groq":
        print("💰 Cost: FREE with Groq + SentenceTransformers!")
    print(f"📖 API Docs: http://0.0.0.0:{settings.api_port}/docs")
    print(f"🌐 Running on port: {settings.api_port}")
    if settings.debug:
        print("🔧 Debug mode: ON")
    else:
        print("🏭 Production mode: ON")

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "LLM-Powered Intelligent Query-Retrieval System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "endpoints": {
            "batch_query": "/hackrx/run",
            "system_health": "/health"
        }
    }

@app.get("/ready")
async def readiness_check():
    """Simple readiness check that responds immediately."""
    return {
        "status": "ready",
        "timestamp": "2025-07-29T09:26:00Z",
        "service": "llm-query-system"
    }

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Get system health status."""
    try:
        health_info = await query_system.get_system_health()
        return health_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/hackrx/run", response_model=BatchQueryResponse)
async def process_batch_queries(request: BatchQueryRequest):
    """
    Process multiple questions for a single document in batch.
    
    Expected input format:
    {
        "documents": "https://blob.core.windows.net/assets/policy.pdf?...",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            ...
        ]
    }
    
    Returns:
    {
        "answers": [
            "A grace period of thirty days is provided...",
            "There is a waiting period of thirty-six months...",
            ...
        ]
    }
    """
    try:
        logger.info(f"Processing batch query with {len(request.questions)} questions")
        
        # Process all questions for the document
        answers = await query_system.process_batch_queries(
            document_url=request.documents,
            questions=request.questions
        )
        
        return BatchQueryResponse(answers=answers)
        
    except Exception as e:
        logger.error(f"Batch query processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch query processing failed: {str(e)}")

# Example endpoint for testing
@app.post("/test/example-query")
async def test_example_query():
    """Test endpoint with example queries for different domains."""
    
    examples = {
        "insurance": {
            "query": "Does this policy cover knee surgery?",
            "expected_intent": "coverage_check",
            "expected_subject": "knee surgery"
        },
        "legal": {
            "query": "What are the termination clauses in this contract?",
            "expected_intent": "definition",
            "expected_subject": "termination clauses"
        },
        "hr": {
            "query": "What is the eligibility criteria for health benefits?",
            "expected_intent": "eligibility",
            "expected_subject": "health benefits"
        },
        "compliance": {
            "query": "Does this meet GDPR data retention requirements?",
            "expected_intent": "compliance",
            "expected_subject": "GDPR data retention"
        }
    }
    
    return {
        "message": "Example queries for testing",
        "examples": examples,
        "usage": "Use POST /query with a QueryRequest containing one of these queries and a document URL"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
