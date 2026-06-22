# Nereid

Nereid is a particle-based framework focused on **Smoothed Particle Hydrodynamics (SPH)** and particle-based numerical methods.

The current implementation features a fully three-dimensional SPH solver built from first principles, including density estimation, pressure forces, artificial viscosity, spatial hashing, and Velocity Verlet integration.

---

## Demonstration

<img width="216" height="384" alt="SPH_GIF" src="https://github.com/user-attachments/assets/ec2a6069-63c5-4404-a585-90ae83e4aa3d" /> <img width="600" height="384" alt="fluid_sim_15k - Trim" src="https://github.com/user-attachments/assets/d9c53b01-a626-4662-8f69-81bab90abd87" />

---

## Motivation

Traditional computational fluid dynamics (CFD) approaches typically discretize space using fixed grids. Particle methods provide a mesh-free alternative in which fluid properties are carried directly by moving particles.

Nereid explores these methods from first principles, with an emphasis on:

* Numerical simulation
* Computational physics
* Scientific visualization
* High-performance particle methods
* Extensible simulation architecture

---

## Current Features

### Physics

* Three-dimensional SPH formulation
* Density estimation using smoothing kernels
* Pressure force computation
* Artificial viscosity
* Gravity and boundary interactions

### Numerical Methods

* Velocity Verlet integration
* Compact-support smoothing kernels
* Structure-of-arrays particle storage
* Vectorized force evaluation

### Performance

* Spatial hashing neighbour search
* Grid-based particle partitioning
* Localized neighbourhood queries
* Reduced complexity relative to naive O(N²) approaches

### Visualization & Output

* Real-time OpenGL visualization
* 3D particle rendering
* Frame export pipeline
* JSON simulation snapshots

---

## Simulation Pipeline

```text
Particle State
      ↓
Spatial Hashing
      ↓
Neighbour Search
      ↓
Density Estimation
      ↓
Pressure & Viscosity
      ↓
Force Accumulation
      ↓
Velocity Verlet Integration
      ↓
Updated Particle State
```

---

## Repository Structure

```text
Nereid/

├── src/
├── docs/
├── examples/
└── legacy/
```

The repository contains multiple prototype implementations developed during the evolution of the project:

* Naive SPH
* Vectorized SPH
* 3D SPH
* Experimental Taichi backend

These implementations serve both as references and as stepping stones toward a unified framework architecture.

---

## Roadmap

### Phase I — Framework Consolidation

* Modular solver architecture
* Documentation overhaul
* Validation suite
* Codebase cleanup

### Phase II — Performance

* GPU acceleration
* Taichi backend
* Larger particle counts

### Phase III — Advanced SPH

* WCSPH improvements
* PCISPH
* DFSPH
* Improved boundary handling

### Phase IV — Extended Physics

* Multi-phase flows
* Granular materials
* Solid-fluid interaction
* Astrophysical SPH experiments

---

## Documentation

* `docs/theory.md` — Mathematical foundations of SPH
* `docs/architecture.md` — System architecture and design decisions
* `docs/roadmap.md` — Development roadmap
* `docs/history.md` — Evolution of the project

---

## Credits

Based on the initial SPH project developed at SEDS Celestia, BITS Goa.

Contributors:

* Aditya Melinkeri
* Harliv Singh
* Tanya Bahrani

---

## References
- [Coding Adventure: Simulating Fluids](https://www.youtube.com/watch?v=rSKMYc1CQHE) - An excellent implementation of SPH.
- Müller, M., Charypar, D., & Gross, M. (2003). *Particle-Based Fluid Simulation for Interactive Applications*. [PDF](https://matthias-research.github.io/pages/publications/sca03.pdf)
