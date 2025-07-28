FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Download NLTK data after nltk is installed
RUN python -m nltk.downloader punkt

# Copy your Python files
COPY pdf_extractor.py .
COPY test_validation.py .

# Create input/output folders
RUN mkdir -p /app/input /app/output

# Set default command
CMD ["python", "pdf_extractor.py"]
