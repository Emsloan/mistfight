"""Legs: self-propulsion.

Legs drive a body horizontally while it's on the ground, accelerating its
velocity toward a target speed. On ticks the legs drive, they own the
contact patch — the world's Coulomb ground friction steps aside, because
the legs ARE the friction interaction (this is how game character
controllers work too: feet are not sliding boxes).

Airborne, legs do nothing: no air control, and what you leave the ground
with is what you fly with.

The `speed_multiplier` dial is where steel feruchemy plugs in: it scales
both top speed and acceleration (faster limbs get up to speed faster — a
stated modeling choice). Legs run on the body's local clock, so a runner
inside a time bubble runs normally in local time and merely *appears* fast
or slow from outside.
"""

import numpy as np


class Legs:
    def __init__(self, body, top_speed_m_per_s, acceleration_m_per_s2=40.0):
        self.body = body
        self.top_speed_m_per_s = float(top_speed_m_per_s)
        self.acceleration_m_per_s2 = float(acceleration_m_per_s2)
        self.direction = 0           # -1 left, 0 brake to a stand, +1 right
        self.speed_multiplier = 1.0  # steel feruchemy's dial

    @property
    def current_speed(self):
        """The body's actual horizontal speed (kept for plots and probes)."""
        return self.body.velocity[0]

    def jump(self, takeoff_speed_m_per_s):
        if self.body.on_ground:
            self.body.velocity[1] = takeoff_speed_m_per_s

    def tick(self, dt_seconds):
        if not self.body.on_ground:
            return  # airborne: ballistic, no air control
        local = self.body.local_dt_seconds
        dt_local = dt_seconds if local is None else local

        target_speed = self.direction * self.top_speed_m_per_s * self.speed_multiplier
        max_change = self.acceleration_m_per_s2 * self.speed_multiplier * dt_local
        self.body.velocity[0] += np.clip(target_speed - self.body.velocity[0],
                                         -max_change, max_change)
        self.body.driven_this_tick = True
