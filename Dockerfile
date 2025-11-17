# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PyTorch and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    ca-certificates \
    libffi-dev \
    libgomp1 \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Install fully compatible PyTorch 2.0 CPU packages
RUN pip install --no-cache-dir \
    torch==2.0.0+cpu \
    torchvision==0.15.1+cpu \
    torchaudio==2.0.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Copy requirements.txt and install other Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# COPY requirements.txt requirements-dev.txt ./
# RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt


# Copy the rest of the application
COPY . .

# Expose port and set entrypoint
EXPOSE 5000
CMD ["python", "app.py"]




