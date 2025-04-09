FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for GPIO and I2C
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    i2c-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
# Install build dependencies explicitly
RUN pip install --upgrade setuptools>=61.0.0 wheel build
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for the web server
EXPOSE 5000

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "web_server.py"] 