FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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