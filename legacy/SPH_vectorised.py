import random
import os
import numpy as np
import pyglet
from pyglet.graphics import Batch
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet import gl
import math
from numba import jit
import time as CPUTime

screen_width = 800
screen_height = 600

ORIGIN = np.array([screen_width / 2, screen_height / 2])
win = pyglet.window.Window(screen_width, screen_height, caption="Balls")

main_batch = Batch()
dt = 0.02


box_attributes = [200, 150, 5]  # width height thickness


box_b = pyglet.shapes.Rectangle(0.5 * (screen_width - 2 * box_attributes[2] - box_attributes[0]),
                                0.5 * (screen_height - 2 * box_attributes[2] - box_attributes[1]),
                                box_attributes[0] + 2 * box_attributes[2], box_attributes[2], batch=main_batch)
box_l = pyglet.shapes.Rectangle(0.5 * (screen_width - 2 * box_attributes[2] - box_attributes[0]),
                                 0.5 * (screen_height - 2 * box_attributes[2] - box_attributes[1]),
                                box_attributes[2], box_attributes[1] + 2 * box_attributes[2], batch=main_batch)
box_t = pyglet.shapes.Rectangle(0.5 * (screen_width - 2 * box_attributes[2] - box_attributes[0]),
                                0.5 * (screen_height - 0 * box_attributes[2] + box_attributes[1]),
                                box_attributes[0] + 2 * box_attributes[2], box_attributes[2], batch=main_batch)
box_r = pyglet.shapes.Rectangle(0.5 * (screen_width - 0 * box_attributes[2] + box_attributes[0]),
                                0.5 * (screen_height - 2 * box_attributes[2] - box_attributes[1]),
                                box_attributes[2], box_attributes[1] + 2 * box_attributes[2], batch=main_batch)


class SPHSim:
    def __init__(self, h, pressure_multiplier, spikey_factor, target_density, ball_count):
        self.smoothening_radius = h
        self.pressure_multiplier = pressure_multiplier
        self.target_density = target_density
        self.ball_count = ball_count
        self.cached_distances = np.zeros((ball_count, ball_count))
        self.cell_count = int((box_attributes[0] / self.smoothening_radius) * (box_attributes[1] / self.smoothening_radius))
        self.start_indices = {}
        self.acceleration_array = np.zeros((self.ball_count, 2), dtype=float)
        self.velocity_array = np.zeros((self.ball_count, 2), dtype=float)
        self.position_array = np.zeros((self.ball_count, 2), dtype=float)
        self.density_array = np.zeros(self.ball_count, dtype=float)
        self.distance_count = 0
        self.chunk_cache = {}
        self.vertex_list = None
        self.spiky_factor = spikey_factor # instead of having a different h for spikey kernelits simply h*spikeyfactor to avoid code changes

    def update_parameters(self):
        self.velocity_array += self.acceleration_array * dt  # Currently utilising Euler Integration
        self.position_array += self.velocity_array * dt

Sim = SPHSim(7, 8000, 1,1, 2000)


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


profiler = Profiler()
frame_counter = 0

class ball():
    def __init__(self, number, radius = 5, m=20, batch=main_batch, name=None, density=1):
        self.m = m
        self.name = name
        self.no = number
        self.r = radius

    def p(self):
        return Sim.position_array[self.no]

    def v(self):
        return Sim.velocity_array[self.no]

    def a(self):
        return Sim.acceleration_array[self.no]

    def density(self):
        return Sim.density_array[self.no]


ball_list = []


all_positions = []
all_colors = []
for i in range(Sim.ball_count):
    rand_x = random.uniform(-20, 20)
    rand_y = random.uniform(-30, 30)
    rand_v = (0 * random.uniform(-1, 1), 0 * random.uniform(-1, 1))
    Sim.position_array[i] = np.array((rand_x, rand_y))
    Sim.velocity_array[i] = np.array(rand_v)

    all_positions.extend([ORIGIN[0] + rand_x, ORIGIN[1] + rand_y, 0])
    all_colors.extend([0, 0, 255])
    ball_list.append(ball(i))



