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
            "single_query": "/query",
            "batch_query": "/hackrx/run",
            "upload": "/upload",
            "search": "/search",
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

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query against documents.
    
    This endpoint:
    1. Processes PDF from blob URL (if provided)
    2. Parses the natural language query
    3. Performs semantic search
    4. Finds relevant clauses
    5. Evaluates logic and provides reasoning
    6. Returns structured JSON response
    """
    try:
        response = await query_system.query_documents(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.post("/documents/process")
async def process_document(
    blob_url: str,
    document_id: str = None,
    background_tasks: BackgroundTasks = None
):
    """
    Process a PDF document from blob URL and add to vector store.
    
    Args:
        blob_url: URL to the PDF blob
        document_id: Optional custom document ID
        background_tasks: Optional background processing
    """
    try:
        if background_tasks:
            # Process in background
            background_tasks.add_task(
                query_system.process_document, 
                blob_url, 
                document_id
            )
            return {
                "message": "Document processing started in background",
                "document_id": document_id or "auto-generated",
                "status": "processing"
            }
        else:
            # Process synchronously
            doc_id = await query_system.process_document(blob_url, document_id)
            return {
                "message": "Document processed successfully",
                "document_id": doc_id,
                "status": "completed"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.get("/documents/{document_id}/status")
async def get_document_status(document_id: str):
    """Get the processing status of a specific document."""
    try:
        status = await query_system.get_document_status(document_id)
        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Document not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document status: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all processed documents."""
    try:
        documents = await query_system.list_documents()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@app.post("/search")
async def search_documents(query: str, k: int = 5):
    """
    Search documents using semantic similarity without full query processing.
    
    Args:
        query: Search query
        k: Number of results to return
    """
    try:
        results = await query_system.search_documents(query, k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/documents/{document_id}/reprocess")
async def reprocess_document(document_id: str):
    """Reprocess an existing document."""
    try:
        success = await query_system.reprocess_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "message": "Document reprocessed successfully",
            "document_id": document_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")

@app.get("/stats")
async def get_statistics():
    """Get system statistics."""
    try:
        health = await query_system.get_system_health()
        documents = await query_system.list_documents()
        
        return {
            "system_health": health,
            "documents_stats": {
                "total_documents": documents["total_count"],
                "processed_documents": len([
                    d for d in documents["documents"].values() 
                    if d.get("status") == "processed"
                ]),
                "failed_documents": len([
                    d for d in documents["documents"].values() 
                    if d.get("status") == "failed"
                ])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

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
