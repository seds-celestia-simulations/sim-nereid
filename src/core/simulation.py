import numpy as np

#SIMULATION CLASS
'''
Initialises particles
Checks for box collisions
Applies gravity
Initialises spatial hashing
Updates particles
'''

class Simulation:
    def __init__(self, params, particles, spatial, solver, integrator, profiler, domain):
        self.params = params
        self.particles = particles
        self.spatial = spatial
        self.solver = solver
        self.integrator = integrator
        self.profiler = profiler
        self.time = 0
        self.domain = domain
        self.paused = False


    def initialize_particles(self):
        self.particles.pos[:, 0] = np.random.uniform(-20, 20, self.particles.count)
        self.particles.pos[:, 1] = np.random.uniform(-30, 30, self.particles.count)
        self.particles.vel[:, 0].fill(75)
        self.particles.vel[:, 1].fill(-75)
        

    def check_box_collisions(self, DAMPING_COEFFICIENT = -0.5):

        out_of_left_boundary = self.particles.pos[:, 0] < -self.domain.width/2 + self.params.radius/2
        out_of_right_boundary = self.particles.pos[:, 0] > self.domain.width/2 - self.params.radius/2
        out_of_bottom_boundary = self.particles.pos[:, 1] < -self.domain.height/2 + self.params.radius/2
        out_of_top_boundary = self.particles.pos[:, 1] > self.domain.height/2 - self.params.radius/2

        self.particles.vel[out_of_left_boundary, 0] *= DAMPING_COEFFICIENT
        self.particles.pos[out_of_left_boundary, 0] = -self.domain.width/2 + self.params.radius/2

        self.particles.vel[out_of_right_boundary, 0] *= DAMPING_COEFFICIENT
        self.particles.pos[out_of_right_boundary, 0] = self.domain.width/2 - self.params.radius/2

        self.particles.vel[out_of_bottom_boundary, 1] *= DAMPING_COEFFICIENT
        self.particles.pos[out_of_bottom_boundary, 1] = -self.domain.height/2 + self.params.radius/2

        self.particles.vel[out_of_top_boundary, 1] *= DAMPING_COEFFICIENT
        self.particles.pos[out_of_top_boundary, 1] = self.domain.height/2 - self.params.radius/2

    def apply_gravity(self):
        self.particles.acc.fill(0)
        self.particles.acc += np.array((0, -50))[np.newaxis, :]

    def update(self):

        self.profiler.start()
        self.spatial.build(self.particles)
        self.profiler.stop("Spatial")

        self.profiler.start()
        self.solver.compute_density()
        self.profiler.stop("Density")

        self.profiler.start()
        self.apply_gravity()
        self.profiler.stop("Gravity")

        self.profiler.start()
        self.solver.compute_forces()
        self.profiler.stop("Forces")

        self.profiler.start()
        self.check_box_collisions()
        self.profiler.stop("Boundary")

        self.profiler.start()
        self.integrator.step()
        self.profiler.stop("Integration")

        self.time += self.params.dt

    def reset(self):

        self.time = 0

        self.initialize_particles()


#PARTICLE-PARTICLE COLLISIONS
'''
def vel_flip(normal, v1, v2, drag=0.7):
    return v1 - (normal * (np.dot(normal, v1) - np.dot(normal, v2))) * drag

def unit_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return np.zeros_like(vector)
    return vector / norm


def check_collisions():
    sorted_x = sorted(particles.pos, key=lambda i: i[0])
    i = 0
    while i + 1 < len(sorted_x):
        if np.linalg.norm(sorted_x[i] - sorted_x[i + 1]) < 1.1 * (params.radius + params.radius):
            new_v1 = vel_flip(unit_vector(sorted_x[i] - sorted_x[i + 1]), particles.vel[i], particles.vel[i + 1])
            new_v2 = vel_flip(unit_vector(sorted_x[i + 1] - sorted_x[i]), particles.vel[i + 1], particles.vel[i])
            particles.vel[i] = new_v1
            particles.vel[i+1] = new_v2
            i += 2
        else:
            i += 1
'''