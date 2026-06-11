"""Physical bodies in the simulation.

Everything that exists in the world — fighters, coins, bullets — is a Body.
A Body is a point mass: it has position, velocity, and mass, plus a radius
used only for ground contact. Powers live elsewhere and act on bodies by
applying forces or changing properties.
"""

import numpy as np


class Body:
    def __init__(self, name, mass_kg, position, velocity=(0.0, 0.0),
                 radius_m=0.3, is_metal=False, is_fixed=False,
                 friction_static=0.6, friction_kinetic=0.4,
                 drag_coefficient=0.47):
        self.name = name
        self.mass_kg = float(mass_kg)
        self.position = np.array(position, dtype=float)  # meters; x = horizontal, y = up
        self.velocity = np.array(velocity, dtype=float)  # meters per second
        self.radius_m = float(radius_m)
        self.is_metal = is_metal
        # How much the air grips this body, used only when an AirDrag power
        # is in the world. 0.47 is the standard value for a sphere; a person
        # falling flat is about 1.0. Has no effect without AirDrag.
        self.drag_coefficient = float(drag_coefficient)
        # Fixed bodies are part of the world — rail spikes, building bones.
        # They never move, no matter what pushes on them: a perfect anchor.
        self.is_fixed = is_fixed
        # Coulomb friction against the ground: static grip holds until the
        # applied force exceeds friction_static * normal_force, then the body
        # breaks loose and only the weaker friction_kinetic resists sliding.
        self.friction_static = float(friction_static)
        self.friction_kinetic = float(friction_kinetic)
        # A body spawned at floor height starts grounded — otherwise it gets
        # one friction-free tick before the ground clamp notices it, which is
        # enough for a steelpush to skitter a coin that should have held.
        self.on_ground = self.position[1] <= self.radius_m + 1e-9
        # Set by Legs each tick it drives this body: the legs own the contact
        # patch, so the world's ground friction steps aside for that tick.
        self.driven_this_tick = False
        # Set by the world each tick: this body's experienced time per world
        # tick (scaled by any time bubble containing it). None until the
        # first step so components can fall back to the global dt.
        self.local_dt_seconds = None
        # Forces accumulate here during a tick; the world integrates and clears them.
        self.pending_force = np.zeros(2)

    def apply_force(self, force_newtons):
        self.pending_force += np.asarray(force_newtons, dtype=float)

    def change_mass(self, new_mass_kg):
        """Change this body's mass, conserving momentum (canon, per Word of Brandon).

        Momentum p = m * v stays fixed, so velocity scales by old_mass / new_mass:
        halve your mass and your speed doubles; tap weight mid-flight and you get
        slower but much harder to stop.
        """
        new_mass_kg = float(new_mass_kg)
        if new_mass_kg <= 0:
            raise ValueError("mass must be positive")
        self.velocity *= self.mass_kg / new_mass_kg
        self.mass_kg = new_mass_kg

    def __repr__(self):
        x, y = self.position
        return f"Body({self.name}, {self.mass_kg} kg, at ({x:.2f}, {y:.2f}))"
