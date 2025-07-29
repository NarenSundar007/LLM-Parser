from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class QueryIntent(str, Enum):
    COVERAGE_CHECK = "coverage_check"
    ELIGIBILITY = "eligibility"
    COMPLIANCE = "compliance"
    DEFINITION = "definition"
    PROCEDURE = "procedure"
    GENERAL = "general"

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    document_url: Optional[str] = Field(None, description="PDF blob URL")
    document_id: Optional[str] = Field(None, description="Existing document ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class ParsedQuery(BaseModel):
    intent: QueryIntent
    target_subject: str
    filter_conditions: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    original_query: str

class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    page_number: int
    chunk_index: int
    document_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchResult(BaseModel):
    chunk: DocumentChunk
    score: float
    embedding_similarity: float

class ClauseMatch(BaseModel):
    clause_text: str
    clause_id: str
    relevance_score: float
    page_reference: int
    section: Optional[str] = None

class LogicEvaluation(BaseModel):
    meets_criteria: bool
    applicable_conditions: List[str]
    rationale: str
    confidence_score: float
    supporting_evidence: List[str]

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Direct answer to the query")
    conditions: List[str] = Field(default_factory=list, description="Applicable conditions")
    clause: str = Field(..., description="Most relevant clause text")
    confidence: float = Field(..., description="Confidence score (0-1)")
    rationale: str = Field(..., description="Explanation of the reasoning")
    page_references: List[int] = Field(default_factory=list)
    additional_info: Optional[Dict[str, Any]] = Field(None)

class DocumentProcessingStatus(BaseModel):
    document_id: str
    status: str  # "processing", "completed", "failed"
    total_chunks: int
    processed_chunks: int
    error_message: Optional[str] = None

class SystemHealth(BaseModel):
    status: str
    vector_db_status: str
    llm_status: str
    total_documents: int
    total_chunks: int

class BatchQueryRequest(BaseModel):
    documents: str = Field(..., description="PDF blob URL")
    questions: List[str] = Field(..., description="List of questions to process")

class BatchQueryResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers corresponding to the questions")
