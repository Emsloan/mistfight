"""Regenerate the README's images from the sim itself.

Run from the repo root:  python assets/make_readme_media.py
Every asset is a real simulation output, never an illustration.
"""

import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from sim import (Body, World, Steelpush, Health, GoldFeruchemy, GoldCompounding,
                 IronFeruchemy, Poison, SpeedBubble, animate)

assets_folder = pathlib.Path(__file__).parent


def coin_drop_gif():
    world = World()
    world.add_body(Body("coin", 0.004, (0, 2.5), radius_m=0.01, is_metal=True))
    wax = world.add_body(Body("wax", 80, (0, 3.0)))
    push = world.add_power(Steelpush(wax, world.bodies[0], 2000))
    push.active = True
    world.run(6.0)
    moving_picture = animate(world.history, x_limits=(-4, 4))
    moving_picture.save(assets_folder / "coin_drop_launch.gif", writer="pillow", fps=30)
    print("coin_drop_launch.gif")


def momentum_jolt_png():
    world = World()
    wax = world.add_body(Body("wax", 80, (0, 200)))
    ironmind = world.add_power(IronFeruchemy(wax))
    world.run(2.0)
    ironmind.store(0.5)
    world.run(1.0)
    ironmind.stop()
    world.run(1.0)
    data = world.history.body("wax")
    figure, ax = plt.subplots(figsize=(8, 4))
    ax.plot(data["t"], data["vy"], linewidth=2)
    ax.axvline(2.0, color="gray", linestyle="--")
    ax.axvline(3.0, color="gray", linestyle="--")
    ax.annotate("stores half his weight\n(speed DOUBLES)", (2.05, -38))
    ax.annotate("stops storing\n(speed halves)", (3.05, -22))
    ax.set_xlabel("time (s)"); ax.set_ylabel("fall velocity (m/s)")
    ax.set_title("Momentum is conserved through mass changes (canon) — so storing weight mid-fall is a speed boost")
    figure.tight_layout()
    figure.savefig(assets_folder / "momentum_jolt.png", dpi=110)
    print("momentum_jolt.png")


def wayne_bubble_png():
    figure, ax = plt.subplots(figsize=(8, 4))
    for label, with_bubble in [("open air", False), ("inside 5x bendalloy bubble", True)]:
        world = World()
        wayne = world.add_body(Body("wayne", 70, (0, 0.3)))
        health = world.add_power(Health(wayne, max_health=100, natural_regen_per_second=0))
        goldmind = world.add_power(GoldFeruchemy(health, initial_reserve_health_points=100))
        if with_bubble:
            world.add_bubble(SpeedBubble(center=(0, 0.3), radius_m=2, time_factor=5.0))
        health.damage(60)
        goldmind.tap(10)
        times, hp = [], []
        for _ in range(int(8.0 / world.dt_seconds)):
            world.step()
            times.append(world.time_seconds)
            hp.append(health.current)
        ax.plot(times, hp, linewidth=2, label=f"Wayne, {label}")
    ax.set_xlabel("external time (s)"); ax.set_ylabel("health")
    ax.set_title("Same wound, same gold, byte-identical healing code — one stands in a bubble")
    ax.legend(loc="lower right")
    figure.tight_layout()
    figure.savefig(assets_folder / "wayne_bubble.png", dpi=110)
    print("wayne_bubble.png")


def miles_budget_png():
    world = World()
    miles = world.add_body(Body("miles", 90, (0, 0.3)))
    health = world.add_power(Health(miles, max_health=100, natural_regen_per_second=0))
    goldmind = world.add_power(GoldFeruchemy(health, initial_reserve_health_points=50))
    compounder = world.add_power(GoldCompounding(health, goldmind, metal_supply_grams=10))
    world.add_power(Poison(health, damage_per_second=30))
    goldmind.store(3.0)
    compounder.active = True
    times, hp, metal = [], [], []
    for _ in range(int(80.0 / world.dt_seconds)):
        world.step()
        times.append(world.time_seconds)
        hp.append(health.current)
        metal.append(compounder.metal_supply_grams)
    figure, ax = plt.subplots(figsize=(8, 4))
    ax.plot(times, hp, linewidth=2, label="health (tanking 30 HP/s)")
    ax_metal = ax.twinx()
    ax_metal.plot(times, metal, color="goldenrod", linewidth=2)
    ax_metal.set_ylabel("gold remaining (g)", color="goldenrod")
    ax.set_xlabel("external time (s)"); ax.set_ylabel("health")
    ax.set_title("Miles Hundredlives: unkillable is a budget line, not a property")
    ax.legend(loc="center left")
    figure.tight_layout()
    figure.savefig(assets_folder / "miles_budget.png", dpi=110)
    print("miles_budget.png")


def marasi_png():
    figure, ax = plt.subplots(figsize=(8, 4))
    for label, factor in [("open air", None), ("inside 0.2x cadmium bubble", 0.2)]:
        world = World()
        wayne = world.add_body(Body("wayne", 70, (0, 0.3)))
        health = world.add_power(Health(wayne, max_health=100, natural_regen_per_second=0))
        poison = world.add_power(Poison(health, damage_per_second=5))
        if factor:
            world.add_bubble(SpeedBubble(center=(0, 0.3), radius_m=2, time_factor=factor))
        times, hp = [], []
        for _ in range(int(110.0 / world.dt_seconds)):
            world.step()
            if world.time_seconds >= 60:
                poison.active = False
            times.append(world.time_seconds)
            hp.append(health.current)
        hp = np.array(hp)
        outcome = "dead" if (hp <= 0).any() else f"survives at {hp[-1]:.0f}/100"
        ax.plot(times, hp, linewidth=2, label=f"poisoned, {label}: {outcome}")
    ax.axvline(60, color="seagreen", linestyle="--", label="antidote arrives (60 s out)")
    ax.set_xlabel("external time (s)"); ax.set_ylabel("health")
    ax.set_title("Marasi's gambit: the poison needs 20 seconds, rescue needs 60")
    ax.legend(loc="upper right")
    figure.tight_layout()
    figure.savefig(assets_folder / "marasi_gambit.png", dpi=110)
    print("marasi_gambit.png")


if __name__ == "__main__":
    coin_drop_gif()
    momentum_jolt_png()
    wayne_bubble_png()
    miles_budget_png()
    marasi_png()
    print("all media regenerated")
