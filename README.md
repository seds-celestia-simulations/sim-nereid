# Nereid

**An experimental environment for studying particle-based numerical methods, with a focus on Smoothed Particle Hydrodynamics and high-performance simulation.**

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

**Physics**

- Weakly Compressible SPH
- Pressure forces
- Artificial viscosity
- Boundary handling

**Numerics**

- Explicit Euler
- Vectorized particle interactions
- Compact-support kernels

**Performance**

- Uniform spatial hash
- Neighbor search
- Structure-of-Arrays storage
- OpenGL rendering

**Diagnostics**

- Runtime profiling
- Statistics overlay
- Multiple visualization modes

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

---

# Future Directions

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
