# Use a slim Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by PyMuPDF
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual Python script
COPY pdf_extractor.py .

# Create input/output folders inside container
RUN mkdir -p /app/input /app/output

# Set default command to run the extractor
CMD ["python", "pdf_extractor.py"]
