# LLM-Powered Intelligent Query-Retrieval System

## 🎯 Overview

This system provides intelligent document analysis and query processing capabilities using Large Language Models (LLMs), semantic search, and advanced NLP techniques. It's designed for use cases in **Insurance**, **Legal**, **HR**, and **Compliance** domains.

## ✨ Features

- **PDF Processing**: Download and parse PDFs from blob URLs
- **Semantic Search**: FAISS/Pinecone-powered vector similarity search
- **LLM Integration**: OpenAI GPT models for query parsing and logic evaluation
- **Structured Responses**: JSON output with reasoning and confidence scores
- **Multi-domain Support**: Insurance, Legal, HR, Compliance use cases
- **RESTful API**: FastAPI-based web service
- **Scalable Architecture**: Modular design with background processing

## 🧱 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF Input     │───▶│   Text Chunking   │───▶│   Embeddings    │
│  (Blob URLs)    │    │   (Overlapping)   │    │   Generation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                          │
┌─────────────────┐    ┌──────────────────┐              ▼
│  User Query     │───▶│   LLM Parser     │    ┌─────────────────┐
│ (Natural Lang)  │    │  (Intent/Subject) │    │  Vector Store   │
└─────────────────┘    └──────────────────┘    │  (FAISS/Pinecone)│
                                │               └─────────────────┘
                                ▼                         │
┌─────────────────┐    ┌──────────────────┐              ▼
│ Structured      │◀───│  Logic Evaluator │    ┌─────────────────┐
│ JSON Response   │    │    (LLM-based)   │◀───│  Semantic Search │
└─────────────────┘    └──────────────────┘    │   (Top-K)       │
                                                └─────────────────┘
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd "Bajaj Hackathon"

# WINDOWS USERS: Create virtual environment to avoid permission issues
python -m venv venv

# Activate virtual environment
# Windows Command Prompt:
venv\Scripts\activate
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Git Bash/Linux/macOS:
source venv/bin/activate

# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**🚨 Windows Permission Fix:**
If you get permission errors, use one of these approaches:
```bash
# Option 1: Install with --user flag
pip install --user -r requirements.txt

# Option 2: Run as administrator (open cmd as admin)
pip install -r requirements.txt

# Option 3: Use conda environment
conda create -n bajaj-env python=3.9
conda activate bajaj-env
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and configure:

```env
# Required: Groq API Key (FREE)
GROQ_API_KEY=gsk_your_groq_api_key_here

# LLM Configuration
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile
EMBEDDING_MODEL=sentence-transformers

# Optional: Pinecone (default uses FAISS)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
USE_PINECONE=false
```

**🆓 FREE Setup**: 
- Get your Groq API key at: https://console.groq.com/
- Uses local SentenceTransformers for embeddings (no cost)
- FAISS for vector storage (no external dependencies)

**📚 See [GROQ_SETUP.md](GROQ_SETUP.md) for detailed setup guide**

### 3. Run the System

```bash
# Start the API server
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**🚨 Common Import Errors & Fixes:**

**Error: `BaseSettings has been moved to pydantic-settings`**
```bash
# Quick fix:
pip install pydantic-settings==2.1.0

# If permission denied:
pip install --user pydantic-settings==2.1.0
```

**Error: `cannot import name 'cached_download' from 'huggingface_hub'`**
```bash
# Fix version conflicts:
pip uninstall huggingface-hub
pip install huggingface-hub==0.17.3 transformers==4.35.2

# If permission denied:
pip install --user huggingface-hub==0.17.3 transformers==4.35.2
```

**Error: Multiple dependency conflicts**
```bash
# Run the automated fix script:
python fix_dependencies.py

# This will fix all common dependency issues automatically
```

**Error: Package permission denied**
```bash
# Use virtual environment (recommended):
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

The API will be available at: `http://localhost:8000`
Interactive documentation: `http://localhost:8000/docs`

## 📋 API Usage

### Process a Document and Query

```python
import requests

# Process document and query
response = requests.post("http://localhost:8000/query", json={
    "query": "Does this policy cover knee surgery?",
    "document_url": "https://example.com/policy.pdf"
})

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Rationale: {result['rationale']}")
```

