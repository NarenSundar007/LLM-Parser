import pytest
import asyncio
from unittest.mock import Mock, patch
from src.pdf_processor import PDFProcessor

class TestPDFProcessor:
    
    @pytest.fixture
    def pdf_processor(self):
        return PDFProcessor()
    
    @pytest.mark.asyncio
    async def test_download_pdf_success(self, pdf_processor):
        """Test successful PDF download."""
        mock_response = Mock()
        mock_response.content = b"fake_pdf_content"
        mock_response.headers = {"content-type": "application/pdf"}
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            result = await pdf_processor.download_pdf_from_blob("http://example.com/test.pdf")
            assert result == b"fake_pdf_content"
    
    def test_clean_text(self, pdf_processor):
        """Test text cleaning functionality."""
        dirty_text = "This  is\xa0\xa0\xa0  some\n\n\n  dirty   text\u2019s"
        cleaned = pdf_processor._clean_text(dirty_text)
        assert "  " not in cleaned  # No double spaces
        assert "\n\n" not in cleaned  # No excessive newlines
        assert "'" in cleaned  # Smart quotes converted
    
    def test_count_tokens(self, pdf_processor):
        """Test token counting."""
        text = "This is a simple test text."
        token_count = pdf_processor.count_tokens(text)
        assert isinstance(token_count, int)
        assert token_count > 0
    
    def test_split_into_sentences(self, pdf_processor):
        """Test sentence splitting."""
        text = "First sentence. Second sentence! Third sentence?"
        sentences = pdf_processor._split_into_sentences(text)
        assert len(sentences) == 3
        assert "First sentence" in sentences[0]
