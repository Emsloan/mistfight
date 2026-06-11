"""Rigid frame: an extended body made of N point masses holding their shape.

The two-point rod of rigid_constraint.py answered what a bubble boundary does
to a body with LENGTH (notebook 12). A frame adds WIDTH, which is where
Elliott's off-center question lives (notebook 12B): a wide body crossing the
boundary anywhere but dead-center has one flank in fast time while the other
is still in slow time, and that imbalance has a lever arm.

Mechanically this is the same physics as the rod, just more of it: every
edge of the frame is projected with project_edge() — the exact primitive
RigidConstraint uses, equal-and-opposite force convention and all. Because
projecting one edge disturbs its neighbors, the frame sweeps all edges
several times per tick (Gauss-Seidel relaxation); each individual projection
follows the engine's force convention, so iterating stays physical, and the
leftover shape error shrinks geometrically with each pass.

Non-canon modeling choices, stated here: the frame is a set of point masses
with pairwise distance constraints — no continuous material, no bending
stiffness beyond what the chosen edges impose. Pick edges that triangulate
the shape or the frame will fold like a paper bag.
"""

import itertools

import numpy as np

from .rigid_constraint import project_edge


class RigidFrame:
    """N point masses rigidly framed by pairwise distance constraints.

    Register as a power with world.add_power(). Rest lengths are captured
    from the bodies' positions at construction: build the shape first, then
    freeze it.

    Parameters
    ----------
    bodies : list of Body
        The point masses making up the extended body.
    edges : list of (int, int), optional
        Index pairs to constrain. Default: every pair (the complete graph),
        which rigidifies any shape and is fine for small frames.
    iterations : int
        Gauss-Seidel sweeps per tick. More sweeps, stiffer shape.
    """

    def __init__(self, bodies, edges=None, iterations=10):
        self.bodies = list(bodies)
        if edges is None:
            edges = list(itertools.combinations(range(len(self.bodies)), 2))
        self.edges = [
            (self.bodies[index_a], self.bodies[index_b],
             float(np.linalg.norm(self.bodies[index_a].position
                                  - self.bodies[index_b].position)))
            for index_a, index_b in edges
        ]
        self.iterations = int(iterations)

    def tick(self, dt_seconds):
        for _ in range(self.iterations):
            for body_a, body_b, length_m in self.edges:
                project_edge(body_a, body_b, length_m, dt_seconds)

    def max_shape_error_m(self):
        """Worst current edge-length violation — the honesty check."""
        return max(
            abs(float(np.linalg.norm(body_a.position - body_b.position)) - length_m)
            for body_a, body_b, length_m in self.edges
        )
