"""Allomantic steel: the Steelpush.

A push is a force PAIR along the line between the pusher's center and the
metal target's center — Newton's third law, no exceptions. The pusher is
shoved away from the metal and the metal is shoved away from the pusher,
with equal and opposite force.

Whether anything dramatic happens depends entirely on the bodies involved,
not on this class. A coin in midair rockets off and absorbs almost no
reaction before leaving range; a coin pinned against the ground cannot
move, so the pusher takes the full launch. None of that is special-cased —
it falls out of the force pair plus the world's ground constraint.

Push strength falls off linearly with distance, reaching zero at max_range.
Canon says pushes weaken with distance; the LINEAR shape is our modeling
choice, stated here so nobody mistakes it for lore.
"""

import numpy as np


class Steelpush:
    def __init__(self, pusher, target, strength_newtons, max_range_m=16.0):
        if not target.is_metal:
            raise ValueError(f"{target.name} is not metal; steel can't touch it")
        self.pusher = pusher
        self.target = target
        self.strength_newtons = float(strength_newtons)
        self.max_range_m = float(max_range_m)
        self.active = False

    def apply_forces(self):
        if not self.active:
            return

        offset = self.pusher.position - self.target.position
        distance = float(np.linalg.norm(offset))

        if distance >= self.max_range_m:
            return  # out of range, the push finds nothing

        if distance < 1e-9:
            # Degenerate case: bodies exactly coincident. Push the pusher
            # straight up so the math stays finite.
            direction_to_pusher = np.array([0.0, 1.0])
        else:
            direction_to_pusher = offset / distance

        magnitude = self.strength_newtons * (1.0 - distance / self.max_range_m)
        force_on_pusher = direction_to_pusher * magnitude

        self.pusher.apply_force(force_on_pusher)
        self.target.apply_force(-force_on_pusher)
