# SyncBill - Billing & Settlement Service
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared dependencies
COPY shared/ /app/shared/
COPY schemas/ /app/schemas/
COPY constants/ /app/constants/

# Copy service code
COPY services/syncbill/requirements.txt .
COPY services/syncbill/app/ /app/app/
COPY services/syncbill/logic/ /app/logic/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create reports directory
RUN mkdir -p /tmp/kiki_reports

# Expose port
EXPOSE 8008

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8008/health', timeout=5)"

# Run the service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8008"]
