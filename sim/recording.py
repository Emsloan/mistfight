"""Recording and viewing what happened in a run.

The History captures every body's state at every tick. Notebooks read it
back as numpy arrays for plotting, or hand it to `animate` to watch the
run as an inline animation. Recording everything every tick is wasteful
on purpose — runs are short, and a complete record is what makes every
experiment replayable and comparable.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation


class History:
    def __init__(self):
        self.times = []
        # body name -> list of (x, y, vx, vy, mass, on_ground) tuples
        self.tracks = {}

    def record(self, world):
        self.times.append(world.time_seconds)
        for body in world.bodies:
            track = self.tracks.setdefault(body.name, [])
            track.append((
                body.position[0], body.position[1],
                body.velocity[0], body.velocity[1],
                body.mass_kg, body.on_ground,
            ))

    def body(self, name):
        """All recorded state for one body, as named numpy arrays."""
        track = np.array(self.tracks[name], dtype=float)
        return {
            "t": np.array(self.times),
            "x": track[:, 0],
            "y": track[:, 1],
            "vx": track[:, 2],
            "vy": track[:, 3],
            "mass": track[:, 4],
            "on_ground": track[:, 5].astype(bool),
        }


def plot_heights(history, body_names, ax=None):
    """Height-over-time curves for the named bodies."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 4))
    for name in body_names:
        data = history.body(name)
        ax.plot(data["t"], data["y"], label=name)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("height (m)")
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.legend()
    return ax


def animate(history, body_names=None, frames_per_second=30,
            x_limits=None, y_limits=None):
    """Watch a run. Returns a matplotlib FuncAnimation; display it in a
    notebook with `HTML(anim.to_jshtml())`.

    The history is recorded at the physics tick rate (hundreds of frames
    per second), so we subsample down to a watchable frame rate.
    """
    if body_names is None:
        body_names = list(history.tracks.keys())

    times = np.array(history.times)
    duration = times[-1] - times[0]
    frame_count = max(2, int(duration * frames_per_second))
    frame_indices = np.linspace(0, len(times) - 1, frame_count).astype(int)

    tracks = {name: history.body(name) for name in body_names}

    figure, ax = plt.subplots(figsize=(7, 5))
    if x_limits is None:
        all_x = np.concatenate([d["x"] for d in tracks.values()])
        x_limits = (all_x.min() - 2, all_x.max() + 2)
    if y_limits is None:
        all_y = np.concatenate([d["y"] for d in tracks.values()])
        y_limits = (-0.5, all_y.max() + 2)
    ax.set_xlim(*x_limits)
    ax.set_ylim(*y_limits)
    ax.set_aspect("equal")
    ax.axhline(0, color="saddlebrown", linewidth=2)  # the ground
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")

    dots = {}
    trails = {}
    for name in body_names:
        trail, = ax.plot([], [], linewidth=0.8, alpha=0.5)
        dot, = ax.plot([], [], "o", markersize=8, label=name,
                       color=trail.get_color())
        dots[name] = dot
        trails[name] = trail
    ax.legend(loc="upper right")
    clock_text = ax.text(0.02, 0.95, "", transform=ax.transAxes)

    def draw_frame(frame_number):
        tick = frame_indices[frame_number]
        for name in body_names:
            data = tracks[name]
            dots[name].set_data([data["x"][tick]], [data["y"][tick]])
            trails[name].set_data(data["x"][: tick + 1], data["y"][: tick + 1])
        clock_text.set_text(f"t = {times[tick]:.2f} s")
        return list(dots.values()) + list(trails.values()) + [clock_text]

    moving_picture = animation.FuncAnimation(
        figure, draw_frame, frames=frame_count,
        interval=1000 / frames_per_second, blit=True,
    )
    plt.close(figure)  # keep the static figure from also rendering in notebooks
    return moving_picture
