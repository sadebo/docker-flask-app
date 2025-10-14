FROM python:3.10-slim

WORKDIR /app
COPY serve.py /app/

RUN pip install --upgrade pip && \
    pip install vllm==0.4.2 fastapi uvicorn prometheus-client

ENV MODEL_NAME=facebook/opt-125m

EXPOSE 8000 9090
ENTRYPOINT ["python", "serve.py"]
