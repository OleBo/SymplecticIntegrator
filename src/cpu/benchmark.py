"""
Benchmark CPU integrators on Henon-Heiles system

Compare energy conservation and accuracy across methods
"""

import numpy as np
import sys
import time
from integrators import (
    EulerIntegrator, RK4Integrator, SymplecticIntegrator,
    batch_integrate, create_initial_condition
)
from analysis import EnergyAnalysis, setup_output_dir


def benchmark_integrators(n_trajectories: int = 100, 
                         n_steps: int = 10000,
                         dt: float = 0.001) -> None:
    """
    Benchmark all three integrators
    
    Args:
        n_trajectories: Number of parallel trajectories
        n_steps: Integration steps per trajectory
        dt: Timestep size
    """
    print(f"\n{'='*70}")
    print("GPU-ACCELERATED SYMPLECTIC INTEGRATOR - CPU BASELINE BENCHMARK")
    print(f"{'='*70}")
    print(f"Configuration:")
    print(f"  Trajectories: {n_trajectories}")
    print(f"  Steps: {n_steps}")
    print(f"  Timestep: {dt}")
    print(f"  Total time: {n_steps * dt:.2f}")
    print(f"  System: Henon-Heiles (chaotic regime)")
    
    # Create initial conditions
    print(f"\nGenerating initial conditions...")
    initial_states = create_initial_condition(n_trajectories, seed=42)
    
    # Setup analysis
    analysis = EnergyAnalysis()
    output_dir = setup_output_dir()
    
    # Benchmark each integrator
    integrators = [
        ('Euler', EulerIntegrator),
        ('RK4', RK4Integrator),
        ('Symplectic', SymplecticIntegrator)
    ]
    
    for method_name, integrator_class in integrators:
        print(f"\n--- {method_name} Integrator ---")
        
        # Copy initial states
        states = [s.copy() for s in initial_states]
        
        # Time the integration
        t_start = time.time()
        final_states, integrators_list = batch_integrate(
            states, dt, n_steps, integrator_class
        )
        t_elapsed = time.time() - t_start
        
        # Collect energies from all trajectories
        energies_history = []
        for integrator in integrators_list:
            energies_history.append(np.array(integrator.energies).T)
        
        energies_all = np.concatenate(energies_history, axis=1)
        times = np.array(integrators_list[0].times)
        
        # Store in analysis
        analysis.add_result(method_name.lower(), energies_all, times)
        
        # Statistics
        E_initial = np.mean(energies_all[0, :])
        E_final = np.mean(energies_all[-1, :])
        dE_max = np.max(np.abs(energies_all - E_initial))
        dE_rel_max = np.max(np.abs(energies_all - E_initial) / np.abs(E_initial))
        
        print(f"  Time: {t_elapsed:.3f}s")
        print(f"  Initial Energy: {E_initial:.6f}")
        print(f"  Final Energy: {E_final:.6f}")
        print(f"  Max Abs Error: {dE_max:.2e}")
        print(f"  Max Rel Error: {dE_rel_max:.2e}")
        print(f"  Throughput: {n_trajectories * n_steps / t_elapsed:.2e} steps/sec")
    
    # Generate plots
    print(f"\nGenerating analysis plots...")
    analysis.print_summary()
    
    fig, ax = analysis.plot_energy_drift(
        output_path=f"{output_dir}/energy_drift_comparison.png"
    )
    plt.close(fig)
    
    print(f"\nResults saved to: {output_dir}/")


if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    
    # Run benchmark with command-line arguments
    n_traj = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    n_steps = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    dt = float(sys.argv[3]) if len(sys.argv) > 3 else 0.001
    
    benchmark_integrators(n_traj, n_steps, dt)
