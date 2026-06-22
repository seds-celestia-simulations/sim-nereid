import random
import os
import numpy as np
import pyglet
import math
import time as CPUTime
from pyglet import clock
import sys

screen_width = 800
screen_height = 600


sim_config = {
    "smoothing_radius": 10.0,
    "pressure_k": 500.0,
    "target_density": 0,
    "pressure_multiplier": 0
}

ORIGIN = np.array([screen_width / 2, screen_height / 2])
win = pyglet.window.Window(screen_width, screen_height, caption="Balls")

main_batch = pyglet.graphics.Batch()
dt = 0.01

class Profiler:
    def __init__(self):
        self.timings = {}
        self.start_time = 0

    def start(self):
        self.start_time = CPUTime.perf_counter()

    def stop(self, name):
        elapsed = (CPUTime.perf_counter() - self.start_time) * 1000  # ms
        self.timings[name] = self.timings.get(name, elapsed) * 0.9 + elapsed * 0.1


    def display(self, frame_counter=1):
        print("\n--- Frame Performance (ms) ---")
        total_time = sum(self.timings.values())
        print(f"{'Total':<30}: {total_time/frame_counter:.3f} ms")
        print("-"*40)
        for name, timing in sorted(self.timings.items()):
            print(f"{name:<30}: {timing/frame_counter:.3f} ms")
        print(f"FPS: {1000/total_time}")
        print("-"*40)
    
    def total_time(self):
        total_time = 0
        for name, timing in sorted(self.timings.items()):
            total_time+=timing
        return total_time

profiler = Profiler()
frame_counter = 0

class SPHSim:
    def __init__(self, h, pressure_multiplier, target_density, ball_count):
        self.smoothening_radius = h
        self.pressure_multiplier = pressure_multiplier
        self.target_density = target_density
        self.ball_count = ball_count
        self.cached_distances = np.zeros((ball_count, ball_count))
        self.cell_count = int(box_attributes[0]/self.smoothening_radius +box_attributes[1]/self.smoothening_radius)
        self.start_indices = np.zeros(int(box_attributes[0]/self.smoothening_radius +box_attributes[1]/self.smoothening_radius))
        self.acceleration_array = np.zeros((self.ball_count, 2))
        self.velocity_array = np.zeros((self.ball_count, 2))
        self.position_array = np.zeros((self.ball_count, 2))



class ball():
    def __init__(self, radius, number, p=(0, 0), v=(0, 0), a=(0, 0), m=20, batch=main_batch, name=None, density=1):
        self.m = m
        self.name = name
        self.no = number
        self.v = np.array(v, dtype=float)
        self.a = np.array(a, dtype=float)
        self.p = np.array(p, dtype=float)
        self.r = radius
        self.smoothradius = radius
        self.sprite = pyglet.shapes.Circle(*(ORIGIN + self.p), radius, color = (0,0,255), batch=batch)
        self.density = density

    def update_parameters(self, dt):
        global time
        if self.m == 0:
            return
        self.p += self.v * dt
        self.v += self.a * dt                       #Currently uttilising Euler integration
        self.sprite.position = ORIGIN + self.p


#box_attributes = [600, 400, 5]
box_attributes = [200,150,5]          #width height thickness

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

ball_list = []
if (len(sys.argv) > 1): 
    ball_count = int(sys.argv[1])
for i in range(ball_count):
    rand_x = random.randrange(-90, 90)  
    rand_y = random.randrange(-70, 70)
    rand_v = (10*random.uniform(-1,1), 10*random.uniform(-1,1))
    ball_list.append(ball(3, i, p=(rand_x, rand_y), v = rand_v))


Sim = SPHSim(20, 1000, 0.8, ball_count)

def vel_flip(normal, v1, v2, drag=0.85):
    return v1 - (normal * (np.dot(normal, v1) - np.dot(normal, v2))) * drag


def unit_vector(vector):
    norm = np.linalg.norm(vector)
    if norm == 0:
        return np.zeros_like(vector)
    return vector / norm


def check_collisions():
    sorted_x = sorted(ball_list, key=lambda i: i.p[0])
    i = 0
    while i + 1 < len(sorted_x):
        if np.linalg.norm(sorted_x[i].p - sorted_x[i + 1].p) < 1.1 * (sorted_x[i].r + sorted_x[i + 1].r):
            new_v1 = vel_flip(unit_vector(sorted_x[i].p - sorted_x[i + 1].p), sorted_x[i].v, sorted_x[i + 1].v)
            new_v2 = vel_flip(unit_vector(sorted_x[i + 1].p - sorted_x[i].p), sorted_x[i + 1].v, sorted_x[i].v)
            sorted_x[i].v = new_v1
            sorted_x[i + 1].v = new_v2
            i += 2
        else:
            i += 1


