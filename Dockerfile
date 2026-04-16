# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (build-essential needed for some python packages like chromadb/torch)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies before copying the rest of the code for Docker cache
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the current directory contents into the container
COPY . /app/

# Expose Streamlit port
EXPOSE 8501

# Command to run the application (we will use this for the streamlit app)
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
