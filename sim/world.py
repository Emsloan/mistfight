"""The world: a fixed-tick, 2D side-view physics simulation.

Coordinates: x is horizontal, y is up. The ground is the line y = 0, and a
body rests when its center sits at its own radius above that line.

Integration is semi-implicit Euler at a fixed timestep, which makes every
run deterministic by construction: the same setup always produces exactly
the same history. There is no randomness anywhere in the engine yet; when
some power eventually needs it, it will come in as a seeded generator so
determinism survives.

Ground contact uses Coulomb friction (reworked 2026-06-10, replacing the
original infinite-friction hack): a grounded body's static grip holds against
horizontal force up to friction_static * normal_force — and the normal force
includes any applied downward push, so a coin pressed into the cobbles
anchors HARDER the harder it's pushed. Past the static limit the body breaks
loose and only the weaker kinetic friction resists: stronger until
overwhelmed, then a drastic fall-off. Fixed bodies (is_fixed) are part of
the world — rail spikes, structure — and never move at all. Bodies being
driven by Legs own their contact patch for that tick and skip friction.
"""

import numpy as np

from .recording import History

GRAVITY_M_PER_S2 = 9.81

# Below this speed a grounded body counts as standing still, eligible for
# static grip. Purely numerical — keeps friction from jittering around zero.
STATIC_SPEED_EPSILON_M_PER_S = 1e-3


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
            body.driven_this_tick = False

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
            if body.is_fixed:
                # Part of the world. Forces vanish into the planet.
                body.pending_force[:] = 0.0
                body.velocity[:] = 0.0
                body.on_ground = True
                continue

            total_force = body.pending_force + np.array(
                [0.0, -GRAVITY_M_PER_S2 * body.mass_kg]
            )
            speed_before = body.velocity[0]
            body.velocity += total_force / body.mass_kg * body.local_dt_seconds

            # Ground friction (Coulomb). The legs own the contact patch on
            # ticks they drive, so friction steps aside for runners.
            if body.on_ground and not body.driven_this_tick:
                normal_force = max(0.0, -total_force[1])
                was_standing = abs(speed_before) <= STATIC_SPEED_EPSILON_M_PER_S
                if was_standing and (abs(total_force[0])
                                     <= body.friction_static * normal_force):
                    # Static grip holds: the ground cancels the shove.
                    body.velocity[0] = 0.0
                else:
                    # Sliding (or just broke loose): kinetic friction drags.
                    friction_slowdown = (body.friction_kinetic * normal_force
                                         / body.mass_kg * body.local_dt_seconds)
                    if abs(body.velocity[0]) <= friction_slowdown:
                        body.velocity[0] = 0.0
                    else:
                        body.velocity[0] -= np.sign(body.velocity[0]) * friction_slowdown

            body.position += body.velocity * body.local_dt_seconds
            body.pending_force[:] = 0.0

            # 3. Ground contact: nothing passes below the floor.
            floor_y = body.radius_m
            if body.position[1] <= floor_y:
                body.position[1] = floor_y
                if body.velocity[1] < 0.0:
                    body.velocity[1] = 0.0
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
