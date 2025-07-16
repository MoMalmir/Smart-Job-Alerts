# Use official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole project
COPY . .

# Set environment variables if desired (can be overridden by --env-file)
ENV PYTHONUNBUFFERED=1

# Entry command
CMD ["python", "main.py"]
