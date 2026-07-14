import math
import numpy as np

#KERNEL CLASS
'''
Calculates kernel values and gradients
'''
class Kernel:
    def __init__(self, params):
        self.params = params
    
    def kernel_vectorized(self, q):
        normalising_constant = 4 / (math.pi * self.params.smoothening_radius**2)

        res = np.zeros_like(q, dtype=float)

        mask1 = q < 1
        q1 = q[mask1]
        res[mask1] = normalising_constant * (1-q1**2)**3
        return res


    def kernel_gradient_vectorized(self, q, diffs):
        normalising_constant = 10 / (math.pi * self.params.smoothening_radius**2)

        res = np.zeros_like(diffs, dtype=float)

        distances = q*self.params.smoothening_radius
        direction = diffs / (distances[:, :, np.newaxis] + 1e-9)

        mask1 = q < 1
        q1 = q[mask1]
        scalar_term1 = normalising_constant * (1-q1)**3
        res[mask1] = -direction[mask1] * scalar_term1[:, np.newaxis]

        return res