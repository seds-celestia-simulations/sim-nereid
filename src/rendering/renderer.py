import pyglet
from pyglet import gl
from pyglet.graphics import Batch
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import key

from enum import Enum
import datetime
from pathlib import Path

import numpy as np

class Visualization(Enum):
    SOLID = 0
    VELOCITY = 1
    DENSITY = 2

#RENDERER CLASS
'''
Renders particles
'''
class Renderer:
    def __init__(self, point_size, domain, simulation):
        self.domain = domain
        self.main_batch = None
        self.win = None

        self.origin = np.array([self.domain.width / 2, self.domain.height / 2])

        self.vertex_list = None
        self.point_size = point_size

        self.mode = Visualization.VELOCITY
        self.stats_left = None
        self.stats_right = None
        self.show_overlay = True
        self.paused = False
        self.simulation = simulation

        self.vertex_shader = Shader("""
        #version 330
        uniform float point_size;
        uniform vec2 screen_size;
        in vec3 position;
        in vec3 color;
        out vec3 v_color;
        in float scalar;
        out float v_scalar;

        void main()
        {
            // convert from pixel space to normalized screen space
            vec2 norm;
            norm = (position.xy / screen_size) * 2.0 - 1.0;

            gl_Position = vec4(norm, 0.0, 1.0);
            gl_PointSize = point_size;
            v_color = color;
            v_scalar = scalar;
        }
        """, 'vertex')

        self.fragment_shader = Shader("""
        #version 330

        in vec3 v_color;
        in float v_scalar;

        out vec4 fragColor;

        void main()
        {
            vec2 coord = gl_PointCoord * 2.0 - 1.0;
            float r = length(coord);

            if (r > 1.0)
                discard;

            float alpha = 1.0 - smoothstep(0.90, 1.0, r);

            float shade = 1.0 - 0.0 * r;

            float s = clamp(v_scalar, 0.0, 1.0);

            vec3 slow = vec3(0.15, 0.25, 1.00);
            vec3 fast = vec3(0.25, 0.55, 1.00);

            vec3 color = mix(slow, fast, s);

            fragColor = vec4(color, alpha);
        }
        """, 'fragment')
        
        self.program = ShaderProgram(self.vertex_shader, self.fragment_shader)
        self.program["point_size"] = float(self.point_size)
        self.program["screen_size"] = (
    float(self.domain.width),
    float(self.domain.height),
)

    def initialize(self, particles):
        self.win = pyglet.window.Window(self.domain.width, self.domain.height, caption="Nereid")

        self.main_batch = Batch()

        self.overlay_bg = pyglet.shapes.Rectangle(
            5,
            self.domain.height - 210,
            390,
            205,
            color=(20, 20, 20),
        )

        self.overlay_bg.opacity = 170
    
        positions = []
        colors = []

        for i in range(particles.count):
            positions.extend([self.origin[0] + particles.pos[i, 0], self.origin[1] + particles.pos[i, 1], 0])
            colors.extend([0, 0, 255])

        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        scalars = np.zeros(particles.count, dtype=np.float32)

        self.vertex_list = self.program.vertex_list(
            particles.count,
            gl.GL_POINTS,
            batch=self.main_batch,
            position=('f', positions),
            color=('Bn', colors),
            scalar=('f', scalars)
        )

        self.win.on_draw = self.on_draw

        self.stats_left = pyglet.text.Label(
            "",
            font_name="Consolas",
            font_size=10,
            x=20,
            y=self.domain.height - 20,
            anchor_x="left",
            anchor_y="top",
            multiline=True,
            width=600,
        )

        self.stats_right = pyglet.text.Label(
            "",
            font_name="Consolas",
            font_size=10,
            x=self.domain.width - 20,
            y=self.domain.height - 20,
            anchor_x="right",
            anchor_y="top",
            align="right",
            multiline=True,
            width=180,
        )

        self.win.on_key_press = self.on_key_press
                

    def update(self, particles, simulation, profiler):
        """A single, fast call to update all particle positions on the screen."""
        # Create a flat list of all positions, interleaving x, y, and z
        # The z-coordinate is always 0 for our 2D simulation
        self.positions = np.zeros((particles.count, 3), dtype=np.float32)

        self.positions[:, :2] = particles.pos
        self.positions[:, :2] += self.origin

        if self.mode == Visualization.SOLID:

            scalar = np.zeros(particles.count, dtype=np.float32)

        elif self.mode == Visualization.DENSITY:

            rho = particles.density
            rho_min = rho.min()
            rho_max = rho.max()

            scalar = (rho - rho_min) / (rho_max - rho_min + 1e-8)

        elif self.mode == Visualization.VELOCITY:

            speed = np.linalg.norm(particles.vel, axis=1)
            speed_max = np.percentile(speed, 95)

            scalar = np.clip(speed / (speed_max + 1e-8), 0.0, 1.0)


        # Update the vertex list's position data in one go
        self.vertex_list.position[:] = self.positions.ravel()
        self.vertex_list.scalar[:] = scalar.astype(np.float32)

        total = sum(profiler.timings.values())


        fps = 1000 / total if total > 0 else 0

        status = "PAUSED" if self.simulation.paused else "RUNNING"

        self.stats_left.text = (
            "NEREID\n"
            "───────────────────────────\n"
            f"{'Particles':<10}: {simulation.particles.count:>6}\n"
            f"{'Time':<10}: {simulation.time:>6.2f} s\n"
            f"{'FPS':<10}: {fps:>6.1f}\n"
            f"{'Density':<10}: {simulation.particles.density.mean():>6.2f}\n"
            f"{'Mode':<10}: {self.mode.name:>6}\n"
            f"{'Status':<10}: {status:>6}"
        )

        play_text = "Play" if self.simulation.paused else "Pause"

        self.stats_right.text = (
            "CONTROLS\n"
            "───────────────────────────\n"
            f"{'[SPACE]':<8} {play_text:>8}\n"
            f"{'[R]':<8} {'Reset':>8}\n"
            f"{'[P]':<8} {'Capture':>8}\n"
            f"{'[1]':<8} {'Solid':>8}\n"
            f"{'[2]':<8} {'Velocity':>8}\n"
            f"{'[3]':<8} {'Density':>8}\n"
            f"{'[F]':<8} {'Overlay':>8}"
        )

    def on_key_press(self, symbol, modifiers):

        if symbol == key._1:
            print("Solid")
            self.mode = Visualization.SOLID

        elif symbol == key._2:
            print("Velocity")
            self.mode = Visualization.VELOCITY

        elif symbol == key._3:
            print("Density")
            self.mode = Visualization.DENSITY

        elif symbol == key.F:
            self.show_overlay = not self.show_overlay

        elif symbol == key.SPACE:
            self.simulation.paused = not self.simulation.paused

        elif symbol == key.R:
            self.simulation.reset()

        elif symbol == key.P:

            project_root = Path(__file__).resolve().parents[2]

            screenshot_dir = project_root / "data" / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)

            filename = screenshot_dir / (
                datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
            )

            pyglet.image.get_buffer_manager().get_color_buffer().save(str(filename))

            print(f"Saved {filename}")

    def on_draw(self):
        self.win.clear()
        self.main_batch.draw()

        if self.show_overlay:
            self.overlay_bg.draw()
            self.stats_left.draw()
            self.stats_right.draw()
