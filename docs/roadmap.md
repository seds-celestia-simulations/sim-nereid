# Roadmap

## Vision

Nereid aims to evolve from a standalone SPH implementation into a modular particle-based continuum mechanics framework.

The long-term objective is to provide a platform for experimentation with particle methods across fluid dynamics, multiphysics systems, and computational science.

---

# Phase I — Foundation

Status: In Progress

Goals:

- Refactor prototype implementations
    
- Separate physics from visualization
    
- Modular architecture
    
- Documentation overhaul
    
- Establish validation framework
    

Deliverables:

- Clean repository structure
    
- Architecture documentation
    
- Theory documentation
    
- Benchmark suite
    

---

# Phase II — Validation

Goals:

- Hydrostatic equilibrium test
    
- Dam-break benchmark
    
- Taylor-Green vortex
    
- Shock-tube benchmark
    

Deliverables:

- Quantitative validation metrics
    
- Convergence studies
    
- Error analysis
    

Success Criteria:

- Reproducible benchmark results
    
- Agreement with literature
    

---

# Phase III — Performance

Goals:

- Taichi backend
    
- GPU acceleration
    
- Improved memory layout
    
- Parallel neighbour search
    

Deliverables:

- Real-time simulations
    
- Increased particle counts
    
- Backend abstraction layer
    

Target Scale:

100k–1M particles

---

# Phase IV — Advanced SPH

Goals:

- PCISPH
    
- IISPH
    
- DFSPH
    

Deliverables:

- Reduced density error
    
- Improved incompressibility
    
- Larger stable time steps
    

---

# Phase V — Extended Physics

Goals:

- Surface tension
    
- Multiphase fluids
    
- Granular materials
    
- Fluid-solid interaction
    

Deliverables:

- Expanded physics library
    
- Modular force system
    

---

# Phase VI — Research Platform

Goals:

- Reproducible experiments
    
- Scientific workflows
    
- Dataset generation
    
- Large-scale studies
    

Deliverables:

- Benchmark repository
    
- Export pipelines
    
- Research-grade documentation
    

---

# Long-Term Possibilities

Potential future directions include:

- Astrophysical SPH
    
- Magnetohydrodynamics
    
- Plasma approximations
    
- Geophysical flows
    
- Hybrid particle-grid methods
    

These are exploratory goals and not part of the current development roadmap.

---

# Development Philosophy

1. Correctness before performance.
    
2. Validation before optimization.
    
3. Simplicity before complexity.
    
4. Architecture before features.
    
5. Reproducibility before scale.
    