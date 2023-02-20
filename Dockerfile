# syntax=docker/dockerfile:1
# app/Dockerfile

FROM python:3.10.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# RUN git clone https://github.com/streamlit/streamlit-example.git .

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY src/network/* ./network/

COPY src/* .

# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["python", "claim_ftso_rewards.py"]