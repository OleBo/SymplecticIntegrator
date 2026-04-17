---
title: Quick Reference
nav_order: 43
---

# Docker Quick Reference Card

## 🐳 Essential Commands

### Build
```bash
# Standard build
docker build -t symplectic-integrator .

# Optimized multi-stage build
docker build -f Dockerfile.multistage -t symplectic-integrator:slim .

# With specific tag
docker build -t symplectic-integrator:v1.0 .

# Using helper script
./scripts/docker-build.sh latest
```

### Run
```bash
# Basic run
docker run symplectic-integrator

# Interactive bash
docker run -it symplectic-integrator bash

# With GPU
docker run --gpus all symplectic-integrator

# With volume mounts
docker run -v $(pwd)/data:/app/data symplectic-integrator

# Mount both data and notebooks
docker run -it \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/notebooks:/app/notebooks \
  symplectic-integrator bash

# Using helper script
./scripts/docker-run.sh "python src/cpu/benchmark.py"
```

## 🔧 Docker Compose

### Services
```bash
# CPU benchmark
docker-compose run symplectic-cpu bash

# GPU version
docker-compose run symplectic-gpu bash

# Jupyter notebook
docker-compose up notebook
# Open http://localhost:8888

# All services
docker-compose up

# Stop all
docker-compose down
```

## 🚀 Common Workflows

### Run Benchmark
```bash
# Option 1: Direct docker
docker run symplectic-integrator python src/cpu/benchmark.py

# Option 2: Compose
docker-compose run symplectic-cpu python src/cpu/benchmark.py

# Option 3: Helper script
./scripts/docker-run.sh "python src/cpu/benchmark.py"
```

### GPU Testing
```bash
# Test GPU support
./scripts/docker-gpu-test.sh

# Run GPU example
docker run --gpus all symplectic-integrator ./build/example

# Check CUDA version
docker run --gpus all symplectic-integrator nvcc --version
```

### Development
```bash
# Interactive development
docker run -it \
  -v $(pwd):/app \
  symplectic-integrator \
  bash

# Run tests
docker run symplectic-integrator pytest

# Run with specific Python version
docker build -t symplectic:py311 \
  --build-arg PYTHON_VERSION=3.11 .
```

## 🧹 Maintenance

### Images
```bash
# List images
docker images | grep symplectic

# Remove image
docker rmi symplectic-integrator:latest

# Remove all symplectic images
docker-compose down
./scripts/docker-clean.sh
```

### Containers
```bash
# List running
docker ps

# List all
docker ps -a

# Stop container
docker stop <container-id>

# Remove container
docker rm <container-id>

# Cleanup all
docker container prune
```

### Space
```bash
# Check disk usage
docker system df

# Remove unused images
docker image prune -a

# Full cleanup
docker system prune -a
```

## 📊 Monitoring

### Resource Usage
```bash
# Real-time stats
docker stats

# Specific container
docker stats <container-id>

# Log output
docker logs <container-id>
docker logs -f <container-id>
```

### Inspect
```bash
# Image info
docker inspect symplectic-integrator

# Image history
docker history symplectic-integrator

# Image layers
docker inspect --format='{{.RootFS.Layers}}' symplectic-integrator | tr ',' '\n'
```

## 🔌 Advanced

### Environment Variables
```bash
# Pass environment variables
docker run -e VAR=value symplectic-integrator

# From file
docker run --env-file .env.docker symplectic-integrator
```

### Build Arguments
```bash
# Custom CUDA version
docker build \
  --build-arg CUDA_VERSION=12.0 \
  -t symplectic-integrator .

# Custom Python version
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t symplectic-integrator .
```

### Network
```bash
# Port mapping
docker run -p 8888:8888 symplectic-integrator

# Custom network
docker network create symplectic-net
docker run --network symplectic-net symplectic-integrator
```

## 🆘 Troubleshooting

### GPU Issues
```bash
# Verify nvidia-docker
which nvidia-docker

# Test GPU
nvidia-docker run --rm nvidia/cuda nvidia-smi

# Check docker-gpu plugin
docker run --rm --gpus all ubuntu nvidia-smi
```

### Build Issues
```bash
# Clear build cache
docker build --no-cache -t symplectic-integrator .

# Check Dockerfile
docker build --progress=plain -t symplectic-integrator .

# Verbose output
docker build -t symplectic-integrator . -v
```

### Runtime Issues
```bash
# Check logs
docker logs <container-id>

# Interactive debugging
docker run -it symplectic-integrator bash

# Check resource limits
docker stats

# Increase memory
docker run -m 8g symplectic-integrator
```

## 📈 Performance Tips

### Build Optimization
```bash
# Use docker buildx
docker buildx build --platform linux/amd64,linux/arm64 .

# Multi-stage (already in use)
docker build -f Dockerfile.multistage .

# Cache layers
docker build --cache-from symplectic-integrator:latest .
```

### Runtime Optimization
```bash
# Use runsc (gVisor)
docker run --runtime=runsc symplectic-integrator

# Limit resources
docker run -m 4g --cpus=2 symplectic-integrator

# CPU affinity
docker run --cpuset-cpus="0,1" symplectic-integrator
```

## 🌐 Distribution

### Docker Hub
```bash
# Login
docker login

# Tag
docker tag symplectic-integrator myuser/symplectic-integrator

# Push
docker push myuser/symplectic-integrator

# Pull
docker pull myuser/symplectic-integrator
```

### Private Registry
```bash
# Tag
docker tag symplectic-integrator myregistry.azurecr.io/symplectic

# Push
docker push myregistry.azurecr.io/symplectic

# Pull
docker pull myregistry.azurecr.io/symplectic
```

## 📋 Checklists

### Pre-deployment
- [ ] Image builds without errors
- [ ] GPU test passes
- [ ] Data mounts correctly
- [ ] Notebooks run in container
- [ ] Benchmarks produce expected output
- [ ] Image size is reasonable (<5GB)
- [ ] All dependencies are pinned
- [ ] Documentation is complete

### Before Production
- [ ] Security scan: `docker scan symplectic-integrator`
- [ ] Image tested on target hardware
- [ ] Resource limits defined
- [ ] Logging configured
- [ ] Monitoring configured
- [ ] Backup strategy planned
- [ ] Release notes prepared

---

**For detailed documentation, see [DOCKER.md](DOCKER.md)**
