#pragma once

/**
 * @file henon_heiles.h
 * @brief Henon-Heiles Hamiltonian system definitions
 * 
 * Hamiltonian: H(x,y,px,py) = 0.5*(px^2 + py^2) + 0.5*(x^2 + y^2) + x^2*y - (1/3)*y^3
 */

struct State4D {
    float x, y, px, py;
};

/**
 * Compute Hamiltonian energy
 */
__host__ __device__ inline float compute_energy(float x, float y, float px, float py) {
    float kinetic = 0.5f * (px * px + py * py);
    float potential = 0.5f * (x * x + y * y) + x * x * y - (1.0f/3.0f) * y * y * y;
    return kinetic + potential;
}

/**
 * Compute gradient components of Hamiltonian
 */
__host__ __device__ inline void compute_gradients(
    float x, float y,
    float& grad_x, float& grad_y) {
    grad_x = x + 2.0f * x * y;
    grad_y = y + x * x - y * y;
}
