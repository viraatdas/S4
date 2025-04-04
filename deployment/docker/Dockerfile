FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for Pillow and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    tesseract-ocr \
    libtesseract-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional packages for embedding functionality
RUN pip install --no-cache-dir \
    pillow \
    pytesseract \
    python-docx \
    numpy \
    openai

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/data/indices /app/data/tenants /app/data/temp

# Expose API port
EXPOSE 8000

# Run initialization and start the service
CMD ["sh", "-c", "s4 init && s4 start"]  