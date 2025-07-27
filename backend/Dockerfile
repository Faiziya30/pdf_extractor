# Dockerfile
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system-level dependencies (if needed for PyMuPDF)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy all code
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Create input/output folders
RUN mkdir -p /app/input /app/output

# Run the extractor
CMD ["python", "run_extractor.py"]
