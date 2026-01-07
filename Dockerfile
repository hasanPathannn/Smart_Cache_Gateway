# Use an official lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

ENV PYTHONUNBUFFERED=1
# Install system dependencies (needed for some python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 1. Install CPU-only PyTorch first (Fixes the 888MB download issue)
# We use a long timeout (1000s) just in case
RUN pip install --no-cache-dir --default-timeout=1000 \
    torch --index-url https://download.pytorch.org/whl/cpu

# 2. Copy requirements and install the rest
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# 3. Copy the rest of the app code
COPY . .

# Expose the port
EXPOSE 8000

# Command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]