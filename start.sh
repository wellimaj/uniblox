#!/bin/bash

if [ -S /var/run/docker.sock ] && [ -z "$DOCKER_HOST" ]; then
    export DOCKER_HOST=unix:///var/run/docker.sock
fi

if [ "$1" == "clean" ] || [ "$1" == "down" ]; then
    echo "Cleaning up containers and volumes..."
    docker-compose down -v 2>/dev/null || docker compose down -v 2>/dev/null
    echo "Cleanup complete."
    exit 0
fi

if [ "$1" == "restart" ]; then
    echo "Restarting services..."
    docker-compose restart 2>/dev/null || docker compose restart 2>/dev/null
    echo "Services restarted."
    echo ""
    echo "View logs with: docker-compose logs -f"
    exit 0
fi

if [ "$1" == "stop" ]; then
    echo "Stopping services..."
    docker-compose stop 2>/dev/null || docker compose stop 2>/dev/null
    echo "Services stopped."
    exit 0
fi

echo "Starting Ecommerce Store..."

if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker daemon is not running."
    echo ""
    echo "Please start Docker:"
    echo "  - Docker Desktop: Open Docker Desktop application"
    echo "  - Docker service (Linux): sudo systemctl start docker"
    echo ""
    echo "After starting Docker, run this script again."
    exit 1
fi

echo "Docker is running. Building and starting all services..."
echo ""

if command -v docker-compose &> /dev/null; then
    docker-compose up --build
elif docker compose version &> /dev/null; then
    docker compose up --build
else
    echo "Error: docker-compose not found. Please install Docker Compose."
    exit 1
fi

