FROM python:3.8-slim-buster

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create storage directory if it does not exist
RUN mkdir -p /app/storage

# Start the application
CMD ["python3", "main.py"]
