
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir fastapi uvicorn redis pydantic
EXPOSE 8000
ENV PORT=8000
ENV REDIS_HOST=redis
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
