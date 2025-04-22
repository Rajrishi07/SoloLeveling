# Use a slim Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy all project files
COPY . .

# Expose the port (Railway uses 8000 by default for Docker)
EXPOSE 8000

# Run with gunicorn using factory pattern
CMD ["gunicorn", "app:create_app()", "--bind", "0.0.0.0:8000"]
