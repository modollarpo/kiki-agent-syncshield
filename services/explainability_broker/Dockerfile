
FROM python:3.11-slim
WORKDIR /app
COPY ./app /app
RUN pip install --no-cache-dir fastapi uvicorn redis pydantic
EXPOSE 8089
CMD ["python", "main.py"]
