cmake_minimum_required(VERSION 3.18)
project(SymplecticIntegrator LANGUAGES CXX CUDA)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# CUDA settings
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -O3 -arch=sm_75")

# Include directories
include_directories(${PROJECT_SOURCE_DIR}/include)

# Add GPU library
add_library(symplectic_gpu SHARED
    src/gpu/integrators.cu
)
set_target_properties(symplectic_gpu PROPERTIES
    CUDA_SEPARABLE_COMPILATION ON
)

# CPU utilities (header-only)
add_library(symplectic_cpu INTERFACE
    include/henon_heiles.h
    include/integrators.h
)
target_include_directories(symplectic_cpu INTERFACE
    ${PROJECT_SOURCE_DIR}/include
)

# Example executable (optional)
add_executable(example src/gpu/example.cpp)
target_link_libraries(example symplectic_gpu)

# Build tests
enable_testing()
add_subdirectory(tests EXCLUDE_FROM_ALL)

# Print configuration
message(STATUS "GPU Architecture: sm_75")
message(STATUS "CUDA Compute Capability: 7.5")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
