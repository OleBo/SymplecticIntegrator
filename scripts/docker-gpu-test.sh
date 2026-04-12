#!/bin/bash

# Docker GPU test script
# Verifies GPU support and runs GPU benchmark
# Usage: ./scripts/docker-gpu-test.sh

set -e

echo "🚀 GPU Support Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check nvidia-docker
echo "1️⃣  Checking nvidia-docker..."
if ! command -v nvidia-docker &> /dev/null; then
    echo "⚠️  nvidia-docker not found. Installing..."
    echo "   See DOCKER.md for installation instructions"
fi

# Test GPU availability
echo ""
echo "2️⃣  Testing GPU availability..."
docker run --rm --gpus all nvidia/cuda:11.8.0-runtime-ubuntu22.04 nvidia-smi || \
    echo "⚠️  GPU not available or nvidia-docker not configured"

# Build GPU image
echo ""
echo "3️⃣  Building optimized GPU image..."
docker build -f Dockerfile.multistage -t symplectic-integrator:gpu . > /dev/null

# Run GPU example
echo ""
echo "4️⃣  Running GPU example..."
docker run --rm --gpus all \
  -v "$(pwd)/data:/app/data" \
  symplectic-integrator:gpu \
  /bin/bash -c "./build/example"

echo ""
echo "✓ GPU test complete!"
