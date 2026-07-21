# Nereid

**Nereid is a computational laboratory for particle-based simulation, high-performance computing, and Smoothed Particle Hydrodynamics.**

---

## Demonstration

<img width="400" height="503" alt="nereid" src="https://github.com/user-attachments/assets/a0bf94f7-774d-4779-8363-6ea7865f8026" />

---

# Overview

Smoothed Particle Hydrodynamics represents fluids using moving particles carrying physical quantities such as density, pressure, and velocity.

Nereid is designed to investigate particle-based numerical methods from first principles, with particular emphasis on algorithmic design, computational performance, and modular simulation architecture.

The project is organized around independent simulation subsystems:

- Physics
- Spatial acceleration
- Numerical integration
- Rendering
- Diagnostics

rather than a single monolithic solver.

---

# Implemented Concepts

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
│   └── spatial_data.py
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

# Research Directions

**Particle Methods**
- WCSPH improvements
- PCISPH
- DFSPH
- Position-Based Fluids

**High-Performance Computing**
- Numba
- GPU compute
- Spatial data structures
- Parallel algorithms

**Physical Systems**
- Free-surface flows
- Multiphase fluids
- Granular media
- Elastic solids
- Astrophysical SPH

---

# References

- [Coding Adventure: Simulating Fluids](https://www.youtube.com/watch?v=rSKMYc1CQHE) - An excellent implementation of SPH.
- Müller, M., Charypar, D., & Gross, M. (2003). *Particle-Based Fluid Simulation for Interactive Applications*. [PDF](https://matthias-research.github.io/pages/publications/sca03.pdf)

---

# Credits

Developed within **SEDS Celestia, BITS Goa**.

Contributors

- [Harliv Singh](https://github.com/h-livv)
