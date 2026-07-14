#INTEGRATOR CLASS
class Integrator:
    def __init__(self, particles, params):
        self.particles = particles
        self.params = params
        self.dt = self.params.dt

    def euler(self):
        self.particles.vel += self.particles.acc * self.dt
        self.particles.pos += self.particles.vel * self.dt

    def step(self):
        self.euler()