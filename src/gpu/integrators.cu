/**
 * @file integrators.cu
 * @brief GPU kernels for integrating Hamiltonian systems
 * 
 * Each thread processes one trajectory independently
 * Perfect embarrassingly parallel structure
 */

#include "henon_heiles.h"
#include "integrators.h"
#include <stdio.h>


/**
 * Explicit Euler integrator kernel
 * 
 * Non-symplectic, naive method
 * q_{n+1} = q_n + dt * p_n
 * p_{n+1} = p_n - dt * dV/dq(q_n)
 */
__global__ void euler_kernel(
    float* x, float* y, float* px, float* py,
    int n, float dt, int steps) {
    
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    
    float xi = x[i];
    float yi = y[i];
    float pxi = px[i];
    float pyi = py[i];
    
    for (int t = 0; t < steps; ++t) {
        // Compute gradients
        float grad_x, grad_y;
        compute_gradients(xi, yi, grad_x, grad_y);
        
        // Update positions
        xi += dt * pxi;
        yi += dt * pyi;
        
        // Update momenta
        pxi -= dt * grad_x;
        pyi -= dt * grad_y;
    }
    
    x[i] = xi;
    y[i] = yi;
    px[i] = pxi;
    py[i] = pyi;
}


/**
 * RK4 integrator kernel
 * 
 * Fourth-order accurate, but not symplectic
 * Better short-term accuracy, poor long-term energy conservation
 */
__global__ void rk4_kernel(
    float* x, float* y, float* px, float* py,
    int n, float dt, int steps) {
    
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    
    float xi = x[i];
    float yi = y[i];
    float pxi = px[i];
    float pyi = py[i];
    
    for (int t = 0; t < steps; ++t) {
        // k1
        float grad_x1, grad_y1;
        compute_gradients(xi, yi, grad_x1, grad_y1);
        float k1_x = pxi;
        float k1_y = pyi;
        float k1_px = -grad_x1;
        float k1_py = -grad_y1;
        
        // k2
        float grad_x2, grad_y2;
        compute_gradients(xi + 0.5f*dt*k1_x, yi + 0.5f*dt*k1_y, grad_x2, grad_y2);
        float k2_x = pxi + 0.5f*dt*k1_px;
        float k2_y = pyi + 0.5f*dt*k1_py;
        float k2_px = -grad_x2;
        float k2_py = -grad_y2;
        
        // k3
        float grad_x3, grad_y3;
        compute_gradients(xi + 0.5f*dt*k2_x, yi + 0.5f*dt*k2_y, grad_x3, grad_y3);
        float k3_x = pxi + 0.5f*dt*k2_px;
        float k3_y = pyi + 0.5f*dt*k2_py;
        float k3_px = -grad_x3;
        float k3_py = -grad_y3;
        
        // k4
        float grad_x4, grad_y4;
        compute_gradients(xi + dt*k3_x, yi + dt*k3_y, grad_x4, grad_y4);
        float k4_x = pxi + dt*k3_px;
        float k4_y = pyi + dt*k3_py;
        float k4_px = -grad_x4;
        float k4_py = -grad_y4;
        
        // Update
        xi += (dt/6.0f) * (k1_x + 2.0f*k2_x + 2.0f*k3_x + k4_x);
        yi += (dt/6.0f) * (k1_y + 2.0f*k2_y + 2.0f*k3_y + k4_y);
        pxi += (dt/6.0f) * (k1_px + 2.0f*k2_px + 2.0f*k3_px + k4_px);
        pyi += (dt/6.0f) * (k1_py + 2.0f*k2_py + 2.0f*k3_py + k4_py);
    }
    
    x[i] = xi;
    y[i] = yi;
    px[i] = pxi;
    py[i] = pyi;
}


