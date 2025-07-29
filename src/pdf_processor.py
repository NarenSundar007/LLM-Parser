import io
import requests
import fitz  # PyMuPDF
import pdfplumber
from typing import List, Optional, Dict, Any
import uuid
import re
import tiktoken
from loguru import logger

from .models import DocumentChunk
from .config import settings

class PDFProcessor:
    """Handles PDF download, parsing, and text chunking."""
    
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    async def download_pdf_from_blob(self, blob_url: str) -> bytes:
        """Download PDF from blob URL."""
        try:
            logger.info(f"Downloading PDF from: {blob_url}")
            response = requests.get(blob_url, stream=True, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'pdf' not in content_type.lower():
                logger.warning(f"Content type may not be PDF: {content_type}")
            
            return response.content
        except Exception as e:
            logger.error(f"Failed to download PDF: {str(e)}")
            raise Exception(f"Failed to download PDF: {str(e)}")
    
    def extract_text_pymupdf(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Extract text using PyMuPDF with page-level granularity."""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Clean up text
                text = self._clean_text(text)
                
                if text.strip():  # Only include pages with content
                    pages.append({
                        'page_number': page_num + 1,
                        'text': text,
                        'char_count': len(text)
                    })
            
            doc.close()
            logger.info(f"Extracted text from {len(pages)} pages using PyMuPDF")
            return pages
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {str(e)}")
            raise
    
    def extract_text_pdfplumber(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Extract text using pdfplumber as fallback."""
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                pages = []
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    text = self._clean_text(text)
                    
                    if text.strip():
                        pages.append({
                            'page_number': page_num + 1,
                            'text': text,
                            'char_count': len(text)
                        })
                
                logger.info(f"Extracted text from {len(pages)} pages using pdfplumber")
                return pages
                
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        # Fix common PDF extraction issues
        text = text.replace('\u2019', "'").replace('\u2018', "'")
        text = text.replace('\u201c', '"').replace('\u201d', '"')
        text = text.replace('\u2013', '-').replace('\u2014', '-')
        
        return text.strip()
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, pages: List[Dict[str, Any]], document_id: str) -> List[DocumentChunk]:
        """Chunk text into overlapping segments."""
        chunks = []
        chunk_counter = 0
        
        for page_data in pages:
            page_number = page_data['page_number']
            text = page_data['text']
            
            # Split text into sentences for better chunking
            sentences = self._split_into_sentences(text)
            
            current_chunk = ""
            current_tokens = 0
            
            for sentence in sentences:
                sentence_tokens = self.count_tokens(sentence)
                
                # If adding this sentence would exceed chunk size, save current chunk
                if current_tokens + sentence_tokens > settings.chunk_size and current_chunk:
                    chunk = self._create_chunk(
                        content=current_chunk.strip(),
                        chunk_id=f"{document_id}_chunk_{chunk_counter}",
                        page_number=page_number,
                        chunk_index=chunk_counter,
                        document_id=document_id
                    )
                    chunks.append(chunk)
                    chunk_counter += 1
                    
                    # Start new chunk with overlap
                    overlap_text = self._get_overlap_text(current_chunk, settings.chunk_overlap)
                    current_chunk = overlap_text + " " + sentence
                    current_tokens = self.count_tokens(current_chunk)
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
                    current_tokens += sentence_tokens
            
            # Add remaining text as final chunk for this page
            if current_chunk.strip():
                chunk = self._create_chunk(
                    content=current_chunk.strip(),
                    chunk_id=f"{document_id}_chunk_{chunk_counter}",
                    page_number=page_number,
                    chunk_index=chunk_counter,
                    document_id=document_id
                )
                chunks.append(chunk)
                chunk_counter += 1
        
        logger.info(f"Created {len(chunks)} chunks for document {document_id}")
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - can be enhanced with NLTK
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str, overlap_tokens: int) -> str:
        """Get overlap text from the end of current chunk."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= overlap_tokens:
            return text
        
        overlap_token_ids = tokens[-overlap_tokens:]
        return self.encoding.decode(overlap_token_ids)
    
    def _create_chunk(self, content: str, chunk_id: str, page_number: int, 
                     chunk_index: int, document_id: str) -> DocumentChunk:
        """Create a DocumentChunk object."""
        return DocumentChunk(
            chunk_id=chunk_id,
            content=content,
            page_number=page_number,
            chunk_index=chunk_index,
            document_id=document_id,
            metadata={
                'token_count': self.count_tokens(content),
                'char_count': len(content)
            }
        )
    
    async def process_pdf(self, blob_url: str, document_id: Optional[str] = None) -> List[DocumentChunk]:
        """Main method to process PDF from blob URL to chunks."""
        if not document_id:
            document_id = str(uuid.uuid4())
        
        try:
            # Download PDF
            pdf_bytes = await self.download_pdf_from_blob(blob_url)
            
            # Try PyMuPDF first, fallback to pdfplumber
            try:
                pages = self.extract_text_pymupdf(pdf_bytes)
            except Exception as e:
                logger.warning(f"PyMuPDF failed, trying pdfplumber: {str(e)}")
                pages = self.extract_text_pdfplumber(pdf_bytes)
            
            # Chunk the text
            chunks = self.chunk_text(pages, document_id)
            
            # Limit chunks if necessary
            if len(chunks) > settings.max_chunks_per_doc:
                logger.warning(f"Document has {len(chunks)} chunks, limiting to {settings.max_chunks_per_doc}")
                chunks = chunks[:settings.max_chunks_per_doc]
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process PDF: {str(e)}")
            raise
