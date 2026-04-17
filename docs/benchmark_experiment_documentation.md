---
title: Benchmark Experiments
nav_order: 3
---

# GPU-Accelerated Integrators — Benchmark Experiment Documentation

## Overview

This document describes the **benchmarking methodology** used to evaluate numerical integrators for the Hénon–Heiles system on CPU and GPU implementations.

The goal is not just performance measurement, but a **scientifically meaningful comparison** across:

* Numerical accuracy
* Energy conservation
* Long-term stability
* Computational efficiency

---

## 1. Objective

The benchmark is designed to answer three core questions:

### 1.1 Numerical Accuracy vs Physical Fidelity

* How accurately does each integrator approximate trajectories?
* Does higher-order accuracy (e.g. RK4) imply better physical correctness?

---

### 1.2 Long-Term Stability

* Does the method preserve invariants such as energy?
* Does error **drift** or remain **bounded**?

---

### 1.3 Performance and Scalability

* How does GPU performance scale with number of trajectories?
* What is the speedup over CPU implementations?

---

## 2. Systems Under Study

### 2.1 Dynamical System

The Hénon–Heiles Hamiltonian:

[
H = \frac{1}{2}(p_x^2 + p_y^2) + \frac{1}{2}(x^2 + y^2) + x^2 y - \frac{1}{3} y^3
]

---

### 2.2 State Representation

Each trajectory is defined by:

[
z = (x, y, p_x, p_y)
]

---

### 2.3 Integrators Compared

| Method   | Order | Symplectic | Expected Behavior                 |
| -------- | ----- | ---------- | --------------------------------- |
| Euler    | 1     | ❌          | Fast divergence                   |
| RK4      | 4     | ❌          | Accurate short-term, energy drift |
| Leapfrog | 2     | ✅          | Long-term stable                  |

---

## 3. Experimental Design

### 3.1 Initial Conditions

* Multiple trajectories initialized with:

  * Fixed energy level ( H \approx
