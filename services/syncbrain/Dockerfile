# SyncBrain Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY ./services/syncbrain/app /app
COPY ./shared /app/shared
COPY ./schemas /app/schemas
RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings openai grpcio grpcio-tools protobuf passlib httpx PyJWT fastapi-limiter prometheus-client opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi redis
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
