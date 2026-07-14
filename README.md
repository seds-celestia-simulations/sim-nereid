# Nereid

A modern particle simulation framework built around **Smoothed Particle Hydrodynamics (SPH)**.

Nereid is designed as a research and development platform for particle-based numerical methods, emphasizing clean architecture, extensibility, and performance. The current implementation provides a CPU-based Weakly Compressible SPH (WCSPH) solver with real-time visualization and a modular framework intended to support future particle methods.

---

## Demonstration

<img width="400" height="503" alt="nereid" src="https://github.com/user-attachments/assets/a0bf94f7-774d-4779-8363-6ea7865f8026" />

---

# Overview

Smoothed Particle Hydrodynamics represents fluids using moving particles carrying physical quantities such as density, pressure, and velocity.

Nereid explores these methods from first principles while providing a reusable software architecture for particle simulations.

The project is organized around independent simulation subsystems:

- Physics
- Spatial acceleration
- Numerical integration
- Rendering
- Diagnostics

rather than a single monolithic solver.

---

# Current Features

## Physics

- Weakly Compressible SPH (WCSPH)
- Density estimation
- Pressure force computation
- Artificial viscosity
- Gravity
- Boundary collisions

## Numerical Methods

- Explicit Euler integration
- Compact-support smoothing kernels
- Data-oriented particle storage (Structure of Arrays)
- Fully vectorized particle interactions

## Spatial Acceleration

- Uniform spatial hash grid
- Grid-based neighbour search
- Local neighbourhood evaluation
- Near-linear neighbour queries

## Rendering

- GPU-accelerated OpenGL renderer
- GLSL shader pipeline
- Circular particle rendering
- Multiple visualization modes
  - Solid
  - Velocity
  - Density

## Diagnostics

- Built-in frame profiler
- Runtime statistics overlay
- Screenshot capture
- Pause / Resume
- Simulation reset

---

# Architecture

```
                Simulation
                     │
      ┌──────────────┼──────────────┐
      │              │              │
  ParticleData   SpatialHash    Renderer
      │              │              │
 Parameters      Neighbour      Diagnostics
      │            Search
      │
 Integrator
```

The framework follows a hybrid **Object-Oriented + Data-Oriented** design.

Large particle datasets are stored in contiguous NumPy arrays for efficient vectorized computation, while higher-level systems encapsulate simulation logic into modular components.

---

# Simulation Pipeline

```
Particle State
      │
      ▼
Spatial Hash Construction
      │
      ▼
Neighbour Search
      │
      ▼
Density Estimation
      │
      ▼
Pressure Evaluation
      │
      ▼
Force Accumulation
      │
      ▼
Integration
      │
      ▼
Rendering
```

---

# Repository Structure

```
src/
│
├── core/
│   ├── data.py
│   ├── simulation.py
│   └── integrators.py
│
├── physics/
│   ├── kernel.py
│   └── solver.py
│
├── spatial/
│   └── spatial_hashing.py
│
├── rendering/
│   └── renderer.py
│
├── diagnostics/
│   └── profiler.py
│
└── main.py
```

---

# Project Goals

Nereid is intended to evolve beyond a single SPH implementation into a general particle simulation framework.

## Near Term

- Leapfrog integration
- Kernel abstraction
- Multiple boundary models
- Solver validation
- Documentation

## Performance

- Numba acceleration
- GPU compute backend
- Improved neighbour search
- Larger particle counts

## Advanced SPH

- Surface tension
- XSPH correction
- Adaptive timesteps
- PCISPH
- DFSPH

## Long Term

- Multi-phase fluids
- Granular materials
- Elastic solids
- Astrophysical SPH
- General particle-based numerical methods

---

# References

- [Coding Adventure: Simulating Fluids](https://www.youtube.com/watch?v=rSKMYc1CQHE) - An excellent implementation of SPH.
- Müller, M., Charypar, D., & Gross, M. (2003). *Particle-Based Fluid Simulation for Interactive Applications*. [PDF](https://matthias-research.github.io/pages/publications/sca03.pdf)

---

# Credits

Developed within **SEDS Celestia, BITS Goa**.

Contributors

- Harliv Singh
