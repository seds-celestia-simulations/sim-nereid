# Architecture

## Overview

Nereid is a particle-based continuum mechanics framework centered around Smoothed Particle Hydrodynamics (SPH).

Rather than discretizing space using a fixed mesh, Nereid represents fluids as collections of particles carrying physical quantities such as position, velocity, density, and pressure. Interactions are computed locally using smoothing kernels.

The framework is organized around four layers:

1. State Representation
    
2. Numerical Infrastructure
    
3. Physics Modules
    
4. Visualization & Analysis
    

---

# System Pipeline

```text
Particle State
      ↓
Spatial Hashing
      ↓
Neighbour Search
      ↓
Density Estimation
      ↓
Pressure Evaluation
      ↓
Force Computation
      ↓
Time Integration
      ↓
Updated State
```

---

# Particle State

The simulation evolves a particle state vector:

X = (r, v, a, ρ)

where

- r = position
    
- v = velocity
    
- a = acceleration
    
- ρ = density
    

Future versions may include:

X = (r, v, a, ρ, P, T, m)

for pressure, temperature, and variable mass systems.

All particle data is stored using a Structure-of-Arrays layout.

Example:

```text
position_array
velocity_array
acceleration_array
density_array
```

This design improves cache locality, enables vectorized operations, and supports future GPU acceleration.

---

# Spatial Partitioning

A naive SPH implementation requires every particle to interact with every other particle.

Complexity:

O(N²)

Nereid uses spatial hashing to reduce neighbour search costs.

The simulation domain is partitioned into uniform cells whose size is proportional to the smoothing length h.

Each particle is assigned a hash:

Hash(x,y,z) → Cell ID

Particles are sorted by cell ID each simulation step.

Benefits:

- Localized neighbour queries
    
- Reduced computational cost
    
- GPU-friendly architecture
    
- Scalable particle counts
    

---

# Neighbour Search

For each particle cell:

- Identify the containing cell
    
- Search the surrounding 3×3×3 cell neighbourhood
    
- Construct a local neighbour list
    

Neighbour search is treated as infrastructure.

Physics modules operate only on neighbour lists and remain independent of the underlying search algorithm.

Future alternatives:

- Octrees
    
- BVH structures
    
- Adaptive grids
    
- GPU hash grids
    

---

# Kernel System

SPH interactions are mediated through smoothing kernels.

The kernel subsystem is responsible for:

- Density interpolation
    
- Gradient evaluation
    
- Force computation
    

Required interfaces:

```text
W(r,h)
∇W(r,h)
∇²W(r,h)
```

Supported kernels:

- Poly6
    
- Spiky
    
- Cubic spline
    

Future kernels may be added without modifying solver logic.

---

# Density Solver

The density solver computes particle densities using neighbour contributions.

Input:

- Particle positions
    
- Particle masses
    
- Neighbour lists
    

Output:

- Density field
    

The density field acts as the primary intermediate quantity used by subsequent physics modules.

---

# Pressure Solver

Pressure is derived from density using an equation of state.

Current formulation:

Weakly Compressible SPH (WCSPH)

Responsibilities:

- Pressure computation
    
- Pressure gradient evaluation
    
- Momentum conservation
    

Future formulations:

- PCISPH
    
- IISPH
    
- DFSPH
    

---

# Viscosity Module

Viscosity models internal momentum diffusion.

Current implementation uses artificial viscosity inspired by Monaghan formulations.

Responsibilities:

- Shock stabilization
    
- Velocity smoothing
    
- Numerical stability
    

Future work:

- Physical viscosity models
    
- Turbulence approximations
    
- Non-Newtonian fluids
    

---

# Boundary Conditions

Boundary handling prevents particle escape and models interactions with solid surfaces.

Current implementation:

- Reflective boundaries
    
- Velocity damping
    
- Positional correction
    

Future work:

- Ghost particles
    
- Dynamic boundaries
    
- Moving rigid bodies
    
- Fluid-solid coupling
    

---

# Time Integration

Particle states evolve through numerical integration.

Current default:

Velocity Verlet

Advantages:

- Second-order accuracy
    
- Improved stability
    
- Better energy behaviour
    

Future integrators:

- Leapfrog
    
- RK4
    
- Symplectic schemes
    

---

# Visualization Layer

Visualization is intentionally separated from physics.

Responsibilities:

- Particle rendering
    
- Camera control
    
- Data export
    

Supported outputs:

- Real-time rendering
    
- JSON snapshots
    

Future outputs:

- VTK
    
- HDF5
    
- ParaView integration
    
- Blender pipelines
    

---

# Validation Philosophy

Nereid prioritizes validation before optimization.

Every major physics module should be tested against established benchmark problems before deployment.

Validation targets include:

- Hydrostatic equilibrium
    
- Dam break
    
- Taylor-Green vortex
    
- Shock tube problems
    

Correctness takes precedence over performance.