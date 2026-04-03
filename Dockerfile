# Use the official lightweight Python image (keeps the image size small!)
FROM python:3.11-slim

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set a default port (Railway will override this dynamically)
ENV PORT=8000 

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (Tesseract OCR for images, and libs for OpenCV/PDFs)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* # ^ Cleaning up the apt cache saves a lot of space!

# Copy ONLY the requirements file first to leverage Docker's caching
COPY requirements.txt .

# Install Python dependencies (Using no-cache-dir to keep the image under 4GB)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files into the container
COPY . .

# Expose the port
EXPOSE $PORT

# Start the FastAPI application
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
