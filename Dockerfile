# Multi-architecture base for high performance across x86 and ARM hardware
FROM python:3.10-slim-bullseye

# Set up strict isolated workspace directories inside the system image
WORKDIR /app

# Install native system audio & hardware dependencies for voice-recognition drivers
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy python deployment configuration maps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the core script logic and security modules to internal container storage
COPY main.py .

# Expose global orchestration ports if running as a cloud microservice
ENTRYPOINT ["python", "main.py"]