def check_box_collisions():
    for i in ball_list:
        if (np.abs(i.p[0]) > box_attributes[0] / 2 - i.r) and (np.abs(i.p[1]) > box_attributes[1] / 2 - i.r):
            i.v = vel_flip(np.array((0, -np.sign(i.p[1]))), i.v, -i.v)
            i.v = vel_flip(np.array((-np.sign(i.p[0]), 0)), i.v, -i.v)
        elif np.abs(i.p[0]) > box_attributes[0] / 2 - i.r and (i.p[0] * i.v[0]) > 0:
            i.v = vel_flip(np.array((-np.sign(i.p[0]), 0)), i.v, -i.v)
        elif np.abs(i.p[1]) > box_attributes[1] / 2 - i.r and (i.p[1] * i.v[1]) > 0:
            i.v = vel_flip(np.array((0, -np.sign(i.p[1]))), i.v, -i.v)


def kernel(q, h=None):             #radius = distance of particle from this position
    if h is None:
        h = Sim.smoothening_radius

    #q = np.linalg.norm(radius) / h
    normalising_constant = 10 / (7 * math.pi)
    if q < 1:
        return (normalising_constant / h ** 2) * (1 - 1.5 * q ** 2 + 0.75 * q ** 3)
    elif q < 2:
        return (normalising_constant / h ** 2) * (0.25 * (2 - q) ** 3)
    else:
        return 0


def kernel_gradient(q,direction, h=None):
    if h is None:
        h = Sim.smoothening_radius
     #q = radius / h
    normalising_constant = 10 / (7 * math.pi)
    if q < 1:
        return -direction * (normalising_constant / h ** 3) * (-3 * q + 2.25 * q ** 2)
    elif q < 2:
        return -direction * (normalising_constant / h ** 3) * (-3 * (2 - q) ** 2 / 4)
    else:
        return np.zeros(2)


def get_distance(particle1, particle2):
    distance = np.linalg.norm(particle2.p-particle1.p)
    return distance


def density_at(particle):
    density = 0
    for i in ball_list:
        distance = get_distance(particle, i)
        density += i.m * kernel(distance/Sim.smoothening_radius)

    return density


# def density_gradient_at(particle):
#     net_gradient = np.zeros(2)
#     for i in ball_list:
#         if Sim.cached_distances[particle.no][i-particle.no-1]
#         if i.p == position:
#             continue
#         net_gradient += i.m * kernel_gradient(r)
#     return net_gradient


def pressure_at(particle):
    pressure_multiplier = Sim.pressure_multiplier
    p0 = Sim.target_density
    return pressure_multiplier * (particle.density - p0)

def force_calc(particle):
    force = np.zeros(2, dtype=float)
    for j in ball_list:
        if j == particle or j.p is particle.p:
            continue
        if j.density == 0:
            continue
        avg_pressure = (pressure_at(j) + pressure_at(particle)) * 0.5

        distance = get_distance(particle, j)
        direction = (j.p-particle.p)/distance      #this is a replacement for unityvector(position) in the old calc: unit_vector(-position) * (normalising_constant / h ** 3) * (-3 * q + 2.25 * q ** 2)

        force += j.m * avg_pressure * (1 / j.density) * kernel_gradient(distance/Sim.smoothening_radius, direction)
    return -force


def update_densities():
    for i in ball_list:
        i.density = density_at(i)
def update_forces():
    for i in ball_list:
        i.a = force_calc(i)

@win.event
def on_draw():
    win.clear()
    main_batch.draw()

def update(dt):
    global ball_list
    global frame_counter
    if frame_counter >= 5:
        print(profiler.total_time())
        sys.exit()
    
    profiler.start()
    update_densities()
    profiler.stop("1. Density Calculation")

    profiler.start()
    update_forces()
    profiler.stop("2. Force Calculation")
    
    profiler.start()
    check_box_collisions()
    profiler.stop("3. Box Collisions")

    profiler.start()
    for i in ball_list:
        i.update_parameters(dt)
    profiler.stop("4. Integration")

    frame_counter += 1


if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, dt)
    pyglet.app.run()