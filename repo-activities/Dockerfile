FROM python:3.12-slim

WORKDIR /app

RUN pip install -U pip uv

RUN apt-get update && \
    apt-get install -y git build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

RUN uv pip install --system -r requirements.txt