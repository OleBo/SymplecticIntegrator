"""
Analysis and visualization tools for Hamiltonian dynamics
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import List, Tuple
import os


class EnergyAnalysis:
    """Analyze energy conservation across trajectories and methods"""
    
    def __init__(self):
        self.results = {}
    
    def add_result(self, method_name: str, energies_history: List[np.ndarray], 
                   times: np.ndarray):
        """
        Store energy history for a method
        
        Args:
            method_name: Name of integrator method
            energies_history: List of energy arrays (one per trajectory, then per timestep)
            times: Time points
        """
        energies = np.array(energies_history)  # Shape: (steps, n_trajectories)
        self.results[method_name] = {
            'energies': energies,
            'times': times
        }
    
    def compute_statistics(self, method_name: str) -> dict:
        """Compute energy conservation statistics"""
        result = self.results[method_name]
        energies = result['energies']
        
        # Initial energy (first timestep, take median across trajectories)
        E0 = np.median(energies[0, :])
        
        # Relative energy errors
        dE = energies - E0
        dE_rel = np.abs(dE) / np.abs(E0)
        
        stats = {
            'initial_energy': E0,
            'max_error_abs': np.max(np.abs(dE)),
            'max_error_rel': np.max(dE_rel),
            'mean_error_abs': np.mean(np.abs(dE)),
            'mean_error_rel': np.mean(dE_rel),
            'final_energy_spread': np.std(energies[-1, :])
        }
        
        return stats
    
    def plot_energy_drift(self, output_path: str = None):
        """
        Plot energy drift for all methods
        
        Shows the key advantage of symplectic integrators
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        colors = {'euler': 'red', 'rk4': 'orange', 'symplectic': 'green'}
        
        for method_name, result in self.results.items():
            energies = result['energies']
            times = result['times']
            
            # Compute mean energy and spread
            E_mean = np.mean(energies, axis=1)
            E_std = np.std(energies, axis=1)
            E0 = E_mean[0]
            
            dE = E_mean - E0
            
            # Absolute error
            axes[0].semilogy(times, np.abs(dE) + 1e-12, 
                            label=method_name.capitalize(), 
                            linewidth=2, color=colors.get(method_name))
            
            # Relative error
            dE_rel = np.abs(dE) / np.abs(E0)
            axes[1].semilogy(times, dE_rel + 1e-12, 
                            label=method_name.capitalize(),
                            linewidth=2, color=colors.get(method_name))
        
        axes[0].set_xlabel('Time')
        axes[0].set_ylabel('|ΔE| (absolute)')
        axes[0].set_title('Absolute Energy Drift')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        axes[1].set_xlabel('Time')
        axes[1].set_ylabel('|ΔE|/|E₀| (relative)')
        axes[1].set_title('Relative Energy Drift')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Saved: {output_path}")
        
        return fig, axes
    
    def plot_phase_space(self, trajectory_idx: int = 0, output_path: str = None):
        """
        Plot phase space trajectories in (x, px) and (y, py) planes
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        colors = {'euler': 'red', 'rk4': 'orange', 'symplectic': 'green'}
        
        for method_name, states in self.results.items():
            # Placeholder - would need to store full trajectory info
            pass
        
        axes[0].set_xlabel('x')
        axes[0].set_ylabel('$p_x$')
        axes[0].set_title('Phase Space: (x, $p_x$)')
        axes[0].grid(True, alpha=0.3)
        
        axes[1].set_xlabel('y')
        axes[1].set_ylabel('$p_y$')
        axes[1].set_title('Phase Space: (y, $p_y$)')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
        
        return fig, axes
    
    def print_summary(self):
        """Print comparison summary"""
        print("\n" + "="*70)
        print("ENERGY CONSERVATION ANALYSIS")
        print("="*70)
        
        for method_name in sorted(self.results.keys()):
            stats = self.compute_statistics(method_name)
            print(f"\n{method_name.upper()}")
            print(f"  Initial Energy: {stats['initial_energy']:.6f}")
            print(f"  Max Abs Error:  {stats['max_error_abs']:.2e}")
            print(f"  Max Rel Error:  {stats['max_error_rel']:.2e}")
            print(f"  Mean Abs Error: {stats['mean_error_abs']:.2e}")
            print(f"  Mean Rel Error: {stats['mean_error_rel']:.2e}")
            print(f"  Final Energy Spread (σ): {stats['final_energy_spread']:.2e}")
        
        print("\n" + "="*70)


def setup_output_dir(base_dir: str = "data") -> str:
    """Create output directory for results"""
    os.makedirs(base_dir, exist_ok=True)
    return base_dir
