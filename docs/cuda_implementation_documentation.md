---
title: CUDA Implementation
nav_order: 4
---

# CUDA Implementation Documentation — GPU-Accelerated Integrators

## Overview

This document explains the **CUDA implementation details** of the GPU-accelerated integrators for the Hénon–Heiles system.

The focus is on:

* Mapping Hamiltonian dynamics to GPU kernels
* Memory layout and performance considerations
* Kernel design for numerical integrators
* Practical CUDA optimization strategies

---

## 1. Computational Problem

We simulate a large number (N) of independent trajectories:

[
z_i(t) = (x_i, y_i, p_{x,i}, p_{y,i}), \quad i = 1, \dots, N
]

Each trajectory evolves according to:

[
\dot{z}_i = f(z_i)
]

**Key property:**

> All trajectories are independent → ideal for massive parallelism.

---

## 2. Parallelization Strategy

### 2.1 Thread Mapping

Each CUDA thread is responsible for **one trajectory**:

```cpp
int i = blockIdx.x * blockDim.x + threadIdx.x;
```

If:

```cpp
i < N
```

then thread `i` updates:

```cpp
x[i], y[i], px[i], py[i]
```

---

### 2.2 Execution Model

```text
Grid
 ├── Block 0
 │    ├── Thread 0 → Trajectory 0
 │    ├── Thread 1 → Trajectory 1
 │    └── ...
 ├── Block 1
 │    └── ...
 └── ...
```

---

## 3. Memory Layout

### 3.1 Structure of Arrays (SoA)

The implementation uses:

```cpp
double* x;
double* y;
double* px;
double* py;
```

instead of:

```cpp
struct State { double x, y, px, py; };
State* states;
```

---

### 3.2 Why SoA?

**Benefits:**

* Coalesced memory access
* Better cache utilization
* Higher memory bandwidth

---

### 3.3 Coalesced Access Pattern

```text
Thread 0 → x[0]
Thread 1 → x[1]
Thread 2 → x[2]
...
```

This allows the GPU to fetch memory in **contiguous blocks**.

---

## 4. Kernel Design

### 4.1 General Structure

Each kernel follows the pattern:

```cpp
__global__ void integrator_kernel(...) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;

    // Load state
    double xi = x[i];
    double yi = y[i];
    double pxi = px[i];
    double pyi = py[i];

    // Time stepping loop
    for (int step = 0; step < steps; ++step) {
        // integrator update
    }

    // Store state
    x[i] = xi;
    y[i] = yi;
    px[i] = pxi;
    py[i] = pyi;
}
```

---

### 4.2 Design Choices

* **Register usage:** state variables kept in registers
* **Minimized global memory access:** load once, store once
* **No synchronization:** independent threads

---

## 5. Gradient Computation

### 5.1 Device Function

```cpp
__device__ void compute_gradients(double x, double y,
                                  double& dVdx, double& dVdy)
```

---

### 5.2 Mathematical Form

[
\frac{\partial V}{\partial x} = x + 2xy
]
[
\frac{\partial V}{\partial y} = y + x^2 - y^2
]

---

### 5.3 Optimization Notes

* Inline device function → avoids function call overhead
* Uses only registers → no memory traffic

---

## 6. Symplectic Integrator Kernel

### 6.1 Algorithm in CUDA

```cpp
// Half-step momentum update
px -= 0.5 * dt * dVdx;
py -= 0.5 * dt * dVdy;

// Full-step position update
x += dt * px;
y += dt * py;

// Recompute gradients
compute_gradients(x, y, dVdx, dVdy);

// Second half-step momentum update
px -= 0.5 * dt * dVdx;
py -= 0.5 * dt * dVdy;
```

---

### 6.2 Key Property

> This update is **symplectic**, meaning it preserves phase-space structure.

---

## 7. RK4 Kernel

### 7.1 Structure

RK4 requires multiple intermediate evaluations:

```cpp
k1 = f(z)
k2 = f(z + dt/2 * k1)
k3 = f(z + dt/2 * k2)
k4 = f(z + dt * k3)
```

---

### 7.2 GPU Implications

* More arithmetic per step
* Higher register pressure
* More gradient evaluations

---

## 8. Euler Kernel

### 8.1 Update Rule

```cpp
x += dt * px;
y += dt * py;
px -= dt * dVdx;
py -= dt * dVdy;
```

---

### 8.2 Role

* Baseline method
* Debugging reference
* Not suitable for production simulations

---

## 9. Energy Kernel

### 9.1 Purpose

Compute:

[
E_i = \frac{1}{2}(p_x^2 + p_y^2) + V(x,y)
]

---

### 9.2 CUDA Implementation Pattern

```cpp
__global__ void energy_kernel(...) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;

    energy[i] = ...;
}
```

---

## 10. Host–Device Interaction

### 10.1 Workflow

1. Allocate device memory (`cudaMalloc`)
2. Copy data to GPU (`cudaMemcpy`)
3. Launch kernel
4. Copy results back
5. Free memory

---

### 10.2 Example

