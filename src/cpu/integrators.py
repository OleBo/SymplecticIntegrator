"""
CPU Baseline Integrators for Henon-Heiles System

Implements three integration schemes:
1. Explicit Euler (naive, poor energy preservation)
2. RK4 (accurate for short times, poor long-term energy)
3. Symplectic/Leapfrog (structure-preserving, excellent energy conservation)
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List
import time


@dataclass
class State:
    """4D Hamiltonian state: (x, y, px, py)"""
    x: np.ndarray
    y: np.ndarray
    px: np.ndarray
    py: np.ndarray
    
    def copy(self):
        return State(self.x.copy(), self.y.copy(), self.px.copy(), self.py.copy())


def henon_heiles_potential(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Henon-Heiles potential: V(x,y) = 0.5*(x^2 + y^2) + x^2*y - (1/3)*y^3
    """
    return 0.5 * (x**2 + y**2) + x**2 * y - (1.0/3.0) * y**3


def henon_heiles_energy(x: np.ndarray, y: np.ndarray, 
                        px: np.ndarray, py: np.ndarray) -> np.ndarray:
    """
    Henon-Heiles Hamiltonian: H = 0.5*(px^2 + py^2) + V(x,y)
    
    Returns energy for each particle (broadcasting compatible)
    """
    kinetic = 0.5 * (px**2 + py**2)
    potential = henon_heiles_potential(x, y)
    return kinetic + potential


