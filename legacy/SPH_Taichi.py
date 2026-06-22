import random
import os
import numpy as np
import numpy.linalg.linalg
import pyglet
import math
from numba import jit
import taichi as ti
import time as CPUTime
import sys
ti.init(arch=ti.gpu)

screen_width = 800
screen_height = 600

ORIGIN = np.array([screen_width / 2, screen_height / 2])
#win = pyglet.window.Window(screen_width, screen_height, caption="Balls")

window = ti.ui.Window("Taichi SPH Simulation", (screen_width, screen_height))
canvas = window.get_canvas()

# main_batch = pyglet.graphics.Batch()
dt = ti.field(dtype=ti.f32, shape=())
dt[None] = 0.02

size = ti.field(dtype=ti.f32, shape=())
size[None] = 14


#Params and variables
smoothening_radius = ti.field(dtype = ti.f32, shape = ())
smoothening_radius[None] = 7

particle_count = ti.field(dtype = ti.i32, shape = ())
if len(sys.argv) > 1:
    particle_count[None] = int(sys.argv[1])
else:
    particle_count[None] = 100

m = ti.field(dtype = ti.f32, shape = ())
m[None] = 20


box_attributes = ti.field(dtype = ti.f32, shape = 3)
box_attributes[0], box_attributes[1], box_attributes[2]  = 140, 140, 5  # width height thickness

cell_count = ti.field(dtype = ti.i32, shape = ())
cell_count[None] = int((box_attributes[0] / smoothening_radius[None]) * (box_attributes[1] / smoothening_radius[None]))



# Taichi vectors and fields

position_field = ti.Vector.field(2, dtype = ti.f32, shape  = particle_count[None])
velocity_field = ti.Vector.field(2, dtype = ti.f32, shape  = particle_count[None])
acceleration_field = ti.Vector.field(2, dtype = ti.f32, shape  = particle_count[None])
density_field = ti.field(dtype = ti.f32, shape = particle_count[None])

# Spawn stuff
@ti.kernel
def spawn_all_particles():
    for i in range(particle_count[None]):
        rand_x = ti.random() * 80 - 40
        rand_y = ti.random() * 40 - 20
        rand_vx = ti.random() * 20 - 10
        rand_vy = ti.random() * 20 - 10
        position_field[i] = [rand_x, rand_y]
        velocity_field[i] = [rand_vx, rand_vy]

# xth index corresponds to the place where x cell index starts in ball list and total no of indices is total no of cels
start_indices = ti.field(dtype = ti.i32, shape = cell_count[None])
end_indices = ti.field(dtype = ti.i32, shape = cell_count[None])
@ti.kernel
def generate_start_indices():
    for i in range(particle_count[None]):
        key = particle_keys[i]
        if i == 0:
            start_indices[key] = i
        else:
            if particle_keys[i-1] != key:
                start_indices[key] = i
                end_indices[particle_keys[i-1]] = i         #you dont refer to key-1 cuz the previous frew keys might be empty, you check the last particle's key

    last_particle_key = particle_keys[particle_count[None] - 1]
    end_indices[last_particle_key] = particle_count[None]

@ti.kernel
def initialize_grid():
    # Reset all grid cells to -1 (empty)
    for i in range(cell_count[None]):
        start_indices[i] = -1
        end_indices[i] = -1
@ti.func
def cell_key(position):
    # Shift world position relative to the box's corner
    grid_x = ti.cast((position[0] + box_attributes[0] / 2) / smoothening_radius[None], dtype = ti.int32)
    grid_y = ti.cast((position[1] + box_attributes[1] / 2) / smoothening_radius[None], dtype = ti.int32)
    grid_w = ti.cast((box_attributes[0]) / smoothening_radius[None], dtype = ti.int32)
    #print(position, grid_x, grid_y, grid_w)

    # Use the correct ROW-MAJOR formula and ensure it's an integer
    return ti.cast(grid_y * grid_w + grid_x, dtype=ti.int32)



@ti.func
def kernel_taichi(q):
    h = smoothening_radius[None]
    normalising_constant = 4 / (math.pi * h**2)
    ker = 0.0
    if q<=1:
        ker =  normalising_constant * (1-q**2)**3
    return ker

@ti.func
def kernel_pressure_taichi(r_vec):
    ker = ti.Vector([0.0, 0.0])
    h = smoothening_radius[None]
    q = r_vec.norm()
    direction = r_vec/q
    q /= h
    normalising_constant = 10 / (math.pi * h**2)
    if q<1:
        ker = -direction*normalising_constant * (1-q)**3
    return ker

