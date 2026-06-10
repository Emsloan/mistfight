"""Bendalloy and cadmium: time bubbles.

A bubble is a circular region where time runs at a different rate —
time_factor > 1 is a bendalloy speed bubble (more local seconds per world
second), < 1 is a cadmium slow bubble. The world scales each body's local
tick by the factor of whatever bubble contains it; that one mechanism is
the entire implementation.

Canon notes, and what this model does with them:

- Bubbles are ANCHORED where they're cast — they do not move with the
  caster (only a bendalloy savant can self-anchor one). So a bubble here
  is a fixed region, full stop.
- Objects crossing the boundary are deflected. That requires extended
  bodies (a nose and a tail in different time rates); our bodies are
  points, so deflection is deliberately absent — future experiment.
- A bullet leaving a bubble drops back to its outside speed. In this model
  that is EMERGENT, not imposed: velocity is stored in meters per local
  second and a bubble only changes how much time a body experiences per
  world tick. Inside, the bullet covers ground fast in world time; on
  exit, nothing needs to be reset because nothing about its state ever
  changed.
"""

import numpy as np


class SpeedBubble:
    def __init__(self, center, radius_m, time_factor):
        if time_factor <= 0:
            raise ValueError("time factor must be positive")
        self.center = np.array(center, dtype=float)
        self.radius_m = float(radius_m)
        self.time_factor = float(time_factor)

    def contains(self, position):
        return float(np.linalg.norm(np.asarray(position) - self.center)) <= self.radius_m
