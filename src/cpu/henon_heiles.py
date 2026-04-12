"""
Hénon-Heiles System: A Chaotic Hamiltonian System

This file provides utility functions for the Hénon-Heiles system.
"""

import numpy as np


def henon_heiles_hamiltonian(x, y, px, py):
    """
    Compute the Hénon-Heiles Hamiltonian
    
    H(x, y, px, py) = 0.5*(px^2 + py^2) + 0.5*(x^2 + y^2) + x^2*y - (1/3)*y^3
    
    Parameters:
    -----------
    x, y : float or array
        Position coordinates
    px, py : float or array  
        Momentum components
        
    Returns:
    --------
    H : float or array
        Hamiltonian energy
    """
    kinetic = 0.5 * (px**2 + py**2)
    potential = 0.5 * (x**2 + y**2) + x**2 * y - (1.0/3.0) * y**3
    return kinetic + potential


def henon_heiles_potential(x, y):
    """
    Compute the Hénon-Heiles potential
    
    V(x, y) = 0.5*(x^2 + y^2) + x^2*y - (1/3)*y^3
    """
    return 0.5 * (x**2 + y**2) + x**2 * y - (1.0/3.0) * y**3


def henon_heiles_gradients(x, y):
    """
    Compute gradients of the potential
    
    ∂V/∂x = x + 2*x*y
    ∂V/∂y = y + x^2 - y^2
    """
    grad_x = x + 2.0 * x * y
    grad_y = y + x**2 - y**2
    return grad_x, grad_y


def estimate_lyapunov_exponent(trajectory_data, dt=0.001):
    """
    Estimate Lyapunov exponent from trajectory
    
    Positive exponent indicates chaos
    """
    # Simplified approach: track divergence of nearby trajectories
    # Full implementation would require running two close trajectories
    pass


# Energy threshold for chaotic regime
E_chaotic_threshold = 1.0/6.0  # ≈ 0.167