@ti.kernel
def update_densities():
    for i in range(particle_count[None]):
        ri = position_field[i]
        density_field[i] = 0

        grid_w = int(box_attributes[0] // smoothening_radius[None])
        grid_h = int(box_attributes[1] // smoothening_radius[None])

        cell_x = ti.cast((ri[0] + box_attributes[0]/2)/ smoothening_radius[None], ti.i32)
        cell_y = ti.cast((ri[1] + box_attributes[1]/2)/ smoothening_radius[None], ti.i32)

        for x in range(cell_x-1, cell_x+2):
            for y in range(cell_y - 1, cell_y + 2):
                if x<0 or y<0:
                    continue
                key = x+y*grid_w
                start = start_indices[key]
                if start == -1: #if chunk is empty skip
                    continue
                end = end_indices[key]

                for temp_j in range(start, end):
                    j = particle_ids[temp_j]
                    if cell_key(position_field[j]) != key:
                        break

                    if i == j:
                        continue
                    rj = position_field[j]
                    q = (ri - rj).norm()/smoothening_radius[None]

                    density_field[i] += m[None]*kernel_taichi(q)


debugger= ti.field(dtype = ti.f32, shape = (particle_count[None], 2))
@ti.kernel
def update_forces():
    for i in range(particle_count[None]):
        ri = position_field[i]
        acceleration_field[i] = 0

        grid_w = int(box_attributes[0] // smoothening_radius[None])
        grid_h = int(box_attributes[1] // smoothening_radius[None])

        cell_x = ti.cast((ri[0] + box_attributes[0]/2)/ smoothening_radius[None], ti.i32)
        cell_y = ti.cast((ri[1] + box_attributes[1]/2)/ smoothening_radius[None], ti.i32)
        debugger[i, 0] = cell_x
        debugger[i, 1] = cell_y

        for x in range(cell_x-1, cell_x+2):
            for y in range(cell_y - 1, cell_y + 2):
                if x<0 or y<0:
                    continue
                key = x+y*grid_w

                start = start_indices[key]
                if start == -1: #if chunk is empty skip
                    continue
                end = end_indices[key]

                for temp_j in range(start, end):
                    j = particle_ids[temp_j]
                    if cell_key(position_field[j]) != key:
                        break

                    if i == j:
                        continue
                    rj = position_field[j]

                    acceleration_field[i] += m[None]*kernel_pressure_taichi(rj-ri)

@ti.kernel
def update_parameters():
    for i in range(particle_count[None]):
        velocity_field[i] += acceleration_field[i]*dt[None]
        position_field[i] += velocity_field[i]*dt[None]


particle_render_positions = ti.Vector.field(2, dtype=ti.f32, shape=particle_count[None]) # New field
@ti.kernel
def render():
    scale_factor = ti.Vector([1.0 / box_attributes[0], 1.0 / box_attributes[1]])
    origin = ti.Vector([0.5, 0.5])
    for i in position_field:
        particle_render_positions[i] = origin + position_field[i] * scale_factor


@ti.kernel
def check_box_collisions():
    DAMPING_COEFFICIENT = 0.5
    for i in range(particle_count[None]):
        if position_field[i][0] < -box_attributes[0]/2 + size[None]/2:
            position_field[i][0] = -box_attributes[0]/2 + size[None]/2
            velocity_field[i][0] *= -DAMPING_COEFFICIENT

        if position_field[i][0] > box_attributes[0]/2 - size[None]/2:
            position_field[i][0] = box_attributes[0]/2 - size[None]/2                    # flaw, doesnt check if vel is radially outwards from the origin, assummes that it is
            velocity_field[i][0] *= -DAMPING_COEFFICIENT

        if position_field[i][1] < -box_attributes[1]/2 + size[None]/2:
            position_field[i][1] = -box_attributes[1]/2 + size[None]/2
            velocity_field[i][1] *= -DAMPING_COEFFICIENT

        if position_field[i][1] > box_attributes[1]/2 - size[None]/2:
            position_field[i][1] = box_attributes[1]/2 - size[None]/2
            velocity_field[i][1] *= -DAMPING_COEFFICIENT



particle_keys = ti.field(ti.i32, shape=(particle_count[None]))
particle_ids = ti.field(ti.i32, shape=(particle_count[None]))
@ti.kernel
def compute_particle_keys():
    # This kernel runs in parallel for every particle
    for i in position_field:
        # Calculate the cell key for this particle
        key = cell_key(position_field[i])

        # Store the (key, value) pair
        particle_keys[i] = key
        particle_ids[i] = i  # original index

# @ti.kernel
# def uncouple_particle_keys(particle_keys):
#     sorted_id_list = ti.field(dtype = ti.int32, shape = particle_count[None])
#     for i in range(particle_count):
#         sorted_id_list[i] = particle_keys[i][1]
#     return sorted_id_list

class Profiler:
    def __init__(self):
        self.timings = {}
        self.start_time = 0

    def start(self):
        self.start_time = CPUTime.perf_counter()

    def stop(self, name):
        elapsed = (CPUTime.perf_counter() - self.start_time) * 1000  # to ms
        self.timings[name] = self.timings.get(name, elapsed) * 0.95 + elapsed * 0.05

    def display(self):
        total_time = 0
        print("\n--- Frame Performance (ms) ---")
        for name, timing in sorted(self.timings.items()):
            print(f"{name:<25}: {timing:.3f} ms")
            total_time+=timing
        print(f"FPS: {1000/total_time}")
        print(f"Total Time: {total_time}")
        print("-" * 30)
    def total_time(self):
        total_time = 0
        for name, timing in sorted(self.timings.items()):
            total_time+=timing
        return total_time

profiler = Profiler()
frame_counter = 0
dict = {}

if __name__ == "__main__":
    spawn_all_particles()
    while window.running:
        if frame_counter >= 500:
            print(profiler.total_time())
            sys.exit()
        grid_w = box_attributes[0]/smoothening_radius[None]
        profiler.start()
        compute_particle_keys()
        ti.sync()
        ti.algorithms.parallel_sort(keys = particle_keys, values=particle_ids)

        initialize_grid()
        generate_start_indices()
        profiler.stop("SpHash")

        profiler.start()
        update_densities()
        ti.sync()
        profiler.stop("Density")

        profiler.start()
        update_forces()
        ti.sync()
        profiler.stop("FOrces")

        profiler.start()
        check_box_collisions()
        ti.sync()
        profiler.stop("Boundry")

        profiler.start()
        update_parameters()
        ti.sync()
        profiler.stop("Integration")

        frame_counter +=1

        render()
        canvas.set_background_color((0, 0.1, 0.1))
        canvas.circles(particle_render_positions, radius=0.01, color=(0.0, 0.0, 1.0)) # Draw all circles
        window.show()