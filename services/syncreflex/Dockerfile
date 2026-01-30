FROM bitnami/python:3.10
WORKDIR /app
COPY ./app /app
RUN pip install fastapi uvicorn pydantic
CMD ["python", "main.py"]
