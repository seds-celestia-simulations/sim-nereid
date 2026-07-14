import numpy as np

#SOLVER CLASS
'''
Computes densities and forces
'''
class Solver:
    def __init__(self, particles, params, spatial, kernel):
        self.particles = particles
        self.params = params
        self.spatial = spatial
        self.kernel = kernel

    def update_chunk_densities(self, i, j):

        chunk_ids, cell_ids = self.spatial.get_nbhd(i, j)

        if(len(cell_ids) == 0):
            return

        cell_positions = self.particles.pos[cell_ids]
        chunk_positions = self.particles.pos[chunk_ids]

        diffs = cell_positions[:, np.newaxis, :] - chunk_positions[np.newaxis, :, :]
        # eg with cell as v1, v2, v3 and chunk as w1 w2 w3 w4 w5
        # converts cell_p to shape [3,1,2] and chunk_p to [1,5, 2]

        # cell_p:[v1                 [v1 v1 v1 v1 v1]
        #         v2       ->        [v2 v2 v2 v2 v2]        THEREFORE DIFF[i][j] is vi-wj
        #         v3]                [v3 v3 v3 v3 v3]
        #
        # nb_p :[w1                  [w1 w2 w3 w4 w5]
        #        w2                  [w1 w2 w3 w4 w5]
        #        w3        ->        [w1 w2 w3 w4 w5]
        #        w4
        #        w5]
        distances = np.linalg.norm(diffs, axis=2)  # calculates magnitiude wrt third axis ie converts  to a 3x5 matrix of aij = |vi-wj|
        q_matrix = distances/self.params.smoothening_radius

        kernel_values = self.kernel.kernel_vectorized(q_matrix)
        densities = np.sum(kernel_values, axis=1) * self.params.mass
        self.particles.density[cell_ids] = densities

        self.spatial.chunk_cache[(i, j)] = (chunk_ids, cell_ids, diffs, q_matrix)

    def update_chunk_forces(self, i, j):

        if (i, j) not in self.spatial.chunk_cache:
            return
        chunk_ids, cell_ids, diffs, q = self.spatial.chunk_cache[(i, j)]

        if(len(cell_ids) == 0):
            return

        cell_velocities = self.particles.vel[cell_ids]
        chunk_velocities = self.particles.vel[chunk_ids]

        cell_densities = self.particles.density[cell_ids]
        chunk_densities = self.particles.density[chunk_ids]

        cell_pressures = self.params.pressure_multiplier * (cell_densities - self.params.target_density)
        chunk_pressures = self.params.pressure_multiplier * (chunk_densities - self.params.target_density)

        # diffs = cell_positions[:, np.newaxis, :] - chunk_positions[np.newaxis, :, :]
        # distances = np.linalg.norm(diffs, axis=2)
        # q = distances / Sim.smoothening_radius

        # Calculate symmetric pressure force
        epsilon = 1e-9
        pressure_term = (cell_pressures / (cell_densities ** 2 + epsilon))[:, np.newaxis] + \
                        (chunk_pressures / (chunk_densities ** 2 + epsilon))[np.newaxis, :]

        grad_values = self.kernel.kernel_gradient_vectorized(q/self.params.spikey_factor, diffs)
        pressure_forces_matrix = -pressure_term[:, :, np.newaxis] * grad_values

        total_acceleration = np.sum(pressure_forces_matrix, axis=1)

        # visc force =  -m*sum(X*spikey kernel) where X is viscocity term = constant*{h(vi-vj).(ri-rj)/|ri-rj|^2}/avg_density   { |ri-rj|^2 = q^2*h^2 }

        v_diff = (cell_velocities[:, np.newaxis] - chunk_velocities[np.newaxis, :]) # vi-vj
        dot_prod = np.einsum('ijk,ijk->ij', v_diff, diffs)                          # ri-rj = diffs

        mask1 = dot_prod < 0                                                        # if rel_vel is opposite to rel_direction, only then we apply visc

        mu = self.params.smoothening_radius * dot_prod / (
                    q ** 2 * self.params.smoothening_radius ** 2 + 0.0001 * self.params.smoothening_radius ** 2)
        avg_density = (cell_densities[:, np.newaxis] + chunk_densities[np.newaxis, :]) / 2
        c = 150
        # Calculate the full viscosity scalar field (Π_ij)
        pi = np.zeros_like(q)
        # Only calculate Pi for the particles that are approaching
        pi[mask1] = (-0.1 * c * mu[mask1]) / (avg_density[mask1] + epsilon)

        # Calculate the final viscosity force vector
        viscosity_force = -np.sum(pi[:, :, np.newaxis] * grad_values, axis=1)

        # Add the viscosity force to the total acceleration
        total_acceleration += viscosity_force

        self.particles.acc[cell_ids] += total_acceleration

    def compute_density(self):
        grid_w = self.spatial.grid_w
        grid_h = self.spatial.grid_h

        for j in range(int(grid_h)):
            for i in range(int(grid_w)):
                self.update_chunk_densities(i, j)

    def compute_forces(self):
        grid_w = self.spatial.grid_w
        grid_h = self.spatial.grid_h

        for j in range(int(grid_h)):
            for i in range(int(grid_w)):
                self.update_chunk_forces(i, j)