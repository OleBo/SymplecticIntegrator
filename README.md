# 🚀 GPU-Accelerated Symplectic Integrator
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://olebo.github.io/SymplecticIntegrator) 
[![JupyterLite][def]](https://olebo.github.io/symplecticintegrator/lite/index.html)
![Jekyll][def]
[![CI](https://github.com/OleBo/SymplecticIntegrator/actions/workflows/ci.yml/badge.svg)](https://github.com/OleBo/SymplecticIntegrator/actions/workflows/ci.yml)
## Structure-Preserving Simulation on GPUs

**Demonstrating mathematical integrity under GPU parallelization and reduced precision.**

---

## 🎯 Core Concept

This project simulates Hamiltonian systems using a **symplectic integrator** on GPU, showcasing:

✅ **Long-term energy preservation** — Structure-preserving integration survives discretization  
✅ **Massive parallel scaling** — Independent trajectories scale transparently  
✅ **Mathematical rigor over benchmarks** — Shows you understand invariant preservation  

### Why This Matters

Most GPU projects showcase:
- GEMM operations
- CNN kernels

This demonstrates:
> "I understand mathematics that survives discretization and hardware constraints."

That's **rare** and **valuable** to research and AI infrastructure teams (NVIDIA, OpenAI, etc.).

---

## 🔬 Mathematical Foundation

### Hamiltonian Dynamics

The core dynamics:
$$\dot{q} = \frac{\partial H}{\partial p}, \quad \dot{p} = -\frac{\partial H}{\partial q}$$

This preserves the symplectic structure of phase space, meaning:
- Energy $H(q,p)$ is exactly conserved
- Phase space volume is invariant
- Trajectories don't artificially diverge

### Test System: Hénon-Heiles

A classic chaotic Hamiltonian:

$$H(x,y,p_x,p_y) = \frac{1}{2}(p_x^2 + p_y^2) + \frac{1}{2}(x^2 + y^2) + x^2y - \frac{1}{3}y^3$$

Why this one:
- **Nonlinear** → interesting dynamics
- **Chaotic regime** → sensitive to errors
- **Energy matters** → perfect test for structure preservation

---

## ⚙️ Integration Schemes

### 1️⃣ Explicit Euler (Baseline, Bad)
```
q_{n+1} = q_n + dt · p_n
p_{n+1} = p_n - dt · ∇_q H(q_n)
```
❌ Non-symplectic  
❌ Energy explodes rapidly  
✅ Useful as contrast

### 2️⃣ RK4 (Accurate Short-Term, Poor Long-Term)
```
Fourth-order accurate Runge-Kutta
```
✅ Excellent for short times  
❌ Secular energy drift  
❌ Not structure-preserving  

### 3️⃣ Leapfrog/Velocity Verlet (Symplectic, Excellent)
```
p_{n+1/2} = p_n - (dt/2) · ∇_q H(q_n)
q_{n+1}   = q_n + dt · p_{n+1/2}
p_{n+1}   = p_{n+1/2} - (dt/2) · ∇_q H(q_{n+1})
```
✅ Phase space volume preserving  
✅ Stable long-term energy conservation  
✅ Second-order accurate  

**Key insight:** The symplectic structure survives discretization when you respect the staggered updates.

---

## 🧱 System Architecture

### CPU Baseline (Python)

Located in `src/cpu/`:

- **`integrators.py`** — Pure Python implementations of all three schemes
- **`analysis.py`** — Energy conservation analysis and visualization
- **`benchmark.py`** — Compare methods end-to-end

**Why Python baseline?**
- Clear algorithm reference
- Easy visualization and experimentation
- Validates GPU results

### GPU Implementation (CUDA)

Located in `src/gpu/`:

- **`integrators.cu`** — Optimized GPU kernels
- Each CUDA thread = one trajectory
- Embarrassingly parallel structure

**Kernel structure:**
```cuda
__global__ void symplectic_kernel(
    float* x, float* y, float* px, float* py,
    int n, float dt, int steps) {
    
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    
    float xi = x[i];
    float yi = y[i];
    float pxi = px[i];
    float pyi = py[i];
    
    // Each thread integrates one trajectory independently
    for (int t = 0; t < steps; ++t) {
        // Half-step momentum
        float grad_x = xi + 2*xi*yi;
        float grad_y = yi + xi*xi - yi*yi;
        pxi -= 0.5f * dt * grad_x;
        pyi -= 0.5f * dt * grad_y;
        
        // Full-step position
        xi += dt * pxi;
        yi += dt * pyi;
        
        // Recompute and final half-step
        grad_x = xi + 2*xi*yi;
        grad_y = yi + xi*xi - yi*yi;
        pxi -= 0.5f * dt * grad_x;
        pyi -= 0.5f * dt * grad_y;
    }
    
    x[i] = xi;
    y[i] = yi;
    px[i] = pxi;
    py[i] = pyi;
}
```

---

## 🧪 Implementation Plan

### Phase 1: CPU Baseline (✓ Complete)
- [x] Euler implementation
- [x] RK4 implementation
- [x] Symplectic/Leapfrog implementation
- [x] Energy computation and tracking
- [x] Analysis framework

**Output:** Data showing Euler explodes, RK4 drifts, Symplectic is stable

### Phase 2: GPU Kernels (In Progress)
- [ ] CUDA kernel implementations
- [ ] Device memory management
- [ ] Host-device data transfer
- [ ] Kernel optimization (register usage, occupancy)

**Target:** Near-optimal performance on test hardware

### Phase 3: Energy Tracking
- [ ] Compute Hamiltonian energy per trajectory
- [ ] Track drift over time
- [ ] Statistical analysis

**Key metric:** Energy error remains $< 10^{-6}$ over long integrations

### Phase 4: Experiments & Benchmarking
- [ ] 10³-10⁶ parallel trajectories
- [ ] 10⁵-10⁶ timesteps per trajectory
- [ ] CPU vs GPU performance comparison
- [ ] Scaling analysis

**Expected results:**
| Method | Energy Drift | Computational Time |
|--------|--------------|-------------------|
| Euler | Huge ❌ | Potentially fast |
| RK4 | Medium ❌ | Moderate |
| Symplectic | Tiny ✅ | Comparable to RK4 |

---

## 📊 Key Visualizations

### 1. Energy Drift Comparison

Log scale showing:
- Euler: exponential growth
- RK4: linear drift
- Symplectic: bounded oscillation

```
Energy Error (log scale)

^
|     ╱╱╱ Euler (explodes)
|   ╱╱╱╱
| ╱╱ RK4 (drifts)
|╱_____ Symplectic (stable)
|_____________________>  Time
```

### 2. Phase Space Trajectories

Show (x, p_x) and (y, p_y) planes:
- Symplectic: Closed orbits or KAM tori
- Euler: Artificially diverging
- RK4: Gradual expansion

### 3. Ensemble Statistics

Multiple trajectories showing:
- Energy spread over ensemble
- Sensitivity to initial conditions
- Chaotic vs regular behavior

---

## 🚀 Performance Expectations

### CPU Baseline
- 100 trajectories × 10,000 steps: ~1-5 seconds
- Throughput: ~10⁷ steps/sec

### GPU
- 10³ trajectories × 10⁵ steps: <100ms
- Throughput: >10¹⁰ steps/sec
- **Speedup: 100-1000x**

Scaling is excellent because:
1. **Zero data dependency** between trajectories
2. **High arithmetic intensity** (many operations per memory access)
3. **Optimal thread utilization** (no synchronization)

---

## 🧠 What This Signals

### To NVIDIA-level teams:
- ✅ You understand numerical structure preservation
- ✅ You can map mathematics → hardware efficiently
- ✅ You think beyond throughput benchmarks
- ✅ You care about correctness under constraints

### Research angles:
- Mixed precision symplectic (FP32 positions, FP64 energy tracking)
- Adaptive timestep methods detecting instability
- Poincaré sections for chaos analysis

---

## 📁 Directory Structure

```
SymplecticIntegrator/
├── include/                    # Headers
│   ├── henon_heiles.h         # System definitions
│   └── integrators.h          # GPU/CPU kernel declarations
├── src/
│   ├── cpu/                   # Python baseline
│   │   ├── __init__.py
│   │   ├── integrators.py     # All three integrators
│   │   ├── analysis.py        # Visualization & analysis
│   │   └── benchmark.py       # End-to-end benchmark
│   └── gpu/                   # CUDA implementation
│       ├── integrators.cu     # GPU kernels
│       └── example.cpp        # Example usage
├── notebooks/                 # Jupyter analysis
│   ├── 01_cpu_benchmark.ipynb
│   ├── 02_energy_analysis.ipynb
│   └── 03_gpu_comparison.ipynb
├── data/                      # Output directory
├── CMakeLists.txt            # CUDA/C++ build
├── .gitignore
└── README.md
```

---

## 🔧 Building & Running

### CPU Baseline (Python)

```bash
cd src/cpu

# Run benchmark with defaults (100 trajectories, 10k steps)
python benchmark.py

# Custom configuration
python benchmark.py 1000 100000 0.001
# Args: n_trajectories n_steps timestep_size
```

**Output:**
- Console: Timing and error statistics
- `data/energy_drift_comparison.png`: Energy comparison plot

### GPU Build (CUDA)

```bash
mkdir build && cd build
cmake ..
make

# Run GPU benchmark executable (to be implemented)
./symplectic_gpu_benchmark
```

**Requirements:**
- CUDA Toolkit ≥ 11.0
- GPU with compute capability ≥ 7.0 (V100/A100/RTX series)
- CMake ≥ 3.18

---

## ✨ Key Achievements

✅ **Phase 1 Complete**: CPU baseline demonstrates clear advantage of symplectic integrators  
✅ **Mathematical Correctness**: Implements exactly the theory from mechanics textbooks  
✅ **Scalable Architecture**: Perfect embarrassingly-parallel structure  
⏳ **Phase 2 In Progress**: GPU kernels for massive parallel scaling  

---

## 📚 References

- Leimkuhler, B., & Reich, S. (2004). *Simulating Hamiltonian Dynamics*
- Thorne, K. S., & Blandford, R. D. (2017). *Modern Classical Physics*
- Hénon, M., & Heiles, C. (1964). The applicability of the third integral of motion

---

## 🎯 What Comes Next

1. **Complete GPU implementation** — Optimize kernels for hardware
2. **Mixed precision variant** — FP32 dynamics, FP64 energy tracking
3. **Advanced visualization** — Animation of phase space evolution
4. **Adaptive timestepping** — Detect chaos and adjust dt dynamically
5. **Performance analysis** — Roofline model analysis

---

**Built to demonstrate that mathematical rigor and GPU acceleration aren't just compatible—they're powerful together.**


[def]: https://shields.io