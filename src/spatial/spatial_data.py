import numpy as np

#SPATIAL DATA CLASS
'''
Stores spatial data
Calculates starting cell indices for each particle
Gets neighbourhood particles and cell indices for each particle
'''
class SpatialData:
    def __init__(self, count, h, domain):
        self.h = h
        self.domain = domain
        self.grid_w = domain.width // h
        self.grid_h = domain.height // h
        self.cached_distances = np.zeros((count, count))
        self.cell_count = int((domain.width / self.h) * (domain.height / self.h))
        self.start_array = np.full(self.cell_count, -1, dtype=np.int32)
        self.distance_count = 0
        self.chunk_cache = {}
        self.particle_ids = np.arange(count)


    def cell_key(self, position):
        grid_w = self.domain.width // self.h

        # Shift world position relative to the box's corner
        grid_x = int((position[0] + self.domain.width / 2) / self.h)
        grid_y = int((position[1] + self.domain.height / 2) / self.h)

        return int(grid_y * grid_w + grid_x)

    # xth index corresponds to the place where x cell index starts in ball list and total no of indices is total no of cels
    def generate_start_indices(self, sorted_keys):
        start_indices = {}

        if len(sorted_keys) == 0:
            return start_indices

        current_key = sorted_keys[0]
        start_indices[current_key] = 0

        for i in range(1, len(sorted_keys)):
            key = sorted_keys[i]

            if key != current_key:
                start_indices[key] = i
                current_key = key

        return start_indices

    def build(self, particles):

        self.chunk_cache.clear()

        keys = np.array([self.cell_key(pos) for pos in particles.pos], dtype=np.int32)

        self.particle_ids = np.argsort(keys).astype(np.int32)

        self.particle_keys = keys[self.particle_ids]

        self.start_array.fill(-1)

        start_indices = self.generate_start_indices(self.particle_keys)
        
        for key, value in start_indices.items():
            self.start_array[key] = value

    def get_nbhd(self, i, j): #particle list is the list after the ball_list has been sorted with either the ball.nos or ball.keys
        neighbourhood_ids = np.zeros(len(self.particle_keys), dtype=np.int32)
        cell_ids = np.zeros(len(self.particle_keys), dtype=np.int32)
        neighbor_count = 0
        cell_count = 0

        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if 0 <= x < self.grid_w and 0 <= y < self.grid_h:
                    key = y * self.grid_w + x


                    start_index = self.start_array[key] # a np array like before where the xth index corresponds to the cell with cell hash = x

                    if start_index != -1:
                        for k in range(start_index, len(self.particle_keys)):
                            if self.particle_keys[k] != key: #particle is not part of the cell we're looking at
                                break

                            neighbourhood_ids[neighbor_count] = self.particle_ids[k]
                            neighbor_count += 1

                            if x==i and y == j:

                                cell_ids[cell_count] = self.particle_ids[k]
                                cell_count += 1

        return neighbourhood_ids[:neighbor_count], cell_ids[:cell_count]