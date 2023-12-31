FROM alpine

# Set work directory
WORKDIR /app

# Mount the app volume
VOLUME /app

# Install dependencies
RUN apk add --update --no-cache python3 py3-pip ffmpeg

# Copy the source directory to the container
COPY /src /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Set the entrypoint to run the Python script
CMD ["python3", "main.py"]

# Define the stop signal
STOPSIGNAL SIGINT
