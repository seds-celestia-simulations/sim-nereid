# History

## Overview

Nereid did not begin as a framework.

It began as a small experiment to understand Smoothed Particle Hydrodynamics (SPH) from first principles.

Over time, the project evolved through multiple independent implementations, each focused on solving a specific limitation of the previous version.

This document records that evolution.

---

# Phase I — Naive SPH

**Objective**

Understand the fundamentals of particle-based fluid simulation.

**Implementation**

The first implementation was a direct two-dimensional SPH solver based closely on the mathematical formulation of SPH.

Features included:

- Density estimation
    
- Pressure computation
    
- Pressure-gradient forces
    
- Boundary collisions
    
- Euler integration
    

Every particle interacted with every other particle.

Complexity:

```text
O(N²)
```

Neighbour searches were performed through brute-force iteration.

**Key Lessons**

This implementation established a working understanding of:

- SPH interpolation
    
- Density estimation
    
- Pressure formulations
    
- Kernel functions
    
- Numerical integration
    

However, performance degraded rapidly as particle counts increased.

The implementation served primarily as a proof of concept and educational reference.

---

# Phase II — Vectorized SPH

**Objective**

Improve performance without sacrificing physical behaviour.

**Implementation**

The second implementation introduced a complete redesign of the data model.

Particle objects were replaced with a Structure-of-Arrays architecture:

```text
position_array
velocity_array
density_array
acceleration_array
```

Major additions:

- NumPy vectorization
    
- Spatial hashing
    
- Grid-based neighbour search
    
- Symmetric pressure formulation
    
- Artificial viscosity
    

Neighbour searches were restricted to local grid regions.

Complexity improved from:

```text
O(N²)
```

to approximately:

```text
O(Nk)
```

where k is the average neighbour count.

**Key Lessons**

This phase demonstrated that algorithmic improvements were significantly more important than raw hardware performance.

Spatial hashing became a foundational component of all future versions.

---

# Phase III — Taichi SPH

**Objective**

Explore parallel execution and GPU acceleration.

**Implementation**

The third implementation ported major components of the solver to Taichi.

Major additions:

- GPU execution
    
- Parallel neighbour processing
    
- Parallel sorting
    
- Taichi kernels
    
- GPU-friendly data structures
    

This implementation focused primarily on performance exploration rather than physical completeness.

Several simplifications were intentionally introduced to study acceleration strategies.

**Key Lessons**

This phase established a viable path toward large-scale particle simulations.

It also revealed that acceleration alone is insufficient; a physically complete solver architecture must be preserved while optimizing performance.

The Taichi implementation remains an important experimental backend for future development.

---

# Phase IV — Three-Dimensional SPH

**Objective**

Extend the simulation from two dimensions into fully three-dimensional domains.

**Implementation**

The current implementation introduced:

- Three-dimensional particle systems
    
- Three-dimensional spatial hashing
    
- Velocity Verlet integration
    
- Improved pressure formulation
    
- Artificial viscosity
    
- Real-time visualization
    
- Data export pipelines
    

Particle initialization was expanded to support structured volumetric configurations and impact scenarios.

The simulation architecture now consists of:

```text
Particle State
      ↓
Spatial Hashing
      ↓
Neighbour Search
      ↓
Density Evaluation
      ↓
Pressure Evaluation
      ↓
Force Computation
      ↓
Velocity Verlet Integration
```

This version represents the most physically complete implementation developed so far.

**Key Lessons**

The transition to three dimensions highlighted the importance of:

- Memory efficiency
    
- Modular solver design
    
- Validation methodology
    
- Separation of physics and visualization
    

These lessons directly motivated the development of Nereid as a framework rather than a standalone simulation.

---

# Toward Nereid

The prototype implementations demonstrated the feasibility of:

- SPH density estimation
    
- Pressure-based fluid dynamics
    
- Spatial hashing
    
- Artificial viscosity
    
- GPU acceleration
    
- Three-dimensional particle simulation
    

However, they also exposed architectural limitations:

- Tight coupling between rendering and physics
    
- Multiple overlapping implementations
    
- Limited validation infrastructure
    
- Difficulty extending the solver
    

Nereid was created to address these limitations.

The framework represents the next stage of the project:

```text
Prototype Simulations
        ↓
Validated Solver
        ↓
Modular Framework
        ↓
Research Platform
```

The historical implementations remain preserved as reference systems and educational artifacts documenting the project's development.