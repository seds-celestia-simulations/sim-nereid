import random
import os
import numpy as np
import numpy.linalg.linalg
import pyglet
import math
from numba import jit
from pyglet.gl import *
import json

screen_width = 800
screen_height = 600

ORIGIN = np.array([screen_width / 2, screen_height / 2, 0])
win = pyglet.window.Window(screen_width, screen_height, caption="Balls", resizable=True)
glEnable(GL_DEPTH_TEST)

@win.event
def on_resize(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(65, width / float(height), 0.1, 1000)
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED

main_batch = pyglet.graphics.Batch()
dt = 0.01


box_attributes = [200, 200, 200, 5]  # width(x) height(y) depth(z) thickness


# box_b = pyglet.shapes.Rectangle(0.5 * (screen_width - 2 * box_attributes[2] - box_attributes[0]),
#                                 0.5 * (screen_height - 2 * box_attributes[2] - box_attributes[1]),
#                                 box_attributes[0] + 2 * box_attributes[2], box_attributes[2], batch=main_batch)
# box_l = pyglet.shapes.Rectangle(0.5 * (screen_width - 2 * box_attributes[2] - box_attributes[0]),
#                                  0.5 * (screen_height - 2 * box_attributes[2] - box_attributes[1]),
#                                 box_attributes[2], box_attributes[1] + 2 * box_attributes[2], batch=main_batch)
# box_t = pyglet.shapes.Rectangle(0.5 * (screen_width - 2 * box_attributes[2] - box_attributes[0]),
#                                 0.5 * (screen_height - 0 * box_attributes[2] + box_attributes[1]),
#                                 box_attributes[0] + 2 * box_attributes[2], box_attributes[2], batch=main_batch)
# box_r = pyglet.shapes.Rectangle(0.5 * (screen_width - 0 * box_attributes[2] + box_attributes[0]),
#                                 0.5 * (screen_height - 2 * box_attributes[2] - box_attributes[1]),
#                                 box_attributes[2], box_attributes[1] + 2 * box_attributes[2], batch=main_batch)
num_x = 20
num_y = 20
num_z = 20

class SPHSim:
    def __init__(self, h, pressure_multiplier, spikey_factor, target_density, ball_count):
        self.smoothening_radius = h
        self.pressure_multiplier = pressure_multiplier
        self.target_density = target_density
        self.ball_count = num_x * num_y * num_z
        self.cell_count = int((box_attributes[0] / self.smoothening_radius) * (box_attributes[1] / self.smoothening_radius)*(box_attributes[2] / self.smoothening_radius))
        self.start_indices = {}
        self.acceleration_array = np.zeros((self.ball_count, 3), dtype=float)
        self.old_acceleration_array = np.zeros((self.ball_count, 3), dtype=float)
        self.velocity_array = np.zeros((self.ball_count, 3), dtype=float)
        self.position_array = np.zeros((self.ball_count, 3), dtype=float)
        self.density_array = np.zeros(self.ball_count, dtype=float)
        self.distance_count = 0
        self.chunk_cache = {}
        self.vertex_list = None
        self.spiky_factor = spikey_factor # instead of having a different h for spikey kernelits simply h*spikeyfactor to avoid code changes

    def update_parameters(self):
        
        self.velocity_array += 0.5*(self.acceleration_array + self.old_acceleration_array) * dt  # Currently utilising Velocity Verlet Integration
        self.position_array += self.velocity_array * dt + 0.5*self.acceleration_array*(dt*dt)

Sim = SPHSim(7, 10000, 1, 1, num_x*num_y*num_z)


class ball():
    def __init__(self, number, radius = 5, m=20, batch=main_batch, name=None, density=1):
        self.m = m
        self.name = name
        self.no = number
        # self.v = np.array(v, dtype=float)
        # self.a = np.array(a, dtype=float)
        # self.p = np.array(p, dtype=float)
        self.r = radius
        #self.sprite = pyglet.shapes.Circle(*(ORIGIN + self.p()), radius, color=(0, 0, 255), batch=batch)
        #self.density = density

    # def update_parameters(self):
    #     self.sprite.position = ORIGIN + self.p()

    def p(self):
        return Sim.position_array[self.no]

    def v(self):
        return Sim.velocity_array[self.no]

    def a(self):
        return Sim.acceleration_array[self.no]

    def density(self):
        return Sim.density_array[self.no]


ball_list = []
# for i in range(10):
#     for j in range(10):
#         ball_list.append(ball(3, p=(-50 + 10*i, -50 + 10*j), v=(0, 0)))
#
# for i in range(10):
#     rand_x = random.randrange(-box_attributes[0]/2+5, box_attributes[0]/2-5)
#     rand_y = random.randrange(-box_attributes[1]/2 + 5, box_attributes[1]/2-5)
#     rand_v = (5*random.uniform(-1,1), 5*random.uniform(-1,1))
#     ball_list.append(ball(3, p=(rand_x, rand_y), v = rand_v))         #random uniform


all_positions = []
all_colors = []
'''for i in range(Sim.ball_count):
    rand_x = random.uniform(-50, 50)
    rand_y = random.uniform(-50, 50)
    rand_z = random.uniform(-50, 50)
    rand_v = (0 * random.uniform(-1, 1), 0 * random.uniform(-1, 1),  0 * random.uniform(-1, 1))
    Sim.position_array[i] = np.array((rand_x, rand_y, rand_z))
    Sim.velocity_array[i] = np.array(rand_v)

    all_positions.extend([ORIGIN[0] + rand_x, ORIGIN[1] + rand_y,ORIGIN[2] + rand_z])
    all_colors.extend([0, 0, 255])
    ball_list.append(ball(i))'''
    
x_vals = np.linspace(-40, 40, num_x)
y_vals = np.linspace(-40, 40, num_y)
z_vals = np.linspace(-40, 40, num_z)

xx, yy, zz = np.meshgrid(x_vals, y_vals, z_vals, indexing='ij')
grid_points = np.column_stack((xx.ravel(), yy.ravel(), zz.ravel()))

offset = np.array([-50.0, 0.0, 0.0])  # start near left wall (x = -60)
impact_velocity = np.array([+200.0, -100.0, 0.0])  # shoot toward +x wall
grid_points += offset

for i in range(Sim.ball_count): 
    gx, gy, gz = grid_points[i] 
    
    vel = impact_velocity + np.random.uniform(-1.0, 1.0, size=3) * 10
    
    Sim.position_array[i] = np.array((gx, gy, gz)) 
    Sim.velocity_array[i] = vel 
    
    all_positions.extend([ORIGIN[0] + gx, ORIGIN[1] + gy, ORIGIN[2] + gz]) 
    all_colors.extend([0, 0, 255]) 
    ball_list.append(ball(i))
    
'''# === PARAMETERS ===
cube_size = 100.0
cube_half_size = cube_size / 2
offset = 45.0          # distance between centers of the two grids
block_vel = 50.0
num_x = num_y = num_z = 20
num_particles_per_block = Sim.ball_count // 2

# === CREATE GRID ===
x_vals = np.linspace(-20, 20, num_x)
y_vals = np.linspace(-20, 20, num_y)
z_vals = np.linspace(-20, 20, num_z)
xx, yy, zz = np.meshgrid(x_vals, y_vals, z_vals, indexing='ij')
grid_points = np.column_stack((xx.ravel(), yy.ravel(), zz.ravel()))

# Center the grid around (0,0,0)
grid_points -= np.mean(grid_points, axis=0)

# Create two symmetric blocks about x = 0
grid_A = grid_points[:num_particles_per_block] + np.array([-offset/2, 0, 0])
grid_B = grid_points[:num_particles_per_block] + np.array([+offset/2, 0, 0])

# Combine both
final_grid_points = np.vstack((grid_A, grid_B))

# === INITIALIZE PARTICLES ===
for i in range(Sim.ball_count):
    gx, gy, gz = final_grid_points[i]

    # Opposite velocities for each block
    if i < num_particles_per_block:
        vel = np.array([block_vel, 0, 0])
    else:
        vel = np.array([-block_vel, 0, 0])

    Sim.position_array[i] = np.array((gx, gy, gz))
    Sim.velocity_array[i] = vel

    # Screen-space position for rendering
    all_positions.extend([ORIGIN[0] + gx, ORIGIN[1] + gy, ORIGIN[2] + gz])
    all_colors.extend([0, 0, 255])
    ball_list.append(ball(i))'''



# Sim.position_array[0] = np.array((0., 0.))
# Sim.velocity_array[1] = np.array((0.,0.))
#
# Sim.position_array[0] = np.array((100., 0.))
# Sim.velocity_array[1] = np.array((20.,0.))
#
# all_positions.extend([ORIGIN[0] + 0, ORIGIN[1] + 0, 0])
# all_positions.extend([ORIGIN[0] + 10, ORIGIN[1] + 0, 0])
# all_colors.extend([0, 0, 255])
# all_colors.extend([0, 0, 255])
#
# ball_list.append(ball(0))
# ball_list.append(ball(1))


Sim.vertex_list = main_batch.add(
    Sim.ball_count,              # Number of vertices
    pyglet.gl.GL_POINTS,         # The type of primitive to draw
    None,                        # Group (not needed here)
    ('v3f', all_positions),      # 'v3f' means 3-component float vertices (x, y, z)
    ('c3B', all_colors)          # 'c3B' means 3-component byte colors (R, G, B)
)

# Set the point size for the vertices
size = 12
pyglet.gl.glPointSize(size)
ball_count = len(ball_list)
# --- ADD THIS BLOCK TO DRAW THE BOUNDING BOX ---
half_w = box_attributes[0] / 2
half_h = box_attributes[1] / 2
half_d = box_attributes[2] / 2

# Get the origin coordinates (center of the box)
ox, oy, oz = ORIGIN[0], ORIGIN[1], ORIGIN[2]

# Define the 8 corners of the cube
x0, x1 = ox - half_w, ox + half_w
y0, y1 = oy - half_h, oy + half_h
z0, z1 = oz - half_d, oz + half_d

# Define the 24 vertices for the 12 lines
box_vertices = [
    # Bottom face
    x0, y0, z0,   x1, y0, z0,  # Back
    x1, y0, z0,   x1, y0, z1,  # Right
    x1, y0, z1,   x0, y0, z1,  # Front
    x0, y0, z1,   x0, y0, z0,  # Left
    # Top face
    x0, y1, z0,   x1, y1, z0,  # Back
    x1, y1, z0,   x1, y1, z1,  # Right
    x1, y1, z1,   x0, y1, z1,  # Front
    x0, y1, z1,   x0, y1, z0,  # Left
    # Vertical edges
    x0, y0, z0,   x0, y1, z0,  # Back-Left
    x1, y0, z0,   x1, y1, z0,  # Back-Right
    x1, y0, z1,   x1, y1, z1,  # Front-Right
    x0, y0, z1,   x0, y1, z1,  # Front-Left
]

# Define the colors (24 vertices, 3 color values each, 255=white)
box_colors = [255, 255, 255] * 24

# Add the box to the main batch
main_batch.add(
    24,  # 24 vertices
    pyglet.gl.GL_LINES,
    None, # No group
    ('v3f', box_vertices),
    ('c3B', box_colors)
)
# --- END OF BLOCK ---

def update_sprite_positions():
    positions_3d = Sim.position_array + ORIGIN

    # Update the vertex list's position data in one go
    Sim.vertex_list.vertices = positions_3d.ravel()


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
    # for i in ball_list:
    #     if (np.abs(i.p()[0]) > box_attributes[0] / 2 - i.r) and (np.abs(i.p()[1]) > box_attributes[1] / 2 - i.r):
    #         Sim.velocity_array[i.no] = vel_flip(np.array((0, -np.sign(i.p()[1]))), i.v(), -i.v())
    #         Sim.velocity_array[i.no] = vel_flip(np.array((-np.sign(i.p()[0]), 0)), i.v(), -i.v())
    #     elif np.abs(i.p()[0]) > box_attributes[0] / 2 - i.r and (i.p()[0] * i.v()[0]) > 0:
    #         Sim.velocity_array[i.no] = vel_flip(np.array((-np.sign(i.p()[0]), 0)), i.v(), -i.v())
    #     elif np.abs(i.p()[1]) > box_attributes[1] / 2 - i.r and (i.p()[1] * i.v()[1]) > 0:
    #         Sim.velocity_array[i.no] = vel_flip(np.array((0, -np.sign(i.p()[1]))), i.v(), -i.v())

    out_of_left_boundary = Sim.position_array[:, 0] < -box_attributes[0]/2 + size/2
    out_of_right_boundary = Sim.position_array[:, 0] > box_attributes[0]/2 - size/2
    out_of_bottom_boundary = Sim.position_array[:, 1] < -box_attributes[1]/2 + size/2
    out_of_top_boundary = Sim.position_array[:, 1] > box_attributes[1]/2 - size/2
    out_of_back_boundary = Sim.position_array[:, 2] < -box_attributes[2]/2 + size/2
    out_of_front_boundary = Sim.position_array[:, 2] > box_attributes[2]/2 - size/2

    Sim.velocity_array[out_of_left_boundary, 0] *= DAMPING_COEFFICIENT
    Sim.position_array[out_of_left_boundary, 0] = -box_attributes[0]/2 + size/2

    Sim.velocity_array[out_of_right_boundary, 0] *= DAMPING_COEFFICIENT
    Sim.position_array[out_of_right_boundary, 0] = box_attributes[0]/2 - size/2

    Sim.velocity_array[out_of_bottom_boundary, 1] *= DAMPING_COEFFICIENT
    Sim.position_array[out_of_bottom_boundary, 1] = -box_attributes[1]/2 + size/2

    Sim.velocity_array[out_of_top_boundary, 1] *= DAMPING_COEFFICIENT
    Sim.position_array[out_of_top_boundary, 1] = +box_attributes[1]/2 - size/2

    Sim.velocity_array[out_of_front_boundary, 2] *= DAMPING_COEFFICIENT
    Sim.position_array[out_of_front_boundary, 2] = box_attributes[2]/2 - size/2

    Sim.velocity_array[out_of_back_boundary, 2] *= DAMPING_COEFFICIENT
    Sim.position_array[out_of_back_boundary, 2] = -box_attributes[2]/2 + size/2

def cell_key(position):
    grid_w = box_attributes[0] // Sim.smoothening_radius
    grid_h = box_attributes[1] // Sim.smoothening_radius

    # Shift world position relative to the box's corner
    grid_x = int((position[0] + box_attributes[0] / 2) / Sim.smoothening_radius)
    grid_y = int((position[1] + box_attributes[1] / 2) / Sim.smoothening_radius)
    grid_z = int((position[2] + box_attributes[2] / 2) / Sim.smoothening_radius)

    #print(position, grid_x, grid_y, grid_w)

    # Use the correct ROW-MAJOR formula and ensure it's an integer
    return int(grid_z*grid_w*grid_h + grid_y * grid_w + grid_x) #basically just numbering each cell from 0 till num_cells

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

    #print(start_indices)
    return start_indices


@jit(nopython=True)
def get_nbhd_jit(i, j, k, start_array_indices, particles_id_list, particles_key_list, grid_w, grid_h, grid_d): #particle list is the list after the ball_list has been sorted with either the ball.nos or ball.keys
    neighbourhood_ids = np.zeros(len(particles_key_list), dtype=np.int32)
    cell_ids = np.zeros(len(particles_key_list), dtype=np.int32)
    neighbor_count = 0
    cell_count = 0

    for x in range(i - 1, i + 2):
        for y in range(j - 1, j + 2):
            for z in range(k-1, k+2):
                if 0 <= x < grid_w and 0 <= y < grid_h and 0 <= z < grid_d:
                    key = z*grid_w*grid_h+y * grid_w + x

                    start_index = start_array_indices[key] # a np array like before where the xth index corresponds to the cell with cell hash = x

                    if start_index != -1:
                        for id in range(start_index, len(particles_key_list)):
                            if particles_key_list[id] != key: #particle is not part of the cell we're looking at
                                break

                            neighbourhood_ids[neighbor_count] = particles_id_list[id]
                            neighbor_count += 1

                            if x==i and y == j and z==k:

                                cell_ids[cell_count] = particles_id_list[id]
                                cell_count += 1

    return neighbourhood_ids[:neighbor_count], cell_ids[:cell_count]


def kernel_vectorized(q):
    h = Sim.smoothening_radius
    normalising_constant = 315 / (64*(math.pi * h**3))

    res = np.zeros_like(q, dtype=float)

    mask1 = q < 1
    q1 = q[mask1]
    res[mask1] = normalising_constant * (1-q1**2)**3
    return res


def kernel_gradient_vectorized(q, diffs):
    h = Sim.smoothening_radius*Sim.spiky_factor
    normalising_constant = 15 / (math.pi * h**3)

    res = np.zeros_like(diffs, dtype=float)

    distances = q*h
    direction = diffs / (distances[:, :, np.newaxis] + 1e-9)

    mask1 = q < 1
    q1 = q[mask1]
    scalar_term1 = normalising_constant * (1-q1)**3 # try changing this to gradient of sky kernel which is 45/pi*h^3(1-r)^2
    res[mask1] = -direction[mask1] * scalar_term1[:, np.newaxis]

    return res


def update_chunk_densities(i, j, k, grid_w, grid_h, grid_d, particles_keys, particles_ids, start_array_indices):
    Sim.old_acceleration_array = Sim.acceleration_array

    chunk_ids, cell_ids = get_nbhd_jit(i,j,k, start_array_indices ,particles_ids, particles_keys, grid_w, grid_h, grid_d)

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

    Sim.chunk_cache[(i, j, k)] = (chunk_ids, cell_ids, diffs, q_matrix)


def update_chunk_forces(i, j, k, grid_w, particles_keys, particles_ids, start_array_indices):
    Sim.old_acceleration_array = Sim.acceleration_array

    if (i, j, k) not in Sim.chunk_cache:
        return
    chunk_ids, cell_ids, diffs, q = Sim.chunk_cache[(i, j, k)]

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
    viscosity_force = -0.01*np.sum(pi[:, :, np.newaxis] * grad_values, axis=1)

    # Add the viscosity force to the total acceleration
    total_acceleration += viscosity_force

    Sim.acceleration_array[cell_ids] += total_acceleration


@win.event
def on_draw():
    """Clear buffers, position camera, and draw."""
    global camera_rotation  # Make sure to get the rotating variable

    # Clear both color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # --- THIS IS THE FIX ---
    # Calculate the new, rotating camera position
    # We want to orbit the center of the box, which is at ORIGIN
    rads = math.radians(camera_rotation)
    eye_x = ORIGIN[0] + 300.0 * math.sin(rads)  # 300 units away on X
    eye_y = ORIGIN[1] + 150.0  # 150 units "above" the box
    eye_z = ORIGIN[2] + 300.0 * math.cos(rads)  # 300 units away on Z

    # Position the camera
    # The "eye" is now rotating, but the "center" (target) is static.
    gluLookAt(eye_x, eye_y, eye_z,  # Camera Position (eye)
              ORIGIN[0], ORIGIN[1], 0.0,  # Look-at Point (box center)
              0.0, 1.0, 0.0)  # Up Vector

    # We don't use glRotatef() here anymore
    main_batch.draw()


time = 0
frame_counter = 0
sim_step_counter = 0
frames_to_render = 60 * 2  # 60 FPS * 15 seconds = 900 frames
frame_interval = int(1 / (60 * dt))  # Save one frame every N simulation steps

frames = []
frame_positions = []
frame_velocities = []
frames_data = []

camera_rotation = 0.0
def update(dt):
    global time, ball_list
    global sim_step_counter, frame_counter
    global frames, times, frame_positions, frame_velocities, frames_data
    Sim.chunk_cache = {}

    global camera_rotation
    camera_rotation +=  10 * dt  # Spin the camera

    ball_list = sorted(ball_list, key=lambda i: cell_key(i.p()))
    Sim.start_indices = generate_start_indices(ball_list)

    start_array_indices = np.full(Sim.cell_count, -1, dtype = np.int32)
    for key, value in Sim.start_indices.items():
        if key >= Sim.cell_count:
            print("Error, key > cell count")
        start_array_indices[key] = value
    grid_w = box_attributes[0] // Sim.smoothening_radius
    grid_h = box_attributes[1] // Sim.smoothening_radius
    grid_d = box_attributes[2] // Sim.smoothening_radius
    particles_keys = np.array([cell_key(b.p()) for b in ball_list], dtype=np.int32)
    particles_ids = np.array([b.no for b in ball_list], dtype=np.int32)

    for j in range(int(grid_h)):
        for i in range(int(grid_w)):
            for k in range(int(grid_d)):
                update_chunk_densities(i, j, k, grid_w, grid_h, grid_d, particles_keys, particles_ids, start_array_indices)

    Sim.acceleration_array.fill(0)
    Sim.acceleration_array += np.array((0, -200, 0))[np.newaxis, :]
    #Sim.acceleration_array += np.array((10*math.sin(1*time), 0))[np.newaxis, :]

    for j in range(int(grid_h)):
        for i in range(int(grid_w)):
            for k in range(int(grid_d)):
                update_chunk_forces(i, j, k, grid_w, particles_keys, particles_ids, start_array_indices)


    check_box_collisions()
    Sim.update_parameters()

    update_sprite_positions()

    time += 1 * dt

    print("Density: ", ball_list[0].density())
    #print("Acc: ", ball_list[30].a())
    #print("Position: ", ball_list[30].p())
    total_energy = np.sum(np.linalg.norm(Sim.velocity_array), axis=0)
    print(f"Energy: {total_energy}")


    #print(pyglet.clock.get_fps())
    sim_step_counter += 1

    frame_info = {
        "frame":sim_step_counter,
        "time":time,
        "positions":Sim.position_array.tolist(),
        "velocities": Sim.velocity_array.tolist()}

    frames_data.append(frame_info)
    if sim_step_counter % 2 == 0:
        #pyglet.image.get_buffer_manager().get_color_buffer().save(f"{frame_counter:04d}.png")
        frame_counter += 1
        #print(f"Saved frame {frame_counter}")
        json_filename = f"{frame_counter:04d}.json"
        frame_data = {
            "frame_number": frame_counter,
            "particle_count": Sim.ball_count,
            "positions": Sim.position_array.tolist(),
            "velocities": Sim.velocity_array.tolist(),
         }
        try:
           with open(json_filename, 'w') as f:
               json.dump(frame_data, f, indent=4)  # indent=4 makes it human-readable
           print(f"Saved JSON data {json_filename}")
        except Exception as e:
             print(f"Error saving JSON file: {e}")
    '''if frame_counter >= frames_to_render:
        print("Finished rendering.")
        pyglet.app.exit()
    # Debugging output (you can remove this)'''

    if np.isnan(Sim.position_array).any():
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!! NaN DETECTED IN PARTICLE POSITIONS  !!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            
'''@win.event
def on_close():
    with open("fluid_sim_info.json", "w") as f:
        json.dump(frames_data, f, indent =2)
        
    print("Information exported")'''
    
if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, dt)
    pyglet.app.run()