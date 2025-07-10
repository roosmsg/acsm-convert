# Base image with libgourou and de-DRM tools (Alpine-based)
FROM bcliang/docker-libgourou:latest

# Install Docker CLI so dedrm.sh can launch internal containers
# Add Python, Flask, and SSL certificates
RUN apk add --no-cache \
      docker-cli \
      python3 \
      py3-pip \
      py3-flask \
      ca-certificates \
 && update-ca-certificates

# Set the working directory for our Flask app
WORKDIR /app

# Copy the Flask application into the container
COPY app.py /app/app.py

# Create the directory for uploads and conversion files
RUN mkdir -p /home/libgourou/files

# Set environment variables so Flask listens on 0.0.0.0
ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0

# Expose port 5000 for access from the host
EXPOSE 5000

# Start Flask (development server)
ENTRYPOINT ["flask", "run"]

# At runtime, you must use the following bind-mounts:
#  - /var/run/docker.sock:/var/run/docker.sock   (to allow internal Docker calls)
#  - ~/acsm-data/adept:/home/libgourou/.adept     (your ADEPT keys)
#  - ~/acsm-data/uploads:/home/libgourou/files    (your ACSM files and output)