vertex_shader = Shader("""
#version 330
in vec3 position;
in vec3 color;
out vec3 v_color;

void main()
{
    // convert from pixel space to normalized screen space
    vec2 norm;
    norm.x = (position.x / 800.0) * 2.0 - 1.0;
    norm.y = (position.y / 600.0) * 2.0 - 1.0;

    gl_Position = vec4(norm, 0.0, 1.0);
    gl_PointSize = 6.0;
    v_color = color;
}
""", 'vertex')

fragment_shader = Shader("""
#version 330
in vec3 v_color;
out vec4 fragColor;

void main()
{
    fragColor = vec4(v_color, 1.0);
}
""", 'fragment')

program = ShaderProgram(vertex_shader, fragment_shader)

Sim.vertex_list = program.vertex_list(
    Sim.ball_count,
    gl.GL_POINTS,
    batch=main_batch,
    position=('f', all_positions),
    color=('Bn', all_colors)
)

# Set the point size for the vertices
size = 12
pyglet.gl.glPointSize(size)
ball_count = len(ball_list)


def update_sprite_positions():
    """A single, fast call to update all particle positions on the screen."""
    # Create a flat list of all positions, interleaving x, y, and z
    # The z-coordinate is always 0 for our 2D simulation
    positions_3d = np.hstack((Sim.position_array + ORIGIN, np.zeros((Sim.ball_count, 1))))

    # Update the vertex list's position data in one go
    Sim.vertex_list.position[:] = positions_3d.ravel()


def vel_flip(normal, v1, v2, drag=0.7):
    return v1 - (normal * (np.dot(normal, v1) - np.dot(normal, v2))) * drag


def unit_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return np.zeros_like(vector)
    return vector / norm


def check_collisions():
    sorted_x = sorted(ball_list, key=lambda i: i.p()[0])
    i = 0
    while i + 1 < len(sorted_x):
        if np.linalg.norm(sorted_x[i].p() - sorted_x[i + 1].p()) < 1.1 * (sorted_x[i].r + sorted_x[i + 1].r):
            new_v1 = vel_flip(unit_vector(sorted_x[i].p() - sorted_x[i + 1].p()), sorted_x[i].v(), sorted_x[i + 1].v())
            new_v2 = vel_flip(unit_vector(sorted_x[i + 1].p() - sorted_x[i].p()), sorted_x[i + 1].v(), sorted_x[i].v())
            Sim.velocity_array[sorted_x[i].no] = new_v1
            Sim.velocity_array[sorted_x[i+1].no] = new_v2
            i += 2
        else:
            i += 1


def check_box_collisions(DAMPING_COEFFICIENT = -0.5 ):

    out_of_left_boundary = Sim.position_array[:, 0] < -box_attributes[0]/2 + size/2
    out_of_right_boundary = Sim.position_array[:, 0] > box_attributes[0]/2 - size/2
    out_of_bottom_boundary = Sim.position_array[:, 1] < -box_attributes[1]/2 + size/2
    out_of_top_boundary = Sim.position_array[:, 1] > box_attributes[1]/2 - size/2

    Sim.velocity_array[out_of_left_boundary, 0] *= DAMPING_COEFFICIENT
    Sim.position_array[out_of_left_boundary, 0] = -box_attributes[0]/2 + size/2

    Sim.velocity_array[out_of_right_boundary, 0] *= DAMPING_COEFFICIENT
    Sim.position_array[out_of_right_boundary, 0] = box_attributes[0]/2 - size/2

    Sim.velocity_array[out_of_bottom_boundary, 1] *= DAMPING_COEFFICIENT
    Sim.position_array[out_of_bottom_boundary, 1] = -box_attributes[1]/2 + size/2

    Sim.velocity_array[out_of_top_boundary, 1] *= DAMPING_COEFFICIENT
    Sim.position_array[out_of_top_boundary, 1] = box_attributes[1]/2 - size/2

