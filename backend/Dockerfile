# Dockerfile
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your main Python script
COPY pdf_extractor.py .

# Create input/output folders
RUN mkdir -p /app/input /app/output

# Define default run command
CMD ["python", "pdf_extractor.py"]
