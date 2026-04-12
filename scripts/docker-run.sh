#!/bin/bash

# Docker run script with common options
# Usage: ./scripts/docker-run.sh [command]

set -e

COMMAND="${@:- python src/cpu/benchmark.py}"
IMAGE="symplectic-integrator:latest"
DATA_DIR="$(pwd)/data"
NOTEBOOKS_DIR="$(pwd)/notebooks"

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

echo "🐳 Running Symplectic Integrator in Docker"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Image: $IMAGE"
echo "Command: $COMMAND"
echo "Data volume: $DATA_DIR"
echo ""

docker run -it --rm \
  -v "$DATA_DIR:/app/data" \
  -v "$NOTEBOOKS_DIR:/app/notebooks" \
  "$IMAGE" \
  bash -c "$COMMAND"
