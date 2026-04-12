<!-- Custom instructions for GPU-Accelerated Symplectic Integrator -->

## Project Setup Checklist

- [x] Create project structure and directories
- [x] Implement CPU baseline integrators (Euler, RK4, Symplectic)
- [x] Create GPU CUDA kernels for parallel simulation
- [x] Build energy tracking and visualization infrastructure
- [x] Set up analysis notebooks and experiments
- [x] Document project architecture and usage
- [x] Complete

## Project Guidelines

**Project Type:** GPU-accelerated scientific computing with CUDA/C++/Python

**Key Components:**
- CPU baseline implementations (Python): Euler, RK4, Leapfrog/Velocity Verlet
- GPU CUDA implementation: Parallel trajectory simulation
- Henon-Heiles Hamiltonian system as test case
- Energy preservation metrics and visualization
- Performance benchmarking tools

**Key Technologies:**
- CUDA Toolkit for GPU programming
- CMake for build system
- NumPy/SciPy for CPU baseline
- Matplotlib for visualization
- Jupyter for analysis notebooks
