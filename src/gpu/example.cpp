/**
 * @file example.cpp
 * @brief Example usage of GPU integrators
 * 
 * This demonstrates how to use the GPU kernels for trajectory integration
 */

#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>
#include "henon_heiles.h"
#include "integrators.h"


// Error checking macro
#define CUDA_CHECK(err) { \
    cudaError_t cuda_error = (err); \
    if (cuda_error != cudaSuccess) { \
        fprintf(stderr, "CUDA error: %s\n", cudaGetErrorString(cuda_error)); \
        exit(EXIT_FAILURE); \
    } \
}


/**
 * GPU benchmark runner
 */
int main(int argc, char* argv[]) {
    printf("GPU-Accelerated Symplectic Integrator - Example\n");
    printf("================================================\n\n");
    
    // Configuration
    int n_trajectories = 1000;
    int n_steps = 100000;
    float dt = 0.001f;
    
    printf("Configuration:\n");
    printf("  Trajectories: %d\n", n_trajectories);
    printf("  Steps: %d\n", n_steps);
    printf("  Timestep: %f\n", dt);
    printf("  Total time: %f\n\n", n_steps * dt);
    
    // Allocate host memory
    size_t bytes = n_trajectories * sizeof(float);
    float *h_x = (float*)malloc(bytes);
    float *h_y = (float*)malloc(bytes);
    float *h_px = (float*)malloc(bytes);
    float *h_py = (float*)malloc(bytes);
    
    // Initialize with random conditions
    printf("Initializing %d random trajectories...\n", n_trajectories);
    for (int i = 0; i < n_trajectories; ++i) {
        h_x[i] = 0.1f * (rand() / (float)RAND_MAX - 0.5f);
        h_y[i] = 0.1f * (rand() / (float)RAND_MAX - 0.5f);
        h_px[i] = 0.3f * (rand() / (float)RAND_MAX - 0.5f);
        h_py[i] = 0.3f * (rand() / (float)RAND_MAX - 0.5f);
    }
    
    // Allocate device memory
    float *d_x, *d_y, *d_px, *d_py;
    CUDA_CHECK(cudaMalloc(&d_x, bytes));
    CUDA_CHECK(cudaMalloc(&d_y, bytes));
    CUDA_CHECK(cudaMalloc(&d_px, bytes));
    CUDA_CHECK(cudaMalloc(&d_py, bytes));
    
    // Copy to device
    printf("Copying data to GPU...\n");
    CUDA_CHECK(cudaMemcpy(d_x, h_x, bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_y, h_y, bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_px, h_px, bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_py, h_py, bytes, cudaMemcpyHostToDevice));
    
    // Launch symplectic kernel
    printf("Launching symplectic integrator kernel...\n");
    int blockSize = 256;
    int gridSize = (n_trajectories + blockSize - 1) / blockSize;
    
    cudaEvent_t start, stop;
    CUDA_CHECK(cudaEventCreate(&start));
    CUDA_CHECK(cudaEventCreate(&stop));
    
    CUDA_CHECK(cudaEventRecord(start));
    symplectic_kernel<<<gridSize, blockSize>>>(
        d_x, d_y, d_px, d_py,
        n_trajectories, dt, n_steps
    );
    CUDA_CHECK(cudaEventRecord(stop));
    CUDA_CHECK(cudaEventSynchronize(stop));
    
    float ms = 0.0f;
    CUDA_CHECK(cudaEventElapsedTime(&ms, start, stop));
    
    // Check for kernel errors
    CUDA_CHECK(cudaGetLastError());
    
    printf("Kernel execution time: %.3f ms\n", ms);
    printf("Throughput: %.2e steps/sec\n", 
           (float)n_trajectories * n_steps / (ms / 1000.0f));
    
    // Copy results back
    printf("Copying results back to CPU...\n");
    CUDA_CHECK(cudaMemcpy(h_x, d_x, bytes, cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(h_y, d_y, bytes, cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(h_px, d_px, bytes, cudaMemcpyDeviceToHost));
    CUDA_CHECK(cudaMemcpy(h_py, d_py, bytes, cudaMemcpyDeviceToHost));
    
    // Compute final energies
    printf("Computing final energies...\n");
    float E_mean = 0.0f, E_min = 1e6f, E_max = -1e6f;
    for (int i = 0; i < n_trajectories; ++i) {
        float E = compute_energy(h_x[i], h_y[i], h_px[i], h_py[i]);
        E_mean += E;
        E_min = (E < E_min) ? E : E_min;
        E_max = (E > E_max) ? E : E_max;
    }
    E_mean /= n_trajectories;
    
    printf("\nFinal Energy Statistics:\n");
    printf("  Mean: %.6f\n", E_mean);
    printf("  Min:  %.6f\n", E_min);
    printf("  Max:  %.6f\n", E_max);
    printf("  Range: %.6f\n", E_max - E_min);
    
    // Cleanup
    free(h_x); free(h_y); free(h_px); free(h_py);
    CUDA_CHECK(cudaFree(d_x));
    CUDA_CHECK(cudaFree(d_y));
    CUDA_CHECK(cudaFree(d_px));
    CUDA_CHECK(cudaFree(d_py));
    
    printf("\n✓ Example completed successfully\n");
    return 0;
}
