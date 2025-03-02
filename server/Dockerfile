FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY server/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ .

# Expose port
EXPOSE 8000

# Run command
CMD ["python", "main.py"]