def cell_key(position):
    grid_w = box_attributes[0] // Sim.smoothening_radius

    # Shift world position relative to the box's corner
    grid_x = int((position[0] + box_attributes[0] / 2) / Sim.smoothening_radius)
    grid_y = int((position[1] + box_attributes[1] / 2) / Sim.smoothening_radius)

    return int(grid_y * grid_w + grid_x)

# xth index corresponds to the place where x cell index starts in ball list and total no of indices is total no of cels
def generate_start_indices(ball_list_sorted):
    start_indices = {}
    if not ball_list_sorted:
        return start_indices

    current_key = cell_key(ball_list_sorted[0].p())
    start_indices[current_key] = 0

    for i in range(1, len(ball_list_sorted)):
        key = cell_key(ball_list_sorted[i].p())

        if key != current_key:
            start_indices[key] = i
            current_key = key

    return start_indices


def get_nbhd_jit(i, j, start_array_indices, particles_id_list, particles_key_list, grid_w, grid_h): #particle list is the list after the ball_list has been sorted with either the ball.nos or ball.keys
    neighbourhood_ids = np.zeros(len(particles_key_list), dtype=np.int32)
    cell_ids = np.zeros(len(particles_key_list), dtype=np.int32)
    neighbor_count = 0
    cell_count = 0

    for x in range(i - 1, i + 2):
        for y in range(j - 1, j + 2):
            if 0 <= x < grid_w and 0 <= y < grid_h:
                key = y * grid_w + x


                start_index = start_array_indices[key] # a np array like before where the xth index corresponds to the cell with cell hash = x

                if start_index != -1:
                    for k in range(start_index, len(particles_key_list)):
                        if particles_key_list[k] != key: #particle is not part of the cell we're looking at
                            break

                        neighbourhood_ids[neighbor_count] = particles_id_list[k]
                        neighbor_count += 1

                        if x==i and y == j:

                            cell_ids[cell_count] = particles_id_list[k]
                            cell_count += 1

    return neighbourhood_ids[:neighbor_count], cell_ids[:cell_count]


def kernel_vectorized(q):
    h = Sim.smoothening_radius
    normalising_constant = 4 / (math.pi * h**2)

    res = np.zeros_like(q, dtype=float)

    mask1 = q < 1
    q1 = q[mask1]
    res[mask1] = normalising_constant * (1-q1**2)**3
    return res


def kernel_gradient_vectorized(q, diffs):
    h = Sim.smoothening_radius*Sim.spiky_factor
    normalising_constant = 10 / (math.pi * h**2)

    res = np.zeros_like(diffs, dtype=float)

    distances = q*h
    direction = diffs / (distances[:, :, np.newaxis] + 1e-9)

    mask1 = q < 1
    q1 = q[mask1]
    scalar_term1 = normalising_constant * (1-q1)**3
    res[mask1] = -direction[mask1] * scalar_term1[:, np.newaxis]

    return res


def update_chunk_densities(i, j, grid_w, grid_h, particles_keys, particles_ids, start_array_indices):

    chunk_ids, cell_ids = get_nbhd_jit(i,j, start_array_indices ,particles_ids, particles_keys, grid_w, grid_h)

    if(len(cell_ids) == 0):
        return

    cell_positions = Sim.position_array[cell_ids]
    chunk_positions = Sim.position_array[chunk_ids]

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
    q_matrix = distances/Sim.smoothening_radius

    kernel_values = kernel_vectorized(q_matrix)
    particle_mass = ball_list[0].m
    densities = np.sum(kernel_values, axis=1) * particle_mass
    Sim.density_array[cell_ids] = densities

    Sim.chunk_cache[(i, j)] = (chunk_ids, cell_ids, diffs, q_matrix)