### Example Response

```json
{
  "answer": "Yes",
  "conditions": ["Pre-approval required", "In-network provider"],
  "clause": "Section 4.3 - Surgical procedures including knee surgery are covered when performed by in-network providers with prior authorization.",
  "confidence": 0.89,
  "rationale": "The policy explicitly covers knee surgery under surgical procedures with specific conditions for pre-approval and network providers.",
  "page_references": [12, 13],
  "additional_info": {
    "parsed_query": {
      "intent": "coverage_check",
      "target_subject": "knee surgery"
    }
  }
}
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | System information |
| `GET` | `/health` | Health check |
| `POST` | `/query` | Process query with document |
| `POST` | `/documents/process` | Process document only |
| `GET` | `/documents` | List all documents |
| `GET` | `/documents/{id}/status` | Get document status |
| `POST` | `/search` | Semantic search only |
| `GET` | `/stats` | System statistics |

## 🏗️ System Components

### 1. PDF Processor (`src/pdf_processor.py`)
- Downloads PDFs from blob URLs
- Extracts text using PyMuPDF/pdfplumber
- Creates overlapping text chunks
- Token counting and optimization

### 2. LLM Parser (`src/llm_parser.py`)
- Query intent classification
- Subject extraction
- Logic evaluation and reasoning
- Structured response generation

### 3. Vector Search (`src/vector_search.py`)
- Embedding generation (OpenAI/SentenceTransformers)
- FAISS/Pinecone vector storage
- Semantic similarity search
- Result ranking and scoring

### 4. Query System (`src/query_retrieval_system.py`)
- Main orchestrator
- Document management
- End-to-end query processing
- Error handling and logging

## 🎯 Use Case Examples

### Insurance
```python
{
  "query": "Is dental cleaning covered under preventive care?",
  "document_url": "https://insurance.com/policy.pdf"
}
```

### Legal
```python
{
  "query": "What are the force majeure clauses in this contract?",
  "document_url": "https://legal.com/contract.pdf"
}
```

### HR
```python
{
  "query": "What is the parental leave policy for new fathers?",
  "document_url": "https://hr.com/handbook.pdf"
}
```

### Compliance
```python
{
  "query": "Does this privacy policy comply with CCPA requirements?",
  "document_url": "https://company.com/privacy.pdf"
}
```

## ⚙️ Configuration Options

### Document Processing
- `CHUNK_SIZE`: Token size per chunk (default: 200)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 40)
- `MAX_CHUNKS_PER_DOC`: Maximum chunks per document (default: 1000)

### LLM Settings
- `LLM_MODEL`: OpenAI model name (default: gpt-3.5-turbo)
- `TEMPERATURE`: LLM creativity (default: 0.1)
- `MAX_TOKENS`: Max response tokens (default: 2000)

### Vector Store
- `USE_PINECONE`: Use Pinecone vs FAISS (default: false)
- `FAISS_INDEX_PATH`: Local FAISS storage path
- `PINECONE_INDEX_NAME`: Pinecone index name

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test specific functionality
python -m pytest tests/test_pdf_processor.py -v

# Load testing
python tests/load_test.py
```

## 📊 Monitoring

- Health check endpoint: `/health`
- System statistics: `/stats`
- Document processing status: `/documents/{id}/status`
- Logging with structured output

## 🔒 Security Considerations

- API key management
- Input validation and sanitization
- Rate limiting (recommended)
- Document access controls
- Secure blob URL handling

## 🚀 Deployment

### Docker Deployment
```bash
# Build container
docker build -t query-retrieval-system .

# Run container
docker run -p 8000:8000 --env-file .env query-retrieval-system
```

### Production Setup
- Use production WSGI server (Gunicorn)
- Set up reverse proxy (Nginx)
- Configure SSL/TLS
- Implement monitoring and logging
- Set up database for persistence

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Create GitHub issue
- Check documentation
- Review API examples
- Test with provided endpoints

---

**Built for Bajaj Hackathon 2025** 🏆
