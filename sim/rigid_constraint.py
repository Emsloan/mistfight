"""Rigid body constraint for a two-point extended body.

Two bodies — a nose and a tail — connected by a rigid rod of fixed length L.
This models a bullet: an extended object whose ends can be in different time
zones when crossing a bubble boundary.

The constraint is enforced by projection, not by spring forces: a spring
stiff enough to be 'rigid' at normal dt goes unstable inside a bubble where
the local dt is several times larger. Projection imposes the constraint
geometrically and is stable at any time scaling.

How the correction is shared between the two ends is THE physical decision,
because at a bubble boundary the ends live at different local time steps and
any asymmetry decides what the boundary does to the bullet. We follow the
engine's native convention for internal force pairs — equal and opposite
FORCE, integrated by each body's own local dt, exactly how steelpush already
works. Concretely: a force F moves a body by (F / m) * local_dt^2 within one
tick, so position corrections are shared in proportion to the generalized
inverse mass

    w = local_dt^2 / mass

and each velocity correction is its body's position correction divided by
that body's local dt. Outside bubbles (equal dt) this reduces to the usual
share-by-inverse-mass rule. A second, velocity-level projection removes any
remaining stretching rate in WORLD time — the discrete analog of a damper,
using the same equal-and-opposite force pattern.

This formulation was validated against ground truth (notebook 12): a stiff
critically-damped spring rod run at 200 kHz, which is the physical object a
projection stands in for. Both agree on what a bubble boundary does to a
nose-first rigid bullet:

  - heading: exactly unchanged. All internal forces act along the rod, and
    the rod is collinear with the velocity, so there is nothing to torque.
  - speed: each boundary crossing multiplies stored speed by
        M(f) = (1 + f)^2 / (2 * (1 + f^2))
    where f is the bubble's time factor. M is symmetric under f -> 1/f and
    is below 1 for every f != 1: a bubble always slows an extended body
    (for f = 5, in-and-out leaves (9/13)^2 = 0.479 of the launch speed).

The first version of this module (Gemini, 2026-06-10) divided velocity
corrections by local dt with mass-only position weights, which amounts to an
equal-and-opposite IMPULSE convention. That contradicts the engine's force
convention and pumped energy in: bullets exited a 5x bubble at 3.24x launch
speed, and at 2000 Hz came back out the side they entered. Notebook 12
records the failure in detail.

Non-canon modeling choice, stated here: the constraint is massless and
transmits only axial force, no torque. Real bullets have rotational inertia
and gyroscopic stability; we deliberately ignore that because the question
under test is whether translational asymmetry alone produces deflection.
(Verified answer: for an aligned bullet, no — see notebook 12.)
"""

import numpy as np


class RigidConstraint:
    """A rigid rod connecting two bodies at a fixed separation distance.

    Register this as a power with world.add_power(). It runs each tick
    before integration, correcting the previous tick's drift in both
    position (rod length) and velocity (rod stretching rate in world time).

    Parameters
    ----------
    body_a : Body
        The first body (conventionally the bullet nose).
    body_b : Body
        The second body (conventionally the bullet tail).
    length_m : float
        The rest length of the rod in metres.
    """

    def __init__(self, body_a, body_b, length_m):
        self.body_a = body_a
        self.body_b = body_b
        self.length_m = float(length_m)

    def tick(self, dt_seconds):
        project_edge(self.body_a, self.body_b, self.length_m, dt_seconds)


def project_edge(body_a, body_b, length_m, dt_seconds):
    """Project one rigid edge: restore its exact length and stop it
    stretching in world time. The shared primitive behind RigidConstraint
    (one edge) and RigidFrame (many edges, iterated). All the time-zone
    physics lives here; see the module docstring for the convention."""
    offset = body_a.position - body_b.position
    distance = float(np.linalg.norm(offset))

    if distance < 1e-9:
        # Bodies are coincident; nothing to project along.
        return

    direction = offset / distance

    # Fall back to the global dt before the world's first step has set
    # local time (and in case a future bubble ever stops time outright).
    local_dt_a = body_a.local_dt_seconds or dt_seconds
    local_dt_b = body_b.local_dt_seconds or dt_seconds

    # Generalized inverse masses: how far one unit of internal force
    # moves each end within one world tick. The local dt enters squared
    # because force acts over local time twice (velocity, then position).
    inverse_mass_a = local_dt_a ** 2 / body_a.mass_kg
    inverse_mass_b = local_dt_b ** 2 / body_b.mass_kg
    total_inverse_mass = inverse_mass_a + inverse_mass_b

    # --- Position projection: restore the exact edge length. ---
    error = distance - length_m
    if abs(error) > 1e-12:
        correction_a = -(inverse_mass_a / total_inverse_mass) * error * direction
        correction_b = (inverse_mass_b / total_inverse_mass) * error * direction

        body_a.position += correction_a
        body_b.position += correction_b
        body_a.velocity += correction_a / local_dt_a
        body_b.velocity += correction_b / local_dt_b

    # --- Velocity projection: stop the edge stretching in world time. ---
    # The edge's length changes per world tick by the axial difference of
    # the ends' world displacement rates v * (local_dt / dt). Choose one
    # equal-and-opposite force j that zeroes it; each end's velocity
    # change is that force integrated over its own local time.
    world_rate_a = np.dot(body_a.velocity, direction) * local_dt_a
    world_rate_b = np.dot(body_b.velocity, direction) * local_dt_b
    stretching_rate = world_rate_a - world_rate_b
    if abs(stretching_rate) > 1e-12:
        force_impulse = stretching_rate / total_inverse_mass
        body_a.velocity -= (force_impulse * local_dt_a / body_a.mass_kg) * direction
        body_b.velocity += (force_impulse * local_dt_b / body_b.mass_kg) * direction
