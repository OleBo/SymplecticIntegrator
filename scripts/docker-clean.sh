#!/bin/bash

# Docker cleanup script
# Removes all symplectic-integrator images and containers
# Usage: ./scripts/docker-clean.sh

set -e

echo "🧹 Cleaning Docker Resources"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Stop and remove containers
echo "Stopping containers..."
docker-compose down -v 2>/dev/null || true

# Remove images
echo "Removing images..."
docker rmi -f \
  symplectic-integrator:latest \
  symplectic-integrator:gpu \
  symplectic-integrator:optimized \
  2>/dev/null || true

# Clean build artifacts
echo "Removing build artifacts..."
rm -rf build/

echo ""
echo "✓ Cleanup complete!"
echo ""
echo "To rebuild:"
echo "  ./scripts/docker-build.sh latest"
