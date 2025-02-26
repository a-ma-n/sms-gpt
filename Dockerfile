# Use an official Ubuntu base image
FROM ubuntu:20.04

# Set non-interactive mode for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
RUN apt-get update && \
    apt-get install -y curl python3 python3-pip ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set working directory
WORKDIR /app

# Start Ollama service in the background & pull model
RUN ollama serve & sleep 5 && ollama pull deepseek-r1:1.5b

# Copy app files
COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 8000

# Start Ollama & FastAPI server
CMD ollama serve & uvicorn app:app --host 0.0.0.0 --port 8000
