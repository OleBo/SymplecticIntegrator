---
title: Architecture & Implementation
nav_order: 5
---

# Project Architecture & Implementation Guide

## Overview

GPU-Accelerated Symplectic Integrator demonstrates:
- Mathematical rigor in numerical integration
- Structure-preserving algorithms for Hamiltonian systems
- GPU parallelization of embarrassingly-parallel workloads
- Long-term energy conservation in chaotic systems

**Target audience:** NVIDIA-level research teams, quantitative researchers, HPC specialists

---

## Mathematical Foundation

### Core Problem

Integrate Hamilton's equations:
$$\frac{d\mathbf{q}}{dt} = \frac{\partial H}{\partial \mathbf{p}}, \quad \frac{d\mathbf{p}}{dt} = -\frac{\partial H}{\partial \mathbf{q}}$$

Key property: These preserve the **symplectic structure** — an invariant volume element in phase space.

### Why This Matters

Most numerical methods do NOT preserve this structure:
- **Euler**: Violates symplectic structure → energy explodes
- **RK4**: Violates symplectic structure → energy drifts linearly
- **Symplectic (Leapfrog)**: PRESERVES structure → bounded energy error

The difference between these is **not** just simulation accuracy—it's about preserving fundamental mathematical properties of the system.

### The Test System: Hénon-Heiles

$$H(x,y,p_x,p_y) = \frac{1}{2}(p_x^2 + p_y^2) + \frac{1}{2}(x^2 + y^2) + x^2y - \frac{1}{3}y^3$$

Properties:
- **Chaotic** for $E > 1/6 \approx 0.167$
- **Nonlinear** → exponential divergence of nearby trajectories
- **Integrable** for low energies → predictable orbits
- **Hard to simulate** → small errors accumulate catastrophically

Perfect test case for demonstrating structure preservation.

---

## Software Architecture

### Layer 1: Core Mathematical Definitions

**File:** `include/henon_heiles.h`

```cpp
struct State4D {
    float x, y, px, py;
};

__host__ __device__ inline float compute_energy(float x, float y, float px, float py);
__host__ __device__ inline void compute_gradients(float x, float y, float& grad_x, float& grad_y);
```

**Key Design:**
- `__host__ __device__` functions → works on both CPU and GPU
- Inline → no function call overhead in tight loops
- Minimal state structure → minimal memory bandwidth

### Layer 2: Integrator API

**Files:** 
- `include/integrators.h` (declarations)
- `src/gpu/integrators.cu` (GPU kernels)
- `src/cpu/integrators.py` (CPU reference)

Three integrator classes:

#### 1. Euler Integrator
```python
class EulerIntegrator(BaseIntegrator):
    def integrate(self, state, dt, steps):
        for n in range(steps):
            grad_x, grad_y = henon_heiles_gradients(state.x, state.y)
            state.x += dt * state.px
            state.y += dt * state.py
            state.px -= dt * grad_x
            state.py -= dt * grad_y
        return state
```

**Characteristics:**
- Simple, naive
- Non-symplectic
- Energy explodes

#### 2. RK4 Integrator
```python
class RK4Integrator(BaseIntegrator):
    def integrate(self, state, dt, steps):
        for n in range(steps):
            # 4 stages of RK4...
            # Evaluate k1, k2, k3, k4
            # Combine with weights 1/6, 2/6, 2/6, 1/6
        return state
```

**Characteristics:**
- Fourth-order accurate
- General-purpose (works for any ODE)
- Non-symplectic
- Energy drifts linearly

#### 3. Symplectic (Leapfrog) Integrator
```python
class SymplecticIntegrator(BaseIntegrator):
    def integrate(self, state, dt, steps):
        for n in range(steps):
            grad_x, grad_y = henon_heiles_gradients(state.x, state.y)
            state.px -= 0.5 * dt * grad_x
            state.py -= 0.5 * dt * grad_y
            state.x += dt * state.px
            state.y += dt * state.py
            grad_x, grad_y = henon_heiles_gradients(state.x, state.y)
            state.px -= 0.5 * dt * grad_x
            state.py -= 0.5 * dt * grad_y
        return state
```

