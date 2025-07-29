import numpy as np
import faiss
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import asyncio
from loguru import logger

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available - using SentenceTransformers only")

from .models import DocumentChunk, SearchResult
from .config import settings

class EmbeddingGenerator:
    """Handles text embedding generation using SentenceTransformers or OpenAI."""
    
    def __init__(self):
        self.embedding_model = settings.embedding_model
        
        if self.embedding_model == "sentence-transformers":
            # Use local SentenceTransformers (FREE)
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast and good quality
            self.use_openai = False
            self.dimension = 384  # all-MiniLM-L6-v2 dimension
            logger.info("Using SentenceTransformers embeddings (FREE)")
        elif OPENAI_AVAILABLE and settings.openai_api_key:
            # Use OpenAI embeddings if available
            openai.api_key = settings.openai_api_key
            self.model_name = settings.embedding_model
            self.use_openai = True
            self.dimension = 1536  # OpenAI ada-002 dimension
            logger.info("Using OpenAI embeddings")
        else:
            # Fallback to SentenceTransformers if OpenAI not available
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_openai = False
            self.dimension = 384
            logger.warning("OpenAI not available, falling back to SentenceTransformers")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if self.use_openai:
            return await self._generate_openai_embeddings(texts)
        else:
            return self._generate_sentence_transformer_embeddings(texts)
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]
    
    async def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI module not available")
            
        try:
            # Process in batches to avoid API limits
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await openai.Embedding.acreate(
                    model=self.model_name,
                    input=batch
                )
                
                batch_embeddings = [item['embedding'] for item in response['data']]
                all_embeddings.extend(batch_embeddings)
                
                # Add small delay to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            logger.info(f"Generated {len(all_embeddings)} embeddings using OpenAI")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {str(e)}")
            raise
    
    def _generate_sentence_transformer_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using SentenceTransformers."""
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            logger.info(f"Generated {len(embeddings)} embeddings using SentenceTransformers")
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"SentenceTransformer embedding generation failed: {str(e)}")
            raise

class FAISSVectorStore:
    """FAISS-based vector storage and retrieval."""
    
    def __init__(self, dimension: int = 384):  # Default to SentenceTransformers dimension
        self.dimension = dimension
        self.index = None
        self.chunks_metadata = []
        self.index_path = settings.faiss_index_path
    
    def create_index(self):
        """Create a new FAISS index."""
        # Use IndexFlatIP for cosine similarity
        self.index = faiss.IndexFlatIP(self.dimension)
        logger.info(f"Created new FAISS index with dimension {self.dimension}")
    
    def add_embeddings(self, embeddings: List[List[float]], chunks: List[DocumentChunk]):
        """Add embeddings and metadata to the index."""
        if self.index is None:
            self.create_index()
        
        # Convert to numpy array and normalize for cosine similarity
        embeddings_array = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings_array)
        
        # Add to index
        self.index.add(embeddings_array)
        
        # Store metadata
        self.chunks_metadata.extend(chunks)
        
        logger.info(f"Added {len(embeddings)} embeddings to FAISS index")
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[SearchResult]:
        """Search for similar embeddings."""
        if self.index is None or self.index.ntotal == 0:
            logger.warning("No embeddings in index")
            return []
        
        # Normalize query embedding
        query_array = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_array)
        
        # Search
        scores, indices = self.index.search(query_array, k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.chunks_metadata):
                chunk = self.chunks_metadata[idx]
                result = SearchResult(
                    chunk=chunk,
                    score=float(score),
                    embedding_similarity=float(score)
                )
                results.append(result)
        
        return results
    
    def save_index(self):
        """Save FAISS index and metadata to disk."""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, f"{self.index_path}.index")
            
            # Save metadata
            with open(f"{self.index_path}.metadata", 'wb') as f:
                pickle.dump(self.chunks_metadata, f)
            
            logger.info(f"Saved FAISS index to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {str(e)}")
            raise
    
    def load_index(self) -> bool:
        """Load FAISS index and metadata from disk."""
        try:
            index_file = f"{self.index_path}.index"
            metadata_file = f"{self.index_path}.metadata"
            
            if os.path.exists(index_file) and os.path.exists(metadata_file):
                # Load FAISS index
                self.index = faiss.read_index(index_file)
                
                # Load metadata
                with open(metadata_file, 'rb') as f:
                    self.chunks_metadata = pickle.load(f)
                
                logger.info(f"Loaded FAISS index with {self.index.ntotal} embeddings")
                return True
            else:
                logger.info("No existing FAISS index found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        return {
            "total_embeddings": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "total_chunks": len(self.chunks_metadata)
        }

class PineconeVectorStore:
    """Pinecone-based vector storage (optional)."""
    
    def __init__(self):
        try:
            import pinecone
            pinecone.init(
                api_key=settings.pinecone_api_key,
                environment=settings.pinecone_environment
            )
            self.index = pinecone.Index(settings.pinecone_index_name)
            self.chunks_map = {}  # Map vector IDs to chunks
            logger.info("Initialized Pinecone vector store")
        except ImportError:
            logger.error("Pinecone client not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise
    
    async def add_embeddings(self, embeddings: List[List[float]], chunks: List[DocumentChunk]):
        """Add embeddings to Pinecone index."""
        try:
            vectors = []
            for i, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
                vector_id = chunk.chunk_id
                metadata = {
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "document_id": chunk.document_id
                }
                vectors.append((vector_id, embedding, metadata))
                self.chunks_map[vector_id] = chunk
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Added {len(vectors)} embeddings to Pinecone")
            
        except Exception as e:
            logger.error(f"Failed to add embeddings to Pinecone: {str(e)}")
            raise
    
    async def search(self, query_embedding: List[float], k: int = 5) -> List[SearchResult]:
        """Search Pinecone index."""
        try:
            response = self.index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True
            )
            
            results = []
            for match in response['matches']:
                vector_id = match['id']
                score = match['score']
                
                if vector_id in self.chunks_map:
                    chunk = self.chunks_map[vector_id]
                    result = SearchResult(
                        chunk=chunk,
                        score=score,
                        embedding_similarity=score
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Pinecone search failed: {str(e)}")
            return []

class VectorSearchEngine:
    """Main interface for vector search operations."""
    
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        
        if settings.use_pinecone and settings.pinecone_api_key:
            self.vector_store = PineconeVectorStore()
        else:
            # Use correct dimension based on embedding model
            dimension = self.embedding_generator.dimension
            self.vector_store = FAISSVectorStore(dimension=dimension)
            self.vector_store.load_index()  # Try to load existing index
    
    async def add_document_chunks(self, chunks: List[DocumentChunk]):
        """Add document chunks to the vector store."""
        try:
            # Generate embeddings for all chunks
            texts = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_generator.generate_embeddings(texts)
            
            # Add to vector store
            if isinstance(self.vector_store, FAISSVectorStore):
                self.vector_store.add_embeddings(embeddings, chunks)
                self.vector_store.save_index()
            else:
                await self.vector_store.add_embeddings(embeddings, chunks)
            
            logger.info(f"Successfully added {len(chunks)} chunks to vector store")
            
        except Exception as e:
            logger.error(f"Failed to add chunks to vector store: {str(e)}")
            raise
    
    async def search_similar_chunks(self, query: str, k: int = 5) -> List[SearchResult]:
        """Search for chunks similar to the query."""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_generator.generate_single_embedding(query)
            
            # Search vector store
            if isinstance(self.vector_store, FAISSVectorStore):
                results = self.vector_store.search(query_embedding, k)
            else:
                results = await self.vector_store.search(query_embedding, k)
            
            logger.info(f"Found {len(results)} similar chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        if isinstance(self.vector_store, FAISSVectorStore):
            return self.vector_store.get_stats()
        else:
            return {"status": "Pinecone vector store active"}
