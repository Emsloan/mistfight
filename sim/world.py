"""The world: a fixed-tick, 2D side-view physics simulation.

Coordinates: x is horizontal, y is up. The ground is the line y = 0, and a
body rests when its center sits at its own radius above that line.

Integration is semi-implicit Euler at a fixed timestep, which makes every
run deterministic by construction: the same setup always produces exactly
the same history. There is no randomness anywhere in the engine yet; when
some power eventually needs it, it will come in as a seeded generator so
determinism survives.

Ground contact is deliberately crude for now: a grounded body's horizontal
velocity is zeroed, which acts like infinite static friction. That is what
makes a coin on the ground an anchor. If sliding ever matters, this is the
line to revisit.
"""

import numpy as np

from .recording import History

GRAVITY_M_PER_S2 = 9.81


class World:
    def __init__(self, dt_seconds=1.0 / 240.0):
        self.dt_seconds = float(dt_seconds)
        self.time_seconds = 0.0
        self.bodies = []
        self.powers = []   # components with tick(dt) or apply_forces()
        self.bubbles = []  # SpeedBubble regions altering local time
        self.history = History()

    def add_body(self, body):
        self.bodies.append(body)
        return body

    def add_power(self, power):
        self.powers.append(power)
        return power

    def add_bubble(self, bubble):
        self.bubbles.append(bubble)
        return bubble

    def time_factor_at(self, position):
        for bubble in self.bubbles:
            if bubble.contains(position):
                return bubble.time_factor
        return 1.0

    def step(self):
        # 0. Local time: each body experiences this tick scaled by whatever
        #    bubble contains it. Everything downstream — integration, healing,
        #    feruchemy — reads this; no other code knows bubbles exist.
        for body in self.bodies:
            body.local_dt_seconds = self.dt_seconds * self.time_factor_at(body.position)

        # 1. Powers act for this tick: state-evolving powers (feruchemy,
        #    health) expose tick(dt); pure-force powers (steelpush) expose
        #    apply_forces(). Either is fine.
        for power in self.powers:
            if hasattr(power, "tick"):
                power.tick(self.dt_seconds)
            else:
                power.apply_forces()

        # 2. Integrate each body in its own local time.
        for body in self.bodies:
            total_force = body.pending_force + np.array(
                [0.0, -GRAVITY_M_PER_S2 * body.mass_kg]
            )
            acceleration = total_force / body.mass_kg
            body.velocity += acceleration * body.local_dt_seconds
            body.position += body.velocity * body.local_dt_seconds
            body.pending_force[:] = 0.0

            # 3. Ground contact: nothing passes below the floor.
            floor_y = body.radius_m
            if body.position[1] <= floor_y:
                body.position[1] = floor_y
                if body.velocity[1] < 0.0:
                    body.velocity[1] = 0.0
                body.velocity[0] = 0.0  # crude static friction (see module docstring)
                body.on_ground = True
            else:
                body.on_ground = False

        self.time_seconds += self.dt_seconds
        self.history.record(self)

    def run(self, duration_seconds):
        """Advance the world by a duration. Returns the world for chaining."""
        step_count = round(duration_seconds / self.dt_seconds)
        for _ in range(step_count):
            self.step()
        return self
