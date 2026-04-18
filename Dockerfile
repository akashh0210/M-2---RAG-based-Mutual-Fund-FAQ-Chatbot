FROM python:3.11-slim

# Install system dependencies
# build-essential is needed for compiled packages like greenlet and tiktoken
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure data directory exists
RUN mkdir -p /app/data

# Optimize huggingface tokenizers
ENV TOKENIZERS_PARALLELISM=false

# Expose the API port (Hugging Face default)
EXPOSE 7860

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