**Characteristics:**
- Staggered/interleaved updates
- Symplectic structure preserving
- Second-order accurate
- Energy bounded over long times

### Layer 3: Analysis Infrastructure

**Files:**
- `src/cpu/analysis.py` → Energy tracking and visualization

```python
class EnergyAnalysis:
    def add_result(self, method_name, energies_history, times):
        # Store results
    
    def compute_statistics(self, method_name):
        # Compute max error, mean error, etc.
    
    def plot_energy_drift(self, output_path):
        # Generate comparison plots
    
    def print_summary(self):
        # Print statistics table
```

### Layer 4: GPU Implementation

**File:** `src/gpu/integrators.cu`

**Kernel structure:**

```cuda
__global__ void symplectic_kernel(
    float* x, float* y,      // Position arrays
    float* px, float* py,    // Momentum arrays
    int n,                   // Number of trajectories
    float dt,                // Timestep
    int steps) {             // Integration steps
    
    // Each thread processes one trajectory
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    
    // Load trajectory into registers
    float xi = x[i];
    float yi = y[i];
    float pxi = px[i];
    float pyi = py[i];
    
    // Integrate all steps
    for (int t = 0; t < steps; ++t) {
        // Compute gradients (arithmetic on registers only)
        float grad_x = xi + 2*xi*yi;
        float grad_y = yi + xi*xi - yi*yi;
        
        // Symplectic update (all in registers)
        pxi -= 0.5f * dt * grad_x;
        pyi -= 0.5f * dt * grad_y;
        xi += dt * pxi;
        yi += dt * pyi;
        grad_x = xi + 2*xi*yi;
        grad_y = yi + xi*xi - yi*yi;
        pxi -= 0.5f * dt * grad_x;
        pyi -= 0.5f * dt * grad_y;
    }
    
    // Write results back
    x[i] = xi;
    y[i] = yi;
    px[i] = pxi;
    py[i] = pyi;
}
```

**GPU Optimization Techniques:**

1. **Data Locality**: All trajectory data in registers
   - No shared memory needed
   - Perfect memory coalescing (each thread writes to consecutive memory)
   - Minimal register pressure

2. **Work Partitioning**: One trajectory per thread
   - Perfect load balancing
   - No synchronization needed
   - Scales transparently with GPU count

3. **Arithmetic Density**: 4 operations per memory access
   - Good compute-to-bandwidth ratio
   - Hides memory latency well

---

## Data Flow

### CPU Benchmark

```
┌─────────────────────────┐
│ Create Initial Ensemble │
│  (random in chaos)      │
└────────────┬────────────┘
             │
             ├──→ EulerIntegrator ─┐
             │                     ├─→ EnergyAnalysis ─→ Plots
             ├─→ RK4Integrator ───┤
             │                     │
             └─→ SymplecticIntegrator ┘
                  │
                  └─→ Write results to data/
```

### GPU Execution

```
Host                           Device
───────────────────────────────────────────
Initial states                 Allocate GPU memory
     │                              │
     ├─→ cudaMemcpy ─────────────→ GPU buffers
     │
     └─→ Launch kernel
          │
          └────────────────────→ 1000s of threads
                                 each integrate 1 trajectory
                                 │
                         ┌───────┴────────┐
                         │                │
                    Symplectic_kernel   Energy_kernel
                         │                │
          ←──────────────┴────────────────┘
          
     Results from GPU
     │
     ├─ cudaMemcpy ←────────────────
     │
     └─→ Analyze/visualize
```

---

## Performance Characteristics

### CPU Baseline

**Throughput:**
- 100 trajectories × 10,000 steps = 1,000,000 trajectory-steps
- Typical time: 1-5 seconds
- Throughput: ~10⁷ steps/sec

**Limitation:** Sequential execution on single core

### GPU

**Theoretical Peak:**
- GPU with 2000 CUDA cores
- 1000 trajectories × 100,000 steps = 10⁸ trajectory-steps
- Estimated time: <100ms
- Throughput: ~10¹⁰ steps/sec

**Expected speedup: 100-1000x**

### Why This Scaling

