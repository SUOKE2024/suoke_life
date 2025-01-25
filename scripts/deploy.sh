#!/bin/bash

# Set variables
PROJECT_NAME="suoke_life"
DOCKER_IMAGE_NAME="suoke_life_image"
DOCKER_CONTAINER_NAME="suoke_life_container"
DOCKER_PORT="3000:3000"

# Build Docker image
echo "Building Docker image..."
docker build -t $DOCKER_IMAGE_NAME .

# Stop and remove existing container (if any)
echo "Stopping and removing existing container..."
docker stop $DOCKER_CONTAINER_NAME 2>/dev/null
docker rm $DOCKER_CONTAINER_NAME 2>/dev/null

# Run Docker container
echo "Running Docker container..."
docker run -d --name $DOCKER_CONTAINER_NAME -p $DOCKER_PORT $DOCKER_IMAGE_NAME

echo "Deployment completed!" 