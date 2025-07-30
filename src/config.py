import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Groq Configuration
    groq_api_key: str = ""
    
    # Gemini Configuration (Primary LLM Provider)
    gemini_api_key: str = ""
    llm_provider: str = "gemini"  # "gemini", "groq", or "openai"
    llm_model: str = "gemini-1.5-flash"  # Gemini model
    
    # OpenAI Configuration (Fallback/Embeddings)
    openai_api_key: str = ""
    embedding_model: str = "sentence-transformers"  # "sentence-transformers" or "text-embedding-ada-002"
    
    # LLM Parameters
    max_tokens: int = 2000
    temperature: float = 0.1
    
    # Pinecone Configuration
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = "document-retrieval"
    use_pinecone: bool = False
    
    # FAISS Configuration
    faiss_index_path: str = "./data/faiss_index"
    
    # Document Processing
    chunk_size: int = 200
    chunk_overlap: int = 40
    max_chunks_per_doc: int = 1000
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", 8000))  # Use Render's PORT env var
    debug: bool = os.getenv("ENVIRONMENT", "development") != "production"
    
    # Logging
    log_level: str = "INFO"
    
    # Data directories
    data_dir: str = "./data"
    uploads_dir: str = "./data/uploads"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env file

# Global settings instance
settings = Settings()

# Ensure data directories exist
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(settings.uploads_dir, exist_ok=True)
os.makedirs(os.path.dirname(settings.faiss_index_path), exist_ok=True)
