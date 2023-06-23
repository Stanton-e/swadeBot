FROM debian:bullseye-slim

# Set work directory
WORKDIR /app

# Mount the app volume
VOLUME /app

# Install dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  ffmpeg \
  python3 \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

# Copy the source directory to the container
COPY /src /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Set the entrypoint to run the Python script
CMD ["python3", "main.py"]

# Define the stop signal
STOPSIGNAL SIGINT
