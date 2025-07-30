FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install minimal required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first
COPY requirements.txt .

# Install Python packages (cleaner and smaller)
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary source files (not everything!)
COPY . .

# Create only needed directories
RUN mkdir -p data/uploads data/faiss_index

# Expose port used by Uvicorn
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
