
FROM python:3.11-slim
WORKDIR /app
COPY ./services/explainability_broker /app
COPY ./shared /app/shared
COPY ./schemas /app/schemas
RUN pip install --no-cache-dir fastapi uvicorn redis pydantic pydantic-settings grpcio grpcio-tools protobuf requests httpx tenacity prometheus-client opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi
EXPOSE 8000
ENV PORT=8000
ENV REDIS_HOST=redis
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
