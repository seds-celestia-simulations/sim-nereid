# Fluid Simulation using SPH

This repository contains a 3D fluid simulation built from scratch using the **Smoothed Particle Hydrodynamics (SPH)** technique.

---

## Demonstration

<img width="216" height="384" alt="SPH_GIF" src="https://github.com/user-attachments/assets/ec2a6069-63c5-4404-a585-90ae83e4aa3d" /> <img width="600" height="384" alt="fluid_sim_15k - Trim" src="https://github.com/user-attachments/assets/d9c53b01-a626-4662-8f69-81bab90abd87" />


---

## What is SPH?

**Smoothed Particle Hydrodynamics (SPH)** is a mesh-free, Lagrangian method used to simulate fluid flows. Instead of tracking fluid properties on a fixed spatial grid (Eulerian approach), SPH tracks physical properties such as mass, density, velocity, and pressure directly on moving particles.

The fundamental principle of SPH is the **Smoothing Kernel** ($W$). The value of any physical property $A$ at a specific point $\mathbf{r}$ is interpolated by summing the contributions of neighboring particles weighted by this kernel function over a characteristic smoothing length $h$:

$$A(\mathbf{r}) \approx \sum_{j} m_j \frac{A_j}{\rho_j} W(\mathbf{r} - \mathbf{r}_j, h)$$

### Mathematical Core
The simulation solves the Navier-Stokes equations for fluid dynamics by breaking them down into three primary particle-particle interactions:
1. **Density & Pressure:** Particle density $\rho_i$ is calculated using the smoothing kernel. Pressure $P_i$ is then derived using an equation of state (e.g., ideal gas law approximation) to generate repulsive forces that prevent fluid compression.
2. **Viscosity:** A friction-like force acting between particles to simulate fluid thickness and damp internal velocities, modeled using a specialized viscosity smoothing kernel.
3. **External Forces:** Gravity and rigid boundary collisions.

---

## How was it Implemented?

The project is engineered to balance physical accuracy with computational performance. 

### Tech Stack
* **Language:** Python
* **Libraries:** NumPy, Pyglet

### Architectural Details & Optimizations
* **Spatial Hashing / Grid-Based Neighbor Search:** A naive neighbor lookup takes $O(N^2)$ time. To achieve real-time performance, we implemented a 3D uniform grid spatial partitioning system. Particles are mapped to grid cells of size $h$, reducing the neighbor lookup complexity to a localized $O(N)$ operations.
* **Numerical Integration:** Uses the **Velocity Verlet** integration scheme for stable particle state updates across discrete time steps ($\Delta t$).
* **Boundary Handling:** Implemented using reflective impulse forces combined with positional corrections to prevent particles from escaping the containment boundaries.
---

---

## Installation

> [!WARNING]
> **Pyglet Compatibility Note:** This simulation relies on specific window management APIs that may not be compatible with the latest versions of `pyglet`. If you encounter launch or display issues, please isolate the project inside a virtual environment using the versions provided in `requirements.txt`.

### Prerequisites
Ensure you have Python 3.x installed on your machine.

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/h-livv/sim-fluid-sph.git
   cd sim-fluid-sph

2. Create and activate a virtual environment (Recommended):
   * Windows:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
    * macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
  ```bash
   pip install -r requirements.txt
  ```

4. Run the simulation:
  ```bash
  python sph.py
  ```

## Next steps
* Clean code: Strip the code down to the core essential functions and implement TODOs.
* GPU Acceleration: Implement parallel computing using libraries like Taichi.
* Laminar flow: Develop laminar flow and explore applications.

## Credits
- Based on the initial project by [Aditya Melinkeri](https://github.com/AMVS24) - [SPH-Simulation](https://github.com/AMVS24/SPH-Simulation) developed at SEDS Celestia, BITS Goa.<br>
- Refined and presented by [Aditya Melinkeri](https://github.com/AMVS24), [Harliv Singh](https://github.com/h-livv), and [Tanya Bahrani](https://github.com/tan-coding) for the final project demo.<br>

## References
- [Coding Adventure: Simulating Fluids](https://www.youtube.com/watch?v=rSKMYc1CQHE) - An excellent implementation of SPH.
- Müller, M., Charypar, D., & Gross, M. (2003). *Particle-Based Fluid Simulation for Interactive Applications*. [PDF](https://matthias-research.github.io/pages/publications/sca03.pdf)
