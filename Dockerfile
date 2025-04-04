FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY server/ ./server/
COPY s4/ ./s4/

# Create necessary directories
RUN mkdir -p /app/data/indices /app/data/tenants /app/data/temp

# Set environment variables
ENV S4_DATA_DIR=/app/data
ENV PYTHONPATH=/app
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Run the server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "server.server:app"]
