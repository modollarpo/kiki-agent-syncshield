# SyncValue Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY ./services/syncvalue/app /app
COPY ./shared /app/shared
COPY ./schemas /app/schemas
RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings scikit-learn grpcio grpcio-tools protobuf passlib pyjwt fastapi-limiter redis prometheus-client opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi tenacity httpx && \
    pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
