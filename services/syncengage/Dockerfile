# SyncEngage Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY ./services/syncengage/app /app
COPY ./shared /app/shared
COPY ./schemas /app/schemas
RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings requests grpcio grpcio-tools protobuf prometheus-client opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi httpx tenacity
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
