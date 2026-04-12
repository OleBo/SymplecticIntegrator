#pragma once

#include "henon_heiles.h"

/**
 * @file integrators.h
 * @brief Integrator kernels and host-device function declarations
 */

// Host-side CPU integrator declarations
struct IntegratorStats {
    float initial_energy;
    float final_energy;
    float max_energy_error;
    float avg_energy_error;
    float computation_time_ms;
};

// CPU integrators (implemented in Python, these are CUDA versions)
void euler_step_gpu(State4D* states, int n, float dt);
void rk4_step_gpu(State4D* states, int n, float dt);
void symplectic_step_gpu(State4D* states, int n, float dt);

// GPU kernels
__global__ void euler_kernel(
    float* x, float* y, float* px, float* py,
    int n, float dt, int steps);

__global__ void rk4_kernel(
    float* x, float* y, float* px, float* py,
    int n, float dt, int steps);

__global__ void symplectic_kernel(
    float* x, float* y, float* px, float* py,
    int n, float dt, int steps);

__global__ void energy_kernel(
    const float* x, const float* y,
    const float* px, const float* py,
    float* energies, int n);
