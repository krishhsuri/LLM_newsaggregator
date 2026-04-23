# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
FROM python:3.10-slim

# HuggingFace Spaces requires a non-root user for security
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies before copying the rest of the code for Docker cache
COPY --chown=user requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY --chown=user . /app/

# Expose HuggingFace Spaces port (must be 7860)
EXPOSE 7860

# Command to run the Streamlit application
CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0", "--server.port=7860"]