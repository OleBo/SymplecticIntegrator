#!/bin/bash

# Docker build script for Symplectic Integrator
# Usage: ./scripts/docker-build.sh [tag]

set -e

TAG="${1:-latest}"
DOCKERFILE="${2:-Dockerfile}"

echo "🐳 Building Symplectic Integrator Docker Image"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Tag: $TAG"
echo "Dockerfile: $DOCKERFILE"
echo ""

docker build -t "symplectic-integrator:$TAG" -f "$DOCKERFILE" .

echo ""
echo "✓ Build complete!"
echo ""
echo "Run container:"
echo "  docker run -it symplectic-integrator:$TAG bash"
echo ""
echo "Run GPU benchmark:"
echo "  docker run --gpus all symplectic-integrator:$TAG /bin/bash -c './build/example'"
echo ""
echo "View image size:"
echo "  docker images | grep symplectic-integrator"
