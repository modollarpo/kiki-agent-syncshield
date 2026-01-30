FROM python:3.11-slim
WORKDIR /app
COPY main.py .
COPY ../.. /app
RUN pip install fastapi uvicorn redis pydantic
EXPOSE 8089
CMD ["python", "main.py"]
