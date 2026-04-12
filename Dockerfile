# Use NVIDIA CUDA base image with cuDNN
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Set working directory
WORKDIR /app

# Install build essentials and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    wget \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Create Python virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the entire project
COPY . .

# Build the project
RUN mkdir -p build && \
    cd build && \
    cmake .. && \
    make -j$(nproc)

# Add src/cpu to Python path
ENV PYTHONPATH="/app/src/cpu:$PYTHONPATH"

# Set the entrypoint to bash for flexibility
ENTRYPOINT ["/bin/bash"]

# Default command
CMD ["-c", "python benchmark.py"]
