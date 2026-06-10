"""One-off decisive check: does a time bubble change a projectile's
spatial path, or only its schedule?  python -m sim.probe_path_invariance
"""

import numpy as np

from sim import Body, World, SpeedBubble


def fire(time_factor):
    world = World(dt_seconds=1.0 / 1000.0)
    ball = world.add_body(Body("ball", 1.0, (-15, 100), velocity=(20, 0), radius_m=0.1))
    if time_factor:
        world.add_bubble(SpeedBubble(center=(0, 100), radius_m=5, time_factor=time_factor))
    while ball.position[0] < 15:
        world.step()
    return world.history.body("ball"), world.time_seconds


if __name__ == "__main__":
    free, t_free = fire(None)
    slow, t_slow = fire(0.2)
    fast, t_fast = fire(5.0)
    grid = np.linspace(-14.9, 14.9, 500)
    dev_slow = np.abs(np.interp(grid, slow["x"], slow["y"])
                      - np.interp(grid, free["x"], free["y"])).max()
    dev_fast = np.abs(np.interp(grid, fast["x"], fast["y"])
                      - np.interp(grid, free["x"], free["y"])).max()
    print(f"max path deviation vs free: cadmium {dev_slow * 100:.2f} cm, "
          f"bendalloy {dev_fast * 100:.2f} cm")
    print(f"total flight, external: free {t_free:.2f} s, "
          f"cadmium {t_slow:.2f} s, bendalloy {t_fast:.2f} s")
