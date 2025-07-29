from typing import List, Dict, Any, Optional
from loguru import logger
import uuid
import time

from .models import (
    QueryRequest, QueryResponse, ParsedQuery, SearchResult, 
    ClauseMatch, LogicEvaluation, DocumentChunk
)
from .pdf_processor import PDFProcessor
from .llm_parser import LLMParser
from .vector_search import VectorSearchEngine
from .config import settings

class QueryRetrievalSystem:
    """Main orchestrator for the LLM-powered query-retrieval system."""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.llm_parser = LLMParser()
        self.vector_search = VectorSearchEngine()
        self.document_store = {}  # In-memory store for processed documents
    
    async def process_document(self, blob_url: str, document_id: Optional[str] = None) -> str:
        """Process a PDF document and add it to the vector store."""
        try:
            doc_start_time = time.time()
            
            if not document_id:
                document_id = str(uuid.uuid4())
            
            logger.info(f"Processing document {document_id} from {blob_url}")
            
            # Step 1: Process PDF to chunks
            pdf_start_time = time.time()
            chunks = await self.pdf_processor.process_pdf(blob_url, document_id)
            pdf_end_time = time.time()
            logger.info(f"⏱️ PDF processing (download + extract + chunk) took: {pdf_end_time - pdf_start_time:.2f} seconds")
            
            # Step 2: Add chunks to vector store
            vector_start_time = time.time()
            await self.vector_search.add_document_chunks(chunks)
            vector_end_time = time.time()
            logger.info(f"⏱️ Vector store operations (embed + index) took: {vector_end_time - vector_start_time:.2f} seconds")
            
            # Step 3: Store document metadata
            self.document_store[document_id] = {
                'url': blob_url,
                'chunks': len(chunks),
                'status': 'processed'
            }
            
            doc_end_time = time.time()
            logger.info(f"⏱️ Total document processing time: {doc_end_time - doc_start_time:.2f} seconds")
            logger.info(f"Successfully processed document {document_id} with {len(chunks)} chunks")
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to process document: {str(e)}")
            if document_id:
                self.document_store[document_id] = {
                    'url': blob_url,
                    'chunks': 0,
                    'status': 'failed',
                    'error': str(e)
                }
            raise
    
    async def query_documents(self, request: QueryRequest) -> QueryResponse:
        """Main method to handle document queries."""
        try:
            logger.info(f"Processing query: {request.query}")
            
            # If document URL provided, process it first
            if request.document_url:
                document_id = await self.process_document(
                    request.document_url, 
                    request.document_id
                )
            
            # Step 1: Parse the query using LLM
            parsed_query = await self.llm_parser.parse_query(
                request.query, 
                request.context
            )
            logger.info(f"Parsed query - Intent: {parsed_query.intent}, Subject: {parsed_query.target_subject}")
            
            # Step 2: Perform semantic search
            search_results = await self.vector_search.search_similar_chunks(
                query=request.query,
                k=10  # Get more results for better clause matching
            )
            
            if not search_results:
                return self._create_no_results_response(request.query)
            
            logger.info(f"Found {len(search_results)} relevant chunks")
            
            # Step 3: Find the best matching clause
            best_clause_match = await self._find_best_clause(
                parsed_query, 
                search_results
            )
            
            # Step 4: Evaluate logic using LLM
            relevant_clauses = [result.chunk.content for result in search_results[:5]]
            logic_evaluation = await self.llm_parser.evaluate_logic(
                query=request.query,
                relevant_clauses=relevant_clauses,
                context=request.context
            )
            
            # Step 5: Generate final response
            page_refs = list(set([result.chunk.page_number for result in search_results[:5]]))
            final_response = await self.llm_parser.generate_final_response(
                query=request.query,
                best_clause=best_clause_match.clause_text,
                logic_eval=logic_evaluation,
                page_refs=page_refs
            )
            
            # Step 6: Create structured response
            response = QueryResponse(
                answer=final_response.get("answer", "Unable to determine"),
                conditions=final_response.get("conditions", []),
                clause=final_response.get("clause", best_clause_match.clause_text),
                confidence=final_response.get("confidence", best_clause_match.relevance_score),
                rationale=final_response.get("rationale", "Analysis completed"),
                page_references=page_refs,
                additional_info={
                    "parsed_query": parsed_query.dict(),
                    "search_results_count": len(search_results),
                    "document_id": request.document_id,
                    "logic_evaluation": logic_evaluation
                }
            )
            
            logger.info(f"Query processed successfully - Answer: {response.answer}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process query: {str(e)}")
            return self._create_error_response(request.query, str(e))
    
    async def _find_best_clause(self, parsed_query: ParsedQuery, 
                               search_results: List[SearchResult]) -> ClauseMatch:
        """Find the most relevant clause from search results."""
        
        if not search_results:
            return ClauseMatch(
                clause_text="No relevant clauses found",
                clause_id="none",
                relevance_score=0.0,
                page_reference=0
            )
        
        # For now, use the top search result as the best clause
        # This could be enhanced with more sophisticated reranking
        best_result = search_results[0]
        
        return ClauseMatch(
            clause_text=best_result.chunk.content,
            clause_id=best_result.chunk.chunk_id,
            relevance_score=best_result.score,
            page_reference=best_result.chunk.page_number,
            section=f"Chunk {best_result.chunk.chunk_index}"
        )
    
    async def _find_best_clause_simple(self, search_results: List[SearchResult]) -> ClauseMatch:
        """Simple best clause matching without LLM for speed."""
        if not search_results:
            return ClauseMatch(
                clause_text="No relevant clauses found",
                clause_id="none",
                relevance_score=0.0,
                page_reference=0
            )
        
        # Simply use the top search result (already ranked by semantic similarity)
        best_result = search_results[0]
        
        return ClauseMatch(
            clause_text=best_result.chunk.content,
            clause_id=best_result.chunk.chunk_id,
            relevance_score=best_result.score,
            page_reference=best_result.chunk.page_number,
            section=f"Chunk {best_result.chunk.chunk_index}"
        )
    
    def _create_no_results_response(self, query: str) -> QueryResponse:
        """Create response when no relevant documents are found."""
        return QueryResponse(
            answer="No relevant information found",
            conditions=[],
            clause="No matching clauses found in the document.",
            confidence=0.0,
            rationale="The system could not find any relevant information to answer your query. This may be because the topic is not covered in the document or the query needs to be more specific.",
            page_references=[],
            additional_info={"status": "no_results"}
        )
    
    def _create_error_response(self, query: str, error: str) -> QueryResponse:
        """Create response when an error occurs."""
        return QueryResponse(
            answer="Error processing query",
            conditions=[],
            clause="An error occurred while processing your request.",
            confidence=0.0,
            rationale=f"The system encountered an error: {error}",
            page_references=[],
            additional_info={"error": error, "status": "error"}
        )
    
    async def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """Get the processing status of a document."""
        return self.document_store.get(document_id, {"status": "not_found"})
    
    async def list_documents(self) -> Dict[str, Any]:
        """List all processed documents."""
        return {
            "documents": self.document_store,
            "total_count": len(self.document_store)
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health and statistics."""
        try:
            vector_stats = self.vector_search.get_stats()
            
            return {
                "status": "healthy",
                "vector_db_status": "connected",
                "llm_status": "connected" if settings.openai_api_key else "not_configured",
                "total_documents": len(self.document_store),
                "total_chunks": vector_stats.get("total_chunks", 0),
                "vector_store_type": "faiss" if not settings.use_pinecone else "pinecone",
                "embedding_model": settings.embedding_model
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "vector_db_status": "error",
                "llm_status": "unknown"
            }
    
    async def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search documents without full query processing."""
        try:
            search_results = await self.vector_search.search_similar_chunks(query, k)
            
            return [
                {
                    "content": result.chunk.content,
                    "page_number": result.chunk.page_number,
                    "document_id": result.chunk.document_id,
                    "similarity_score": result.score,
                    "chunk_id": result.chunk.chunk_id
                }
                for result in search_results
            ]
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    async def reprocess_document(self, document_id: str) -> bool:
        """Reprocess an existing document."""
        try:
            doc_info = self.document_store.get(document_id)
            if not doc_info:
                return False
            
            # Remove old document data (implementation depends on vector store)
            # For now, we'll just reprocess and add
            await self.process_document(doc_info['url'], document_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to reprocess document {document_id}: {str(e)}")
            return False
    
    async def process_batch_queries(self, document_url: str, questions: List[str]) -> List[str]:
        """Process multiple questions for a single document and return batch answers."""
        try:
            total_start_time = time.time()
            
            # Generate a unique document ID for this batch
            document_id = f"batch_{str(uuid.uuid4())[:8]}"
            
            # Step 1: Process the document ONCE for the entire batch
            doc_start_time = time.time()
            logger.info(f"Processing document for batch queries: {document_url}")
            await self.process_document(document_url, document_id)
            doc_end_time = time.time()
            logger.info(f"⏱️ Document processing took: {doc_end_time - doc_start_time:.2f} seconds")
            
            # Step 2: Process questions sequentially but with optimized combined API calls
            answers = []
            questions_start_time = time.time()
            
            for i, question in enumerate(questions):
                question_start_time = time.time()
                logger.info(f"Processing question {i+1}/{len(questions)}: {question}")
                
                try:
                    # Step 1: Perform semantic search on already processed document
                    search_start_time = time.time()
                    search_results = await self.vector_search.search_similar_chunks(
                        query=question,
                        k=15  # Get more results for comprehensive analysis
                    )
                    search_end_time = time.time()
                    logger.info(f"⏱️ Vector search took: {search_end_time - search_start_time:.2f} seconds")
                    
                    if not search_results:
                        answers.append("No relevant information found in the document for this question.")
                        continue
                    
                    logger.info(f"Found {len(search_results)} relevant chunks")
                    
                    # Step 2: Find the best matching clause
                    clause_start_time = time.time()
                    best_clause_match = await self._find_best_clause_simple(search_results)
                    clause_end_time = time.time()
                    logger.info(f"⏱️ Best clause matching took: {clause_end_time - clause_start_time:.2f} seconds")
                    
                    # Step 3: Combined parsing, logic evaluation, and response generation with comprehensive analysis
                    combined_start_time = time.time()
                    
                    # Use top 5 clauses for comprehensive analysis (increased from 2)
                    top_clauses = [result.chunk.content for result in search_results[:5]]
                    
                    # Use the improved combined method for comprehensive processing
                    combined_analysis = await self.llm_parser.parse_and_evaluate_combined(
                        question, top_clauses
                    )
                    
                    # Generate comprehensive final response using the combined analysis
                    final_response = await self.llm_parser.generate_fast_response(
                        question, combined_analysis, best_clause_match.clause_text
                    )
                    
                    combined_end_time = time.time()
                    logger.info(f"⏱️ Comprehensive LLM processing took: {combined_end_time - combined_start_time:.2f} seconds")
                    
                    # Extract just the answer text and ensure it's a string
                    raw_answer = final_response.get('answer', 'Unable to process query')
                    
                    # Ensure answer is always a string (handle cases where LLM returns objects)
                    if isinstance(raw_answer, dict):
                        # If it's a dict, extract the main text or convert to string
                        answer_text = raw_answer.get('text', '') or raw_answer.get('answer', '') or str(raw_answer)
                    elif isinstance(raw_answer, list):
                        # If it's a list, join the items
                        answer_text = '; '.join(str(item) for item in raw_answer)
                    else:
                        # If it's already a string or other type, convert to string
                        answer_text = str(raw_answer)
                    
                    answers.append(answer_text)
                    
                    question_end_time = time.time()
                    logger.info(f"⏱️ Total time for question {i+1}: {question_end_time - question_start_time:.2f} seconds")
                    
                except Exception as e:
                    logger.error(f"Failed to process question {i+1}: {str(e)}")
                    answers.append(f"Unable to process this question: {str(e)}")
            
            questions_end_time = time.time()
            total_end_time = time.time()
            
            logger.info(f"⏱️ All questions processing took: {questions_end_time - questions_start_time:.2f} seconds")
            logger.info(f"⏱️ TOTAL BATCH PROCESSING TIME: {total_end_time - total_start_time:.2f} seconds")
            logger.info(f"Successfully processed {len(questions)} questions")
            return answers
            
        except Exception as e:
            logger.error(f"Failed to process batch queries: {str(e)}")
            # Return error message for each question
            return [f"Error processing questions: {str(e)}"] * len(questions)
