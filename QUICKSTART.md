# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites

- **CPU Baseline:**
  - Python 3.8+
  - NumPy, SciPy, Matplotlib

- **GPU (CUDA):**
  - CUDA Toolkit 11.0+
  - CMake 3.18+
  - GPU with compute capability ≥ 7.0

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run CPU Benchmark

```bash
cd src/cpu
python benchmark.py
```

**Output:**
- Timing comparison
- Energy drift statistics  
- Plot: `data/energy_drift_comparison.png`

### Step 3: Analyze Results

```bash
cd notebooks
jupyter notebook 01_cpu_benchmark.ipynb
```

This notebook shows:
- ✅ Energy preservation of symplectic integrator
- ❌ Energy explosion in Euler method
- ⚠️ Energy drift in RK4 method

### Step 4 (Optional): Build GPU Kernels

```bash
mkdir build && cd build
cmake ..
make
```

Requires CUDA toolkit.

---

## 📊 Expected Results

### CPU Benchmark Output

```
======================================================================
GPU-ACCELERATED SYMPLECTIC INTEGRATOR - CPU BASELINE BENCHMARK
======================================================================
Configuration:
  Trajectories: 100
  Steps: 10000
  Timestep: 0.001
  Total time: 10.00
  System: Henon-Heiles (chaotic regime)

--- Euler Integrator ---
  Time: X.XXXs
  Initial Energy: 0.XXXXXX
  Final Energy: X.XXXXXX (DIVERGED)
  Max Abs Error: X.XXe+XX
  Max Rel Error: X.XXe+XX

--- RK4 Integrator ---
  Time: X.XXXs
  Initial Energy: 0.XXXXXX
  Final Energy: 0.XXXXXX
  Max Abs Error: X.XXe-XX
  Max Rel Error: X.XXe-XX

--- Symplectic Integrator ---
  Time: X.XXXs
  Initial Energy: 0.XXXXXX
  Final Energy: 0.XXXXXX
  Max Abs Error: X.XXe-XX (TINY!) ✓
  Max Rel Error: X.XXe-XX
```

The key insight: **Symplectic preserves energy while Euler/RK4 fail**

---

## 🔍 What to Look For

In the energy drift plot:

1. **Euler** (red line at top)
   - Exponential growth
   - Clearly fails
   - Shows why naive integration is dangerous

2. **RK4** (orange line in middle)
   - Linear drift
   - Better than Euler
   - But accumulates error over time

3. **Symplectic** (green line at bottom)
   - Bounded oscillation
   - Stable over entire time range
   - What structure preservation looks like

---

## 🎯 Next Steps

### To Deepen Understanding

- [ ] Read `README.md` for mathematical background
- [ ] Study `src/cpu/integrators.py` — understand each method
- [ ] Modify `benchmark.py` — try different initial conditions
- [ ] Implement adaptive timestepping

### To Extend the Project

- [ ] GPU kernel optimization
- [ ] Mixed-precision integration
- [ ] Poincaré section visualization
- [ ] Performance profiling

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/cpu/benchmark.py` | Run CPU benchmark |
| `src/cpu/integrators.py` | All three integrators |
| `src/cpu/analysis.py` | Visualization & analysis |
| `notebooks/01_cpu_benchmark.ipynb` | Interactive analysis |
| `include/henon_heiles.h` | System definitions |
| `src/gpu/integrators.cu` | GPU kernels |
| `CMakeLists.txt` | Build configuration |

---

## 💡 Tips

### To see more detail in energy conservation:

```bash
python benchmark.py 1000 50000 0.0005
```
This runs 1000 trajectories for 50,000 steps with smaller timestep.

### To test different systems:

Modify `henon_heiles_gradients()` in `src/cpu/integrators.py` to implement another Hamiltonian.

### To profile GPU performance:

```bash
nvprof ./build/symplectic_gpu_benchmark
```

---

## ❓ FAQ

**Q: Why symplectic integrators?**  
A: They preserve the mathematical structure (symplectic form) that encodes energy conservation. This survives discretization, unlike naive methods.

**Q: Why GPU?**  
A: Each trajectory is independent → embarrassingly parallel. GPU excels at this pattern. 100x-1000x speedup expected.

**Q: What's special about Hénon-Heiles?**  
A: It's chaotic and nonlinear, so errors accumulate fast. A perfect test case for structure preservation.

**Q: Can I use this for other systems?**  
A: Yes! Modify the potential and gradient functions to implement any Hamiltonian.

---

**Ready to dive in? Run `python src/cpu/benchmark.py` and check `data/energy_drift_comparison.png`!**
