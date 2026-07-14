from core.data import Parameters, ParticleData, Domain
from rendering.renderer import Renderer
from spatial.spatialdata import SpatialData
from physics.solver import Solver
from physics.kernel import Kernel
from core.integrators import Integrator
from diagnostics.profiler import Profiler
from core.simulation import Simulation
import pyglet


#MAIN FUNCTION
def main():
    domain = Domain(400, 500)
    params = Parameters(20, 15, 10, 8000, 1, 2, 0.02)
    particles = ParticleData(2000)
    spatial = SpatialData(particles.count, params.smoothening_radius, domain)
    kernel = Kernel(params)
    solver = Solver(particles, params, spatial, kernel)
    integrator = Integrator(particles, params)
    profiler = Profiler()
    sim = Simulation(params, particles, spatial, solver, integrator, profiler, domain)
    renderer = Renderer(10, domain, sim)

    sim.initialize_particles()
    renderer.initialize(particles)


    def update(dt):

        profiler.start()

        if not sim.paused:
            sim.update()

        renderer.update(particles, sim, profiler)
        profiler.stop("Rendering")

        profiler.display()

    pyglet.clock.schedule_interval(update, params.dt)   

if __name__ == "__main__":
    main()
    pyglet.app.run()


