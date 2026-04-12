# Docker Setup Guide

## Overview

This project includes Docker configurations for:
- **Development**: Full environment with all build tools
- **Production**: Optimized multi-stage build (smaller image)
- **Jupyter**: Interactive notebook environment
- **GPU Support**: NVIDIA GPU acceleration via Docker Compose

---

## Quick Start

### Option 1: Using Docker Compose (Recommended)

#### CPU-only benchmark:
```bash
docker-compose run symplectic-cpu bash
cd src/cpu
python benchmark.py
```

#### GPU version (requires nvidia-docker):
```bash
docker-compose run symplectic-gpu bash
cd build
./example  # Run GPU example
```

#### Interactive Jupyter notebook:
```bash
docker-compose up notebook
# Open http://localhost:8888 in browser
```

---

### Option 2: Direct Docker Build

#### Simple build:
```bash
docker build -t symplectic-integrator .
```

#### Multi-stage optimized build:
```bash
docker build -f Dockerfile.multistage -t symplectic-integrator:optimized .
```

#### Run container:
```bash
docker run -it --rm symplectic-integrator /bin/bash
```

#### With GPU support (requires nvidia-docker):
```bash
docker run -it --rm --gpus all symplectic-integrator /bin/bash
```

#### Mount data directory:
```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  symplectic-integrator /bin/bash
```

---

## GPU Support Setup

### Prerequisites

1. **NVIDIA GPU** (tested on V100, A100, RTX series)
2. **NVIDIA Docker Runtime**

### Install nvidia-docker

**Ubuntu/Debian:**
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

**macOS with Docker Desktop:**
GPU support is automatic through Docker Desktop 4.6+

### Verify GPU Setup

```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-runtime-ubuntu22.04 nvidia-smi
```

Should show GPU information.

---

## Docker Compose Services

### `symplectic-cpu`
- Full development environment
- Includes build tools and Python
- CPU-only (no GPU needed)
- For development and testing

### `symplectic-gpu`
- Optimized for GPU execution
- Has nvidia-docker GPU support
- Use for performance benchmarking
- Requires compatible GPU

### `notebook`
- Jupyter notebook server
- Port 8888 (localhost)
- Real-time analysis and visualization
- Pre-configured with Matplotlib

---

## Image Sizes

| Image | Size | Notes |
|-------|------|-------|
| Development | ~4 GB | Full build tools included |
| Optimized | ~2 GB | Multi-stage, runtime only |
| Base CUDA | ~1 GB | nvidia/cuda base image |

---

## Common Commands

### Build
```bash
# Simple build
docker build -t symplectic-integrator .

# Multi-stage build (smaller)
docker build -f Dockerfile.multistage -t symplectic-integrator:slim .

# With build args
docker build --build-arg CUDA_VERSION=12.0 -t symplectic-integrator .
```

### Run
```bash
# Interactive shell
docker run -it symplectic-integrator bash

# Run benchmark
docker run symplectic-integrator python src/cpu/benchmark.py

# With volume mount
docker run -v ~/data:/app/data symplectic-integrator bash

# With GPU
docker run --gpus all symplectic-integrator bash
```

### Compose
```bash
# Start all services
docker-compose up

# Run single service
docker-compose run symplectic-cpu bash

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

### Clean up
```bash
# Remove images
docker rmi symplectic-integrator

# Remove containers
docker-compose down -v

# Remove all unused images
docker image prune -a
```

---

## Troubleshooting

### GPU Not Detected
```bash
# Check nvidia-docker installation
nvidia-docker run --rm nvidia/cuda nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda nvidia-smi

# Verify compose GPU config
docker-compose exec symplectic-gpu nvidia-smi
```

### Out of Memory
- Reduce trajectory count: `python benchmark.py 100 1000`
- Use GPU: GPU has more VRAM than CPU
- Check: `docker stats`

### Build Failures
- Check CUDA version compatibility
- Verify nvidia/cuda image availability
- Check disk space: `docker system df`

### Permission Issues
```bash
# Run as specific user
docker run --user $(id -u):$(id -g) symplectic-integrator bash

# Fix volume mount permissions
sudo chown -R $USER:$USER ./data
```

---

## Kubernetes Deployment (Optional)

### Create deployment YAML:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: symplectic-integrator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: symplectic
  template:
    metadata:
      labels:
        app: symplectic
    spec:
      containers:
      - name: symplectic
        image: symplectic-integrator:gpu
        resources:
          limits:
            nvidia.com/gpu: 1
      nodeSelector:
        accelerator: nvidia-tesla
```

### Deploy:
```bash
kubectl apply -f deployment.yaml
kubectl logs -f deployment/symplectic-integrator
```

---

## CI/CD Integration

### GitHub Actions Example:
```yaml
name: Docker Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: docker/build-push-action@v2
        with:
          file: ./Dockerfile
          tags: symplectic-integrator:${{ github.sha }}
```

---

## Production Considerations

### Security
- Use specific version tags (not `latest`)
- Scan images: `docker scan symplectic-integrator`
- Use read-only filesystem if possible
- Run as non-root user

### Performance
- Use multi-stage builds
- Cache layer optimization
- Pin base image versions
- Use `.dockerignore`

### Monitoring
```bash
# Monitor resource usage
docker stats

# Check image layers
docker history symplectic-integrator

# Inspect image
docker inspect symplectic-integrator
```

---

## Advanced: Custom Build Args

Add to Dockerfile:
```dockerfile
ARG CUDA_VERSION=11.8.0
ARG UBUNTU_VERSION=22.04
ARG PYTHON_VERSION=3.10

FROM nvidia/cuda:${CUDA_VERSION}-runtime-ubuntu${UBUNTU_VERSION}
...
```

Build with custom versions:
```bash
docker build \
  --build-arg CUDA_VERSION=12.0 \
  --build-arg PYTHON_VERSION=3.11 \
  -t symplectic-integrator:custom .
```

---

## Resources

- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [Docker Documentation](https://docs.docker.com)
- [nvidia/cuda Base Images](https://hub.docker.com/r/nvidia/cuda)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

---

**Ready to containerize! 🐳**
