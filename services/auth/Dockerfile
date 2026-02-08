FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY ../../shared /app/shared
COPY ../syncvalue/database.py /app/services/syncvalue/database.py

# Copy application
COPY ./app /app/

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8030/healthz')"

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8030"]