def update_chunk_forces(i, j, grid_w, particles_keys, particles_ids, start_array_indices):

    if (i, j) not in Sim.chunk_cache:
        return
    chunk_ids, cell_ids, diffs, q = Sim.chunk_cache[(i, j)]

    if(len(cell_ids) == 0):
        return

    cell_positions = Sim.position_array[cell_ids]
    chunk_positions = Sim.position_array[chunk_ids]

    cell_velocities = Sim.velocity_array[cell_ids]
    chunk_velocities = Sim.velocity_array[chunk_ids]

    cell_densities = Sim.density_array[cell_ids]
    chunk_densities = Sim.density_array[chunk_ids]

    cell_pressures = Sim.pressure_multiplier * (cell_densities - Sim.target_density)
    chunk_pressures = Sim.pressure_multiplier * (chunk_densities - Sim.target_density)

    # diffs = cell_positions[:, np.newaxis, :] - chunk_positions[np.newaxis, :, :]
    # distances = np.linalg.norm(diffs, axis=2)
    # q = distances / Sim.smoothening_radius

    # Calculate symmetric pressure force
    epsilon = 1e-9
    pressure_term = (cell_pressures / (cell_densities ** 2 + epsilon))[:, np.newaxis] + \
                    (chunk_pressures / (chunk_densities ** 2 + epsilon))[np.newaxis, :]

    grad_values = kernel_gradient_vectorized(q/Sim.spiky_factor, diffs)
    pressure_forces_matrix = -pressure_term[:, :, np.newaxis] * grad_values

    total_acceleration = np.sum(pressure_forces_matrix, axis=1)

    # visc force =  -m*sum(X*spikey kernel) where X is viscocity term = constant*{h(vi-vj).(ri-rj)/|ri-rj|^2}/avg_density   { |ri-rj|^2 = q^2*h^2 }

    v_diff = (cell_velocities[:, np.newaxis] - chunk_velocities[np.newaxis, :]) # vi-vj
    dot_prod = np.einsum('ijk,ijk->ij', v_diff, diffs)                          # ri-rj = diffs

    mask1 = dot_prod < 0                                                        # if rel_vel is opposite to rel_direction, only then we apply visc

    mu = Sim.smoothening_radius * dot_prod / (
                q ** 2 * Sim.smoothening_radius ** 2 + 0.0001 * Sim.smoothening_radius ** 2)
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

    Sim.acceleration_array[cell_ids] += total_acceleration


@win.event
def on_draw():
    win.clear()
    main_batch.draw()

time = 0
frame_counter = 0
sim_step_counter = 0
frames_to_render = 60 * 2  # 60 FPS * 15 seconds = 900 frames
frame_interval = int(1 / (60 * dt))  # Save one frame every N simulation steps


def update(dt):
    global time, ball_list
    global sim_step_counter, frame_counter
    Sim.chunk_cache = {}
    profiler.start()
    ball_list = sorted(ball_list, key=lambda i: cell_key(i.p()))
    Sim.start_indices = generate_start_indices(ball_list)
    
    start_array_indices = np.full(Sim.cell_count, -1, dtype = np.int32)
    for key, value in Sim.start_indices.items():
        if key >= Sim.cell_count:
            print("Error, key > cell count")
        start_array_indices[key] = value
    grid_w = box_attributes[0] // Sim.smoothening_radius
    grid_h = box_attributes[1] // Sim.smoothening_radius
    particles_keys = np.array([cell_key(b.p()) for b in ball_list], dtype=np.int32)
    particles_ids = np.array([b.no for b in ball_list], dtype=np.int32)
    profiler.stop("Sorting+StartIndices")

    profiler.start()
    for j in range(int(grid_h)):
        for i in range(int(grid_w)):
            update_chunk_densities(i, j, grid_w, grid_h, particles_keys, particles_ids, start_array_indices)
    profiler.stop("Densities")

    Sim.acceleration_array.fill(0)
    Sim.acceleration_array += np.array((0, -40))[np.newaxis, :]

    profiler.start()
    for j in range(int(grid_h)):
        for i in range(int(grid_w)):
            update_chunk_forces(i, j, grid_w, particles_keys, particles_ids, start_array_indices)
    profiler.stop("Forces")

    profiler.start()
    check_box_collisions()
    profiler.stop("Boundry")
    profiler.start()
    Sim.update_parameters()
    profiler.stop("INtegration")
    update_sprite_positions()

    time += 1 * dt
    frame_counter+=1
    if (frame_counter%120):
        profiler.display()

if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, dt)
    pyglet.app.run()