"""Air drag: the push of air against motion.

Opt-in: nothing in the world feels air until an AirDrag power is added, so
every notebook and probe written before this module behaves exactly as it
did. Add the power and every non-fixed body feels a force opposing its
velocity, growing with the square of its speed:

    drag force = -0.5 * air_density * drag_coefficient * area * |v| * v

where area is the body's cross-section (pi * radius^2) and drag_coefficient
comes from the body (0.47 for a sphere, about 1.0 for a person falling
flat). This is the standard model for fast-moving objects; slow, syrupy
drag (force proportional to plain v) is for dust motes and is not modeled.

A falling body stops accelerating when drag balances weight. That speed is
called terminal velocity and follows from setting the two forces equal:

    terminal velocity = sqrt(2 * m * g / (air_density * drag_coefficient * area))

Terminal velocity grows with the square root of mass. That is the whole
Skimmer story in one line: store weight and the sky holds you up better
(notebook 13).

Time bubbles, choice stated: the air inside a bubble is inside the bubble,
so it shares the bubble's time. Drag is computed from the body's stored
velocity and applied through the normal force path, which integrates it
over the body's local time like every other force. Consequence: terminal
velocity in stored units is the same inside a bubble as outside; a bubbled
faller hits the ground sooner but no harder (probe-checked).

Non-canon modeling choices, stated here: still air (no wind), uniform
density (no altitude thinning), and the cross-section of a point mass is a
sphere of its ground-contact radius.
"""

import numpy as np

AIR_DENSITY_KG_PER_M3 = 1.225  # sea-level air


class AirDrag:
    """Quadratic air drag on every non-fixed body in the world.

    Register with world.add_power(). Bodies opt out individually by setting
    their drag_coefficient to 0.
    """

    def __init__(self, world, air_density_kg_per_m3=AIR_DENSITY_KG_PER_M3):
        self.world = world
        self.air_density_kg_per_m3 = float(air_density_kg_per_m3)

    def apply_forces(self):
        for body in self.world.bodies:
            if body.is_fixed or body.drag_coefficient == 0.0:
                continue
            speed = float(np.linalg.norm(body.velocity))
            if speed < 1e-12:
                continue
            area_m2 = np.pi * body.radius_m ** 2
            force_magnitude = (0.5 * self.air_density_kg_per_m3
                               * body.drag_coefficient * area_m2 * speed)
            body.apply_force(-force_magnitude * body.velocity)