def henon_heiles_gradients(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute gradients of potential: (dV/dx, dV/dy)
    
    dV/dx = x + 2*x*y
    dV/dy = y + x^2 - y^2
    """
    grad_x = x + 2.0 * x * y
    grad_y = y + x**2 - y**2
    return grad_x, grad_y


class BaseIntegrator:
    """Base class for trajectory integrators"""
    
    def __init__(self):
        self.energies = []
        self.times = []
        
    def integrate(self, state: State, dt: float, steps: int) -> State:
        """Integrate state forward in time"""
        raise NotImplementedError
        
    def _record_energy(self, state: State, t: float):
        """Record energy at current timestep"""
        E = henon_heiles_energy(state.x, state.y, state.px, state.py)
        self.energies.append(E.copy())
        self.times.append(t)


class EulerIntegrator(BaseIntegrator):
    """
    Explicit Euler method: naive, non-symplectic
    
    q_{n+1} = q_n + dt * p_n
    p_{n+1} = p_n - dt * dV/dq(q_n)
    """
    
    def integrate(self, state: State, dt: float, steps: int) -> State:
        """Integrate using explicit Euler"""
        self.energies = []
        self.times = []
        
        x, y, px, py = state.x.copy(), state.y.copy(), state.px.copy(), state.py.copy()
        
        self._record_energy(State(x, y, px, py), 0.0)
        
        for n in range(steps):
            # Compute gradients
            grad_x, grad_y = henon_heiles_gradients(x, y)
            
            # Update positions
            x += dt * px
            y += dt * py
            
            # Update momenta
            px -= dt * grad_x
            py -= dt * grad_y
            
            self._record_energy(State(x, y, px, py), (n + 1) * dt)
        
        return State(x, y, px, py)


class RK4Integrator(BaseIntegrator):
    """
    Fourth-order Runge-Kutta integrator
    
    Accurate for short times but experiences secular drift in energy
    """
    
    def integrate(self, state: State, dt: float, steps: int) -> State:
        """Integrate using RK4"""
        self.energies = []
        self.times = []
        
        x, y, px, py = state.x.copy(), state.y.copy(), state.px.copy(), state.py.copy()
        
        self._record_energy(State(x, y, px, py), 0.0)
        
        for n in range(steps):
            # RK4 stages for the system:
            # dq/dt = p, dp/dt = -dV/dq
            
            # k1
            grad_x1, grad_y1 = henon_heiles_gradients(x, y)
            k1_x = px
            k1_y = py
            k1_px = -grad_x1
            k1_py = -grad_y1
            
            # k2
            grad_x2, grad_y2 = henon_heiles_gradients(x + 0.5*dt*k1_x, y + 0.5*dt*k1_y)
            k2_x = px + 0.5*dt*k1_px
            k2_y = py + 0.5*dt*k1_py
            k2_px = -grad_x2
            k2_py = -grad_y2
            
            # k3
            grad_x3, grad_y3 = henon_heiles_gradients(x + 0.5*dt*k2_x, y + 0.5*dt*k2_y)
            k3_x = px + 0.5*dt*k2_px
            k3_y = py + 0.5*dt*k2_py
            k3_px = -grad_x3
            k3_py = -grad_y3
            
            # k4
            grad_x4, grad_y4 = henon_heiles_gradients(x + dt*k3_x, y + dt*k3_y)
            k4_x = px + dt*k3_px
            k4_y = py + dt*k3_py
            k4_px = -grad_x4
            k4_py = -grad_y4
            
            # Update
            x += (dt/6.0) * (k1_x + 2*k2_x + 2*k3_x + k4_x)
            y += (dt/6.0) * (k1_y + 2*k2_y + 2*k3_y + k4_y)
            px += (dt/6.0) * (k1_px + 2*k2_px + 2*k3_px + k4_px)
            py += (dt/6.0) * (k1_py + 2*k2_py + 2*k3_py + k4_py)
            
            self._record_energy(State(x, y, px, py), (n + 1) * dt)
        
        return State(x, y, px, py)


class SymplecticIntegrator(BaseIntegrator):
    """
    Leapfrog/Velocity Verlet symplectic integrator
    
    Structure-preserving: conserves Hamiltonian structure
    Phase space volume preserving
    Excellent long-term energy conservation
    
    Algorithm:
    p_{n+1/2} = p_n - (dt/2) * dV/dq(q_n)
    q_{n+1} = q_n + dt * p_{n+1/2}
    p_{n+1} = p_{n+1/2} - (dt/2) * dV/dq(q_{n+1})
    """
    
    def integrate(self, state: State, dt: float, steps: int) -> State:
        """Integrate using symplectic integrator"""
        self.energies = []
        self.times = []
        
        x, y, px, py = state.x.copy(), state.y.copy(), state.px.copy(), state.py.copy()
        
        self._record_energy(State(x, y, px, py), 0.0)
        
        for n in range(steps):
            # Compute initial gradients
            grad_x, grad_y = henon_heiles_gradients(x, y)
            
            # Half-step momentum update
            px -= 0.5 * dt * grad_x
            py -= 0.5 * dt * grad_y
            
            # Full-step position update
            x += dt * px
            y += dt * py
            
            # Recompute gradients at new position
            grad_x, grad_y = henon_heiles_gradients(x, y)
            
            # Final half-step momentum update
            px -= 0.5 * dt * grad_x
            py -= 0.5 * dt * grad_y
            
            self._record_energy(State(x, y, px, py), (n + 1) * dt)
        
        return State(x, y, px, py)


def batch_integrate(states_list: List[State], dt: float, steps: int, 
                   integrator_class) -> Tuple[List[State], List]:
    """
    Integrate multiple trajectories
    
    Args:
        states_list: List of initial states
        dt: Timestep
        steps: Number of integration steps
        integrator_class: Integrator class to use
        
    Returns:
        Final states, list of integrators with recorded energies
    """
    integrators = []
    final_states = []
    
    for state in states_list:
        integrator = integrator_class()
        final_state = integrator.integrate(state, dt, steps)
        integrators.append(integrator)
        final_states.append(final_state)
    
    return final_states, integrators


def create_initial_condition(n_trajectories: int, seed: int = 42) -> List[State]:
    """
    Create ensemble of initial conditions for Henon-Heiles system
    
    Sample in the chaotic regime
    """
    np.random.seed(seed)
    
    # Energy threshold - chaotic regime is E > 1/6
    E_target = 0.15  # Slightly above threshold
    
    states = []
    for _ in range(n_trajectories):
        # Random position
        x = np.random.randn() * 0.3
        y = np.random.randn() * 0.3
        
        # Random momentum direction, scale to achieve target energy
        theta = np.random.uniform(0, 2*np.pi)
        p_mag = np.sqrt(2 * (E_target - henon_heiles_potential(x, y)))
        px = p_mag * np.cos(theta)
        py = p_mag * np.sin(theta)
        
        states.append(State(
            x=np.array([x], dtype=np.float32),
            y=np.array([y], dtype=np.float32),
            px=np.array([px], dtype=np.float32),
            py=np.array([py], dtype=np.float32)
        ))
    
    return states
