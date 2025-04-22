# Use an official lightweight Python image
FROM python:3.10-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8080
ENV GEMINI_KEY AIzaSyCA2xN2qTOFZ9y-A2-GVaIuu_H57NyycRc
ENV MONGO_URI mongodb+srv://rajrishicharan11:THYs2bFFpQDxMnMI@cluster01.nkk4qaf.mongodb.net/NEWAILeveling
# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8080

# Run gunicorn with factory pattern
CMD ["gunicorn", "--factory", "app:create_app", "--bind", "0.0.0.0:${PORT}"]
