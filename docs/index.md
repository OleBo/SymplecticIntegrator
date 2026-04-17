---
title: Home
nav_order: 1
---

# GPU-Accelerated Hamiltonian Integrators

## Overview

This project implements **GPU-accelerated numerical integrators** for simulating nonlinear Hamiltonian systems, with a focus on the **Hénon–Heiles system** — a classical benchmark for studying chaos and long-term dynamical behavior.

The core idea is to combine:

* **Mathematical structure (Hamiltonian mechanics)**
* **Advanced numerical methods (symplectic integrators)**
* **High-performance computing (CUDA on GPUs)**

to simulate **millions of trajectories efficiently and accurately**.

---

## Why This Project Matters

Simulating physical systems over long time horizons is fundamentally challenging:

* Standard high-order methods (e.g. RK4) introduce **energy drift**
* Physical systems require preservation of **geometric structure**
* GPUs enable massive parallel exploration of phase space

This project demonstrates that:

> **Structure-preserving algorithms + GPU parallelism = scalable and physically correct simulations**

---

## Project Documentation

### 📘 Mathematical Documentation

👉 [Symplectic Integrator — Mathematical Documentation](symplectic_integrator_documentation.md)

Covers:

* Hamiltonian formulation
* Hénon–Heiles system
* Symplectic integration theory
* Energy conservation and phase-space structure
* Visual diagrams and plots

---

### 🧪 Benchmark Experiment

👉 [Benchmark Experiment Documentation](benchmark_experiment_documentation.md)

Covers:

* Experimental design and methodology
* Accuracy vs stability comparison
* Energy drift analysis
* GPU vs CPU performance evaluation
* Reproducibility setup

---

### ⚙️ CUDA Implementation

👉 [CUDA Implementation Documentation](cuda_implementation_documentation.md)

Covers:

* Kernel design and parallelization strategy
* Memory layout (SoA vs AoS)
* Annotated CUDA kernels
* Performance optimization techniques
* Practical HPC considerations

---

## Key Features

* ✅ Symplectic (Leapfrog) integrator for long-term stability
* ✅ RK4 and Euler baselines for comparison
* ✅ GPU parallelization (one trajectory per thread)
* ✅ Energy diagnostics and validation
* ✅ Visualization-ready outputs

---

## 📌 Key Insight

This project highlights a fundamental principle in scientific computing:

> **Numerical accuracy alone is not enough — preserving the underlying physics is essential.**

---

## 👤 Author

This project is part of a portfolio exploring:
- Numerical linear algebra
- GPU programming (CUDA)
- High-performance computing systems