```cpp
cudaMemcpy(d_x, x, size, cudaMemcpyHostToDevice);

kernel<<<grid, block>>>(...);

cudaMemcpy(x, d_x, size, cudaMemcpyDeviceToHost);
```

---

## 11. Performance Considerations

### 11.1 Occupancy

* Choose block size (e.g. 128–256 threads)
* Balance:

  * register usage
  * active warps

---

### 11.2 Arithmetic Intensity

Symplectic integrator:

* Moderate arithmetic
* Low memory traffic
* Good GPU utilization

RK4:

* High arithmetic
* Potential register bottleneck

---

### 11.3 Memory Bottlenecks

Avoid:

* Repeated global loads/stores inside loop
* Uncoalesced memory access

---

## 12. Scaling Behavior

### 12.1 Strong Scaling

Fix number of trajectories, vary GPU:

* Limited by memory bandwidth

---

### 12.2 Weak Scaling

Increase (N):

[
\text{Runtime} \sim \mathcal{O}(N)
]

GPU handles millions of trajectories efficiently.

---

## 13. Precision Considerations

### 13.1 FP32 vs FP64

* FP32: faster, less accurate
* FP64: slower, required for long simulations

---

### 13.2 Mixed Precision (Advanced)

* Store state in FP32
* Accumulate energy in FP64

---

## 14. Common Pitfalls

* ❌ Divergence due to large timestep
* ❌ Energy drift (non-symplectic methods)
* ❌ Register spilling in RK4
* ❌ Poor memory layout (AoS)

---

## 15. Summary

This CUDA implementation demonstrates:

* Efficient mapping of **Hamiltonian dynamics to GPU kernels**
* Importance of **memory layout (SoA)**
* Trade-offs between **numerical accuracy and GPU performance**
* Why **symplectic integrators are ideal for large-scale simulations**

---

## Final Insight

> GPUs excel when the mathematical structure matches the hardware model.

Here:

* Independent trajectories → parallel threads
* Local computations → register usage
* Minimal communication → high scalability

This alignment is what enables **high-performance scientific computing**.


# CUDA Implementation Documentation — Annotated Code Snippets

This section adds **line-by-line annotated CUDA kernels** for the three integrators and key helpers. The goal is to make the mapping from **mathematics → GPU execution** completely explicit.

---

## 1. Thread Indexing & Guard

```cpp
// Compute global thread index
int i = blockIdx.x * blockDim.x + threadIdx.x;

// Guard against out-of-bounds threads
if (i >= N) return;
```

**Explanation**

* `blockIdx.x`: block id in the grid
* `blockDim.x`: threads per block
* `threadIdx.x`: thread id within block
* Global index `i` maps **thread → trajectory**
* Guard avoids illegal memory access when grid is oversized

---

## 2. Device Function: Gradient of Potential

```cpp
__device__ __forceinline__
void compute_gradients(double x, double y,
                       double& dVdx, double& dVdy)
{
    // ∂V/∂x = x + 2xy
    dVdx = x + 2.0 * x * y;

    // ∂V/∂y = y + x^2 - y^2
    dVdy = y + x * x - y * y;
}
```

**Explanation**

* `__device__`: runs on GPU
* `__forceinline__`: encourages inlining → avoids call overhead
* Uses only registers → **no global memory traffic**
* Direct implementation of the analytical gradient

---

## 3. Symplectic (Leapfrog) Kernel

```cpp
__global__
void symplectic_kernel(double* x, double* y,
                       double* px, double* py,
                       int N, int steps, double dt)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;

    // --- Load state into registers (fast) ---
    double xi  = x[i];
    double yi  = y[i];
    double pxi = px[i];
    double pyi = py[i];

    double dVdx, dVdy;

    // --- Time integration loop ---
    for (int s = 0; s < steps; ++s) {

        // Compute gradient at current position
        compute_gradients(xi, yi, dVdx, dVdy);

        // (1) Half-step momentum update (Kick)
        pxi -= 0.5 * dt * dVdx;
        pyi -= 0.5 * dt * dVdy;

        // (2) Full-step position update (Drift)
        xi += dt * pxi;
        yi += dt * pyi;

        // Recompute gradient at new position
        compute_gradients(xi, yi, dVdx, dVdy);

        // (3) Half-step momentum update (Kick)
        pxi -= 0.5 * dt * dVdx;
        pyi -= 0.5 * dt * dVdy;
    }

    // --- Store results back to global memory ---
    x[i]  = xi;
    y[i]  = yi;
    px[i] = pxi;
    py[i] = pyi;
}
```

**Key Points**

* State loaded **once** → stored **once**
* Loop operates entirely in **registers**
* Implements:

  * Kick → Drift → Kick splitting
* Preserves **symplectic structure**

---

## 4. RK4 Kernel (Annotated)

