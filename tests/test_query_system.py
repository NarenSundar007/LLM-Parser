import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.query_retrieval_system import QueryRetrievalSystem
from src.models import QueryRequest, QueryIntent

class TestQueryRetrievalSystem:
    
    @pytest.fixture
    def query_system(self):
        return QueryRetrievalSystem()
    
    @pytest.mark.asyncio
    async def test_process_simple_query(self, query_system):
        """Test processing a simple query without document URL."""
        
        # Mock the dependencies
        with patch.object(query_system.llm_parser, 'parse_query') as mock_parse, \
             patch.object(query_system.vector_search, 'search_similar_chunks') as mock_search, \
             patch.object(query_system.llm_parser, 'evaluate_logic') as mock_eval, \
             patch.object(query_system.llm_parser, 'generate_final_response') as mock_response:
            
            # Setup mocks
            mock_parse.return_value = Mock(
                intent=QueryIntent.COVERAGE_CHECK,
                target_subject="knee surgery",
                filter_conditions=[],
                keywords=["knee", "surgery"],
                original_query="Does this cover knee surgery?"
            )
            
            mock_search.return_value = [
                Mock(
                    chunk=Mock(
                        content="Knee surgery is covered with pre-approval.",
                        page_number=5,
                        chunk_id="test_chunk_1",
                        chunk_index=1
                    ),
                    score=0.85
                )
            ]
            
            mock_eval.return_value = {
                "meets_criteria": True,
                "applicable_conditions": ["Pre-approval required"],
                "rationale": "Clear coverage statement",
                "confidence_score": 0.85
            }
            
            mock_response.return_value = {
                "answer": "Yes",
                "conditions": ["Pre-approval required"],
                "clause": "Knee surgery is covered with pre-approval.",
                "confidence": 0.85,
                "rationale": "Clear coverage statement"
            }
            
            # Test the query
            request = QueryRequest(query="Does this cover knee surgery?")
            response = await query_system.query_documents(request)
            
            assert response.answer == "Yes"
            assert "Pre-approval required" in response.conditions
            assert response.confidence == 0.85
    
    @pytest.mark.asyncio
    async def test_no_results_response(self, query_system):
        """Test response when no relevant documents are found."""
        
        with patch.object(query_system.vector_search, 'search_similar_chunks') as mock_search:
            mock_search.return_value = []
            
            request = QueryRequest(query="Test query with no results")
            response = await query_system.query_documents(request)
            
            assert response.answer == "No relevant information found"
            assert response.confidence == 0.0
            assert "no_results" in response.additional_info.get("status", "")
    
    def test_document_store(self, query_system):
        """Test document storage functionality."""
        doc_id = "test_doc_1"
        doc_info = {
            'url': 'http://example.com/test.pdf',
            'chunks': 10,
            'status': 'processed'
        }
        
        query_system.document_store[doc_id] = doc_info
        
        assert doc_id in query_system.document_store
        assert query_system.document_store[doc_id]['status'] == 'processed'
