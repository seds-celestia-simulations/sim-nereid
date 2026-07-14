import numpy as np

#PARAMETERS CLASS
class Parameters:
    def __init__(self, mass, radius, h, pressure_multiplier, spikey_factor, target_density, dt):
        self.smoothening_radius = h
        self.pressure_multiplier = pressure_multiplier
        self.target_density = target_density
        self.spikey_factor = spikey_factor
        self.dt = dt
        self.mass = mass
        self.radius = radius


#PARTICLE DATA CLASS
class ParticleData:
    def __init__(self, count):
        self.count = count
        self.pos = np.zeros((self.count, 2), dtype=np.float32)
        self.vel = np.zeros((self.count, 2), dtype=np.float32)
        self.acc = np.zeros((self.count, 2), dtype=np.float32)
        self.density = np.zeros(self.count, dtype=np.float32)

#THE WORLD
class Domain:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        


