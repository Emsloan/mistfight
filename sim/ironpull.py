"""Allomantic iron: the Ironpull.

The mirror of the Steelpush, and like it, a force PAIR along the line
between centers — Newton's third law, no exceptions. The puller is drawn
toward the metal and the metal toward the puller, with equal force. Same
linear falloff to zero at max range as the push (same modeling choice,
stated for the same reason).

The asymmetry with pushing is not coded anywhere and must emerge: a push's
downward component presses loose metal into the ground and manufactures
grip; a pull's component lifts it and destroys grip. If the model is right,
no pull on a loose coin ever anchors — Lurchers must use the bones of the
world, while Coinshots mint anchors from pocket change.

Known gap, stated: the engine has no body-body collision, so a Lurcher who
holds the pull all the way in will sail through the anchor (and a pulled
coin through the Lurcher). Experiments release the pull on approach, which
is also what canon Lurchers do, or they eat the lamppost.
"""

import numpy as np


class Ironpull:
    def __init__(self, puller, target, strength_newtons, max_range_m=16.0):
        if not target.is_metal:
            raise ValueError(f"{target.name} is not metal; iron can't touch it")
        self.puller = puller
        self.target = target
        self.strength_newtons = float(strength_newtons)
        self.max_range_m = float(max_range_m)
        self.active = False

    def apply_forces(self):
        if not self.active:
            return

        offset = self.target.position - self.puller.position
        distance = float(np.linalg.norm(offset))

        if distance >= self.max_range_m:
            return  # out of range, the pull finds nothing

        if distance < 1e-9:
            return  # already there; nothing to pull along

        direction_to_target = offset / distance
        magnitude = self.strength_newtons * (1.0 - distance / self.max_range_m)
        force_on_puller = direction_to_target * magnitude

        self.puller.apply_force(force_on_puller)
        self.target.apply_force(-force_on_puller)
