# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# yt-dlp needs nodejs for bot protection challenges
# ffmpeg is needed for audio/video processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    nodejs \
    npm \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements_api.txt /app/

# Install any needed packages specified in requirements_api.txt
RUN pip install --no-cache-dir -r requirements_api.txt

# Copy the rest of the application code
COPY . /app/

# Expose the port that the app runs on
# Render sets the PORT environment variable
EXPOSE 8000

# Run the application
# Use the PORT environment variable provided by Render, defaulting to 8000
CMD ["sh", "-c", "uvicorn api_transcriber:app --host 0.0.0.0 --port ${PORT:-8000}"]