```cpp
__global__
void rk4_kernel(double* x, double* y,
                double* px, double* py,
                int N, int steps, double dt)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;

    double xi  = x[i];
    double yi  = y[i];
    double pxi = px[i];
    double pyi = py[i];

    for (int s = 0; s < steps; ++s) {

        // k1
        double dVdx1, dVdy1;
        compute_gradients(xi, yi, dVdx1, dVdy1);

        double k1_x  = pxi;
        double k1_y  = pyi;
        double k1_px = -dVdx1;
        double k1_py = -dVdy1;

        // k2 (midpoint using k1)
        double x2  = xi  + 0.5 * dt * k1_x;
        double y2  = yi  + 0.5 * dt * k1_y;
        double px2 = pxi + 0.5 * dt * k1_px;
        double py2 = pyi + 0.5 * dt * k1_py;

        double dVdx2, dVdy2;
        compute_gradients(x2, y2, dVdx2, dVdy2);

        double k2_x  = px2;
        double k2_y  = py2;
        double k2_px = -dVdx2;
        double k2_py = -dVdy2;

        // k3 (another midpoint)
        double x3  = xi  + 0.5 * dt * k2_x;
        double y3  = yi  + 0.5 * dt * k2_y;
        double px3 = pxi + 0.5 * dt * k2_px;
        double py3 = pyi + 0.5 * dt * k2_py;

        double dVdx3, dVdy3;
        compute_gradients(x3, y3, dVdx3, dVdy3);

        double k3_x  = px3;
        double k3_y  = py3;
        double k3_px = -dVdx3;
        double k3_py = -dVdy3;

        // k4 (full step)
        double x4  = xi  + dt * k3_x;
        double y4  = yi  + dt * k3_y;
        double px4 = pxi + dt * k3_px;
        double py4 = pyi + dt * k3_py;

        double dVdx4, dVdy4;
        compute_gradients(x4, y4, dVdx4, dVdy4);

        double k4_x  = px4;
        double k4_y  = py4;
        double k4_px = -dVdx4;
        double k4_py = -dVdy4;

        // Combine increments
        xi  += dt / 6.0 * (k1_x  + 2*k2_x  + 2*k3_x  + k4_x);
        yi  += dt / 6.0 * (k1_y  + 2*k2_y  + 2*k3_y  + k4_y);
        pxi += dt / 6.0 * (k1_px + 2*k2_px + 2*k3_px + k4_px);
        pyi += dt / 6.0 * (k1_py + 2*k2_py + 2*k3_py + k4_py);
    }

    x[i]  = xi;
    y[i]  = yi;
    px[i] = pxi;
    py[i] = pyi;
}
```

**Key Points**

* 4 gradient evaluations per step
* High arithmetic intensity
* More **register pressure** → possible spilling
* Not structure-preserving

---

## 5. Euler Kernel (Baseline)

```cpp
__global__
void euler_kernel(double* x, double* y,
                  double* px, double* py,
                  int N, int steps, double dt)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;

    double xi  = x[i];
    double yi  = y[i];
    double pxi = px[i];
    double pyi = py[i];

    double dVdx, dVdy;

    for (int s = 0; s < steps; ++s) {
        compute_gradients(xi, yi, dVdx, dVdy);

        // Explicit Euler update
        xi  += dt * pxi;
        yi  += dt * pyi;
        pxi -= dt * dVdx;
        pyi -= dt * dVdy;
    }

    x[i]  = xi;
    y[i]  = yi;
    px[i] = pxi;
    py[i] = pyi;
}
```

**Key Points**

* Minimal computation
* Useful for debugging
* Physically unstable

---

## 6. Energy Kernel

```cpp
__global__
void energy_kernel(const double* x, const double* y,
                   const double* px, const double* py,
                   double* E, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;

    double xi  = x[i];
    double yi  = y[i];
    double pxi = px[i];
    double pyi = py[i];

    // Kinetic energy
    double T = 0.5 * (pxi * pxi + pyi * pyi);

    // Potential energy
    double V = 0.5 * (xi * xi + yi * yi)
             + xi * xi * yi
             - (1.0 / 3.0) * yi * yi * yi;

    E[i] = T + V;
}
```

**Key Points**

* Purely **read-only inputs → write-only output**
* Memory bandwidth bound
* Ideal for parallel reduction extensions

---

## 7. Kernel Launch Configuration

```cpp
int blockSize = 256;
int gridSize  = (N + blockSize - 1) / blockSize;

symplectic_kernel<<<gridSize, blockSize>>>(d_x, d_y, d_px, d_py,
                                           N, steps, dt);
```

**Explanation**

* Ensures coverage of all (N) trajectories
* Typical block size: 128–256 (hardware dependent)

---

## 8. Performance Checklist (Practical)

* ✔ Load state into registers once
* ✔ Avoid global memory inside loop
* ✔ Use SoA layout
* ✔ Inline small device functions
* ✔ Watch register usage (`nvcc --ptxas-options=-v`)
* ✔ Tune block size experimentally

---

## Final Insight

These kernels illustrate a key HPC principle:

> **Performance emerges when mathematical structure aligns with hardware structure.**

* Independent trajectories → thread-level parallelism
* Local updates → register reuse
* Minimal communication → massive scalability

---
