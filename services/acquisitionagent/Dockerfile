
# Acquisition Agent Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY ./services/acquisitionagent/app /app
COPY ./services/acquisitionagent/interfaces /app/interfaces
COPY ./services/acquisitionagent/domain /app/domain
COPY ./services/acquisitionagent/infrastructure /app/infrastructure
COPY ./shared /app/shared
COPY ./schemas /app/schemas
RUN pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings pytest grpcio grpcio-tools protobuf httpx requests tenacity prometheus-client opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