1. **Embarrassingly parallel**: No inter-trajectory communication
2. **High arithmetic intensity**: 4 FLOPs per memory access
3. **Predictable memory access**: Sequential writes enable coalescing
4. **Scalable work**: More trajectories = more GPU utilization

---

## Build System

### CPU Baseline
```bash
cd src/cpu
python -m pip install -r ../../requirements.txt
python benchmark.py
```

No compilation needed—pure Python.

### GPU Build
```bash
mkdir build && cd build
cmake ..
make
```

**CMakeLists.txt structure:**
```cmake
find_package(CUDA REQUIRED)
add_library(symplectic_gpu SHARED src/gpu/integrators.cu)
set_target_properties(symplectic_gpu PROPERTIES CUDA_SEPARABLE_COMPILATION ON)
set_target_compile_options(symplectic_gpu PRIVATE -O3 -arch=sm_70)
```

**Key settings:**
- `CUDA_SEPARABLE_COMPILATION` → allows device linking
- `-arch=sm_70` → target compute capability 7.0+ (V100/A100/RTX)
- `-O3` → aggressive optimization

---

## Testing Strategy

### Unit Tests (not yet implemented)
```cpp
TEST(EnergyConservation, SymplecticPreserves) {
    // Integrate one step
    // Check energy error < 1e-6
}

TEST(IntegratorBounds, SymplecticFinalStateValid) {
    // Check final state in reasonable bounds
}
```

### Integration Tests (CPU benchmark)
```bash
python src/cpu/benchmark.py
# Check:
# 1. Symplectic max error < Euler/RK4
# 2. Symplectic energy bounded over time
# 3. All methods produce physical results
```

### Performance Tests (GPU)
```bash
nvprof ./build/symplectic_gpu_example
# Check:
# 1. Kernel launch overhead < 1%
# 2. Memory bandwidth utilization > 50%
# 3. No kernel divergence or shared memory conflicts
```

---

## Extension Ideas

### Short-term (1-2 weeks)
- [ ] Adaptive timestep (detect instability)
- [ ] Mixed precision (FP32 positions, FP64 energy)
- [ ] Poincaré section visualization

### Medium-term (1 month)
- [ ] Higher-order symplectic integrators (6th order)
- [ ] Other Hamiltonian systems (3D oscillators, particle chains)
- [ ] Hybrid CPU/GPU execution

### Long-term (1+ months)
- [ ] Molecular dynamics acceleration (real application)
- [ ] Portfolio simulation (financial application)
- [ ] Quantum dynamics (phase space WKB methods)

---

## Key Files Reference

| File | Purpose | Language |
|------|---------|----------|
| `src/cpu/integrators.py` | Three integrator implementations | Python |
| `src/cpu/analysis.py` | Energy analysis and visualization | Python |
| `src/cpu/benchmark.py` | CPU benchmark driver | Python |
| `src/gpu/integrators.cu` | GPU kernels | CUDA C++ |
| `include/henon_heiles.h` | System definitions (dual CPU/GPU) | C++ |
| `include/integrators.h` | Integrator API | C++ |
| `CMakeLists.txt` | Build configuration | CMake |
| `notebooks/01_cpu_benchmark.ipynb` | Interactive analysis | Jupyter |

---

## Development Tips

### Debug Energy Conservation

```python
from src.cpu import SymplecticIntegrator
integrator = SymplecticIntegrator()
state = create_initial_condition(1)[0]
final = integrator.integrate(state, dt=1e-3, steps=100)
print(integrator.energies)  # Check if energy stays constant
```

### Profile GPU Execution

```bash
nvprof --print-gpu-trace ./build/symplectic_gpu_benchmark
```

### Test Different Hamiltonians

Modify `henon_heiles_gradients()` in `src/cpu/integrators.py`:

```python
def henon_heiles_gradients(x, y):
    # Current: Hénon-Heiles
    grad_x = x + 2*x*y
    grad_y = y + x**2 - y**2
    
    # Alternative: Coupled oscillators
    # grad_x = x
    # grad_y = y
```

---

**This architecture enables clear separation between mathematical correctness (CPU) and computational performance (GPU), making it easy to validate, optimize, and extend.**
