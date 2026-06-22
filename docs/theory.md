## Theory

## Introduction

Smoothed Particle Hydrodynamics (SPH) is a mesh-free Lagrangian method for solving continuum mechanics problems.

Instead of representing a fluid on a fixed grid, SPH discretizes the fluid into particles that move with the flow.

Each particle carries physical properties such as:

- Mass
    
- Density
    
- Velocity
    
- Pressure
    

The governing equations are solved through particle-particle interactions.

---

# Governing Equations

## Continuity Equation

Mass conservation is given by

dρ/dt = -ρ(∇·v)

which describes the evolution of density.

---

## Momentum Equation

The Navier-Stokes momentum equation is

dv/dt = -(1/ρ)∇P + ν∇²v + g

where

- P is pressure
    
- ρ is density
    
- ν is viscosity
    
- g is external acceleration
    

This equation forms the foundation of SPH force computation.

---

# SPH Approximation

Any field quantity A can be approximated using neighbouring particles:

A(r) ≈ Σ m_j (A_j/ρ_j) W(r-r_j,h)

where

- W is the smoothing kernel
    
- h is the smoothing length
    

The kernel determines the influence radius of each particle.

Only nearby particles contribute.

---

# Density Estimation

Density is computed using kernel interpolation:

ρ_i = Σ m_j W(r_ij,h)

where

r_ij = |r_i-r_j|

This produces a smooth density field from discrete particles.

---

# Pressure Model

Pressure is obtained through an equation of state.

For weakly compressible SPH:

P_i = k(ρ_i-ρ₀)

where

- k is the stiffness constant
    
- ρ₀ is the reference density
    

Pressure acts to restore density toward equilibrium.

---

# Pressure Forces

Pressure forces arise from pressure gradients.

A symmetric formulation is used:

F_i = -m Σ (P_i/ρ_i² + P_j/ρ_j²) ∇W_ij

This improves momentum conservation and numerical stability.

---

# Artificial Viscosity

Artificial viscosity stabilizes shocks and prevents particle interpenetration.

Relative motion between particles is used to construct a viscosity term:

Π_ij

which contributes an additional dissipative force.

Benefits:

- Shock handling
    
- Numerical stability
    
- Reduced oscillations
    

---

# Smoothing Kernels

A kernel must satisfy:

1. Positivity
    
2. Compact support
    
3. Normalization
    
4. Smooth differentiability
    

Common kernels:

## Poly6

Used for density estimation.

## Spiky

Used for pressure gradients.

## Cubic Spline

Widely used general-purpose kernel.

---

# Neighbour Search

Efficient neighbour search is essential.

Without optimization:

O(N²)

With spatial hashing:

Approximately O(Nk)

where k is the average neighbour count.

This enables large particle simulations.

---

# Boundary Conditions

Boundaries introduce additional forces that prevent particle escape.

Methods include:

- Reflective boundaries
    
- Ghost particles
    
- Dynamic collision surfaces
    

The current implementation uses reflective walls.

---

# Time Integration

The particle state evolves through:

dr/dt = v

dv/dt = a

Nereid currently uses Velocity Verlet integration due to its balance of stability and computational cost.

---

# Limitations of Classical WCSPH

Weakly Compressible SPH remains attractive due to simplicity but introduces:

- Density fluctuations
    
- Time-step restrictions
    
- Artificial compressibility
    

These motivate modern formulations such as:

- PCISPH
    
- IISPH
    
- DFSPH
    

which form part of Nereid's long-term roadmap.