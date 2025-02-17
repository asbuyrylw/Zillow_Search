# Use the official Python 3.9 image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the FastAPI app code to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install -r requirements.txt

# Expose port 8000 for FastAPI
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