/**
 * Symplectic (Leapfrog/Velocity Verlet) integrator kernel
 * 
 * Structure-preserving: conserves Hamiltonian structure
 * Phase space volume preserving
 * Excellent long-term energy conservation
 * 
 * Algorithm:
 * p_{n+1/2} = p_n - (dt/2) * dV/dq(q_n)
 * q_{n+1} = q_n + dt * p_{n+1/2}
 * p_{n+1} = p_{n+1/2} - (dt/2) * dV/dq(q_{n+1})
 */
__global__ void symplectic_kernel(
    float* x, float* y, float* px, float* py,
    int n, float dt, int steps) {
    
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    
    float xi = x[i];
    float yi = y[i];
    float pxi = px[i];
    float pyi = py[i];
    
    for (int t = 0; t < steps; ++t) {
        // Compute gradients at current position
        float grad_x, grad_y;
        compute_gradients(xi, yi, grad_x, grad_y);
        
        // Half-step momentum update
        pxi -= 0.5f * dt * grad_x;
        pyi -= 0.5f * dt * grad_y;
        
        // Full-step position update
        xi += dt * pxi;
        yi += dt * pyi;
        
        // Recompute gradients at new position
        compute_gradients(xi, yi, grad_x, grad_y);
        
        // Final half-step momentum update
        pxi -= 0.5f * dt * grad_x;
        pyi -= 0.5f * dt * grad_y;
    }
    
    x[i] = xi;
    y[i] = yi;
    px[i] = pxi;
    py[i] = pyi;
}


/**
 * Compute Hamiltonian energy for each trajectory
 * 
 * Kernel for potential energy calculations and diagnostics
 */
__global__ void energy_kernel(
    const float* x, const float* y,
    const float* px, const float* py,
    float* energies, int n) {
    
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    
    energies[i] = compute_energy(x[i], y[i], px[i], py[i]);
}


// Host-side wrapper functions

void euler_step_gpu(State4D* states, int n, float dt) {
    // Allocate device memory
    float *d_x, *d_y, *d_px, *d_py;
    size_t bytes = n * sizeof(float);
    
    cudaMalloc(&d_x, bytes);
    cudaMalloc(&d_y, bytes);
    cudaMalloc(&d_px, bytes);
    cudaMalloc(&d_py, bytes);
    
    // Copy to device
    float *h_x = new float[n], *h_y = new float[n],
          *h_px = new float[n], *h_py = new float[n];
    for (int i = 0; i < n; ++i) {
        h_x[i] = states[i].x;
        h_y[i] = states[i].y;
        h_px[i] = states[i].px;
        h_py[i] = states[i].py;
    }
    
    cudaMemcpy(d_x, h_x, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_y, h_y, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_px, h_px, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_py, h_py, bytes, cudaMemcpyHostToDevice);
    
    // Launch kernel
    int blockSize = 256;
    int gridSize = (n + blockSize - 1) / blockSize;
    euler_kernel<<<gridSize, blockSize>>>(d_x, d_y, d_px, d_py, n, dt, 1);
    
    // Copy back
    cudaMemcpy(h_x, d_x, bytes, cudaMemcpyDeviceToHost);
    cudaMemcpy(h_y, d_y, bytes, cudaMemcpyDeviceToHost);
    cudaMemcpy(h_px, d_px, bytes, cudaMemcpyDeviceToHost);
    cudaMemcpy(h_py, d_py, bytes, cudaMemcpyDeviceToHost);
    
    for (int i = 0; i < n; ++i) {
        states[i].x = h_x[i];
        states[i].y = h_y[i];
        states[i].px = h_px[i];
        states[i].py = h_py[i];
    }
    
    // Cleanup
    delete[] h_x; delete[] h_y; delete[] h_px; delete[] h_py;
    cudaFree(d_x); cudaFree(d_y); cudaFree(d_px); cudaFree(d_py);
}

void rk4_step_gpu(State4D* states, int n, float dt) {
    // Similar structure to euler_step_gpu
}

void symplectic_step_gpu(State4D* states, int n, float dt) {
    // Similar structure to euler_step_gpu
}
