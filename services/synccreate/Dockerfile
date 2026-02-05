# SyncCreate Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY ./services/synccreate/app /app
COPY ./services/synccreate/logic /app/logic
COPY ./shared /app/shared
COPY ./schemas /app/schemas
RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings requests httpx grpcio grpcio-tools protobuf prometheus-client opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi tenacity
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
