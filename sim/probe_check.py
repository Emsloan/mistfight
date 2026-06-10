"""Quick numerical probe of the engine before the notebooks lean on it.

Run from the mistfight folder:  python -m sim.probe_check
"""

import math

import numpy as np

from sim import (Body, World, Steelpush, IronFeruchemy, GoldFeruchemy,
                 GoldCompounding, Health, Poison, SpeedBubble, GRAVITY_M_PER_S2)


def check_free_fall():
    world = World()
    guy = world.add_body(Body("guy", mass_kg=80, position=(0, 20)))
    world.run(3.0)
    data = world.history.body("guy")
    landed_tick = np.argmax(data["on_ground"])
    simulated = data["t"][landed_tick]
    analytic = math.sqrt(2 * (20 - guy.radius_m) / GRAVITY_M_PER_S2)
    print(f"free fall: landed at {simulated:.3f} s, analytic {analytic:.3f} s")
    assert abs(simulated - analytic) < 0.02


def check_momentum_conserving_mass_change():
    body = Body("test", mass_kg=80, position=(0, 10), velocity=(0, -10))
    body.change_mass(40)
    print(f"mass 80->40 kg: velocity {body.velocity[1]:.1f} m/s (expect -20)")
    assert abs(body.velocity[1] + 20) < 1e-9


def check_anchored_launch():
    world = World()
    coin = world.add_body(Body("coin", 0.004, (0, 0.01), radius_m=0.01, is_metal=True))
    wax = world.add_body(Body("wax", 80, (0, 1.0)))
    push = world.add_power(Steelpush(wax, coin, strength_newtons=2000))
    push.active = True
    world.run(12.0)
    data = world.history.body("wax")
    equilibrium = push.max_range_m * (1 - 80 * GRAVITY_M_PER_S2 / 2000) + coin.position[1]
    mean_height = data["y"][len(data["y"]) // 2:].mean()  # after transient
    peak = data["y"].max()
    print(f"anchored launch: peak {peak:.2f} m, late-run mean {mean_height:.2f} m, "
          f"analytic equilibrium {equilibrium:.2f} m")
    assert peak > 5.0, "Wax should launch well off the ground"
    assert abs(mean_height - equilibrium) < 1.5, "should oscillate around equilibrium"


def check_midair_coin_is_no_anchor():
    # High altitude on purpose: near the ground a downward-pushed coin lands
    # almost instantly and BECOMES an anchor (the classic coin-drop launch),
    # so "unanchored coins give you nothing" is only testable in open air.
    world = World()
    coin = world.add_body(Body("coin", 0.004, (0, 49.5), radius_m=0.01, is_metal=True))
    wax = world.add_body(Body("wax", 80, (0, 50.0)))
    push = world.add_power(Steelpush(wax, coin, strength_newtons=2000))
    push.active = True
    world.run(1.0)
    data = world.history.body("wax")
    upward_kick = (data["vy"] + GRAVITY_M_PER_S2 * data["t"]).max()  # gravity removed
    print(f"midair coin: Wax's total upward kick {upward_kick:.2f} m/s (should be small)")
    assert upward_kick < 1.0, "an unanchored coin should give Wax almost nothing"


def check_coin_drop_launch():
    world = World()
    coin = world.add_body(Body("coin", 0.004, (0, 2.5), radius_m=0.01, is_metal=True))
    wax = world.add_body(Body("wax", 80, (0, 3.0)))
    push = world.add_power(Steelpush(wax, coin, strength_newtons=2000))
    push.active = True
    world.run(6.0)
    coin_data = world.history.body("coin")
    wax_data = world.history.body("wax")
    coin_grounded_at = coin_data["t"][np.argmax(coin_data["on_ground"])]
    print(f"coin drop: coin grounded at {coin_grounded_at:.3f} s, "
          f"Wax peak {wax_data['y'].max():.2f} m")
    assert coin_grounded_at < 0.3, "pushed coin should slam down almost instantly"
    assert wax_data["y"].max() > 5.0, "grounded coin becomes an anchor; Wax launches"


def check_feruchemy_is_zero_sum():
    # Store half your mass for 2 s -> 80 kg-s banked. Tapping at +1.0 base
    # mass (160 kg total) drains 80 kg-s per second -> should last exactly 1 s.
    world = World()
    wax = world.add_body(Body("wax", 80, (0, 0.3)))  # standing on the ground
    ironmind = world.add_power(IronFeruchemy(wax))

    ironmind.store(0.5)
    world.run(2.0)
    banked = ironmind.reserve_kg_seconds
    print(f"feruchemy: stored half weight for 2 s -> {banked:.1f} kg-s banked (expect 80)")
    assert abs(banked - 80.0) < 0.5
    assert abs(wax.mass_kg - 40.0) < 1e-9, "actively lighter the whole time storing"

    ironmind.tap(1.0)
    world.run(0.9)
    assert abs(wax.mass_kg - 160.0) < 1e-9, "carrying double mass while tapping"
    world.run(0.2)  # past the 1 s mark: the ironmind should have run dry
    print(f"feruchemy: after over-tapping, mass back to {wax.mass_kg:.0f} kg, "
          f"reserve {ironmind.reserve_kg_seconds:.2f} kg-s")
    assert abs(wax.mass_kg - 80.0) < 1e-9, "snaps back to base when the ironmind empties"
    assert ironmind.reserve_kg_seconds == 0.0


def check_storing_midfall_speeds_you_up():
    # The counterintuitive canon consequence: momentum is conserved, so
    # halving your mass mid-fall DOUBLES your fall speed.
    world = World()
    wax = world.add_body(Body("wax", 80, (0, 200)))
    ironmind = world.add_power(IronFeruchemy(wax))
    world.run(2.0)
    speed_before = wax.velocity[1]
    ironmind.store(0.5)
    world.step()
    speed_after = wax.velocity[1]
    print(f"mid-fall store: {speed_before:.1f} m/s -> {speed_after:.1f} m/s "
          f"(expect roughly doubled)")
    assert abs(speed_after - 2 * speed_before) < 0.5


def check_bubble_compresses_time():
    # Two identical balls dropped from 5 m; one falls inside a 5x bendalloy
    # bubble. It should land in one fifth the EXTERNAL time.
    world = World()
    free_ball = world.add_body(Body("free", 1.0, (0, 5), radius_m=0.1))
    fast_ball = world.add_body(Body("fast", 1.0, (10, 5), radius_m=0.1))
    world.add_bubble(SpeedBubble(center=(10, 3), radius_m=3.5, time_factor=5.0))
    world.run(1.5)
    free_landing = world.history.body("free")
    fast_landing = world.history.body("fast")
    free_time = free_landing["t"][np.argmax(free_landing["on_ground"])]
    fast_time = fast_landing["t"][np.argmax(fast_landing["on_ground"])]
    print(f"bubble drop: free ball lands at {free_time:.3f} s, "
          f"bubbled ball at {fast_time:.3f} s (ratio {free_time / fast_time:.1f}, expect ~5)")
    assert abs(free_time / fast_time - 5.0) < 0.3


def check_exit_speed_is_emergent():
    # A ball crossing a speed bubble covers ground fast WHILE INSIDE but
    # exits at its original velocity, with no reset code anywhere — its
    # velocity state never changed, only its experienced time.
    # The ball falls while crossing, so it cuts a descending chord through
    # the circular bubble — chord length varies. The robust invariant: while
    # inside, horizontal ground covered per EXTERNAL second should be
    # vx * time_factor = 100 m/s, and the exit velocity should be untouched.
    world = World(dt_seconds=1.0 / 1000.0)
    ball = world.add_body(Body("ball", 1.0, (-15, 100), velocity=(20, 0), radius_m=0.1))
    world.add_bubble(SpeedBubble(center=(0, 100), radius_m=5, time_factor=5.0))
    inside_external_seconds = 0.0
    inside_distance_m = 0.0
    while ball.position[0] < 15:
        inside_before = world.time_factor_at(ball.position) > 1.0
        x_before = ball.position[0]
        world.step()
        if inside_before:
            inside_external_seconds += world.dt_seconds
            inside_distance_m += ball.position[0] - x_before
    effective_speed = inside_distance_m / inside_external_seconds
    print(f"bubble crossing: while inside, {inside_distance_m:.1f} m covered in "
          f"{inside_external_seconds:.3f} s external = {effective_speed:.0f} m/s effective "
          f"(expect ~100); exit vx = {ball.velocity[0]:.1f} m/s (expect 20, untouched)")
    assert abs(effective_speed - 100.0) < 5.0
    assert abs(ball.velocity[0] - 20.0) < 1e-9


def check_wayne_heals_fast_in_a_bubble():
    # THE emergence test. Two identical Wayne setups: 60 damage, tapping
    # gold at 10 HP/s. One stands inside a 5x bubble. Neither the health
    # nor the gold code knows bubbles exist; the bubbled Wayne should
    # nevertheless be fully healed ~5x sooner in external time.
    def wounded_wayne(world):
        wayne = world.add_body(Body("wayne", 70, (0, 0.3)))
        health = world.add_power(Health(wayne, max_health=100, natural_regen_per_second=0))
        goldmind = world.add_power(GoldFeruchemy(health, initial_reserve_health_points=100))
        health.damage(60)
        goldmind.tap(10)
        return health

    plain_world = World()
    plain_health = wounded_wayne(plain_world)
    bubble_world = World()
    bubble_health = wounded_wayne(bubble_world)
    bubble_world.add_bubble(SpeedBubble(center=(0, 0.3), radius_m=2, time_factor=5.0))

    bubble_world.run(1.3)
    plain_world.run(1.3)
    healed_in_bubble = bubble_health.current
    healed_outside = plain_health.current
    plain_world.run(4.8)  # out to ~6.1 s total
    print(f"wayne: after 1.3 s external — bubbled {healed_in_bubble:.0f}/100, "
          f"plain {healed_outside:.0f}/100; plain full at ~6 s: {plain_health.current:.0f}/100")
    assert healed_in_bubble >= 99.9, "bubbled Wayne should be fully healed"
    assert healed_outside < 60, "plain Wayne should still be wounded"
    assert plain_health.current >= 99.9


def check_cadmium_stretches_time():
    # The mirror of the bendalloy probe: a ball falling inside a 0.2x
    # cadmium bubble should take five times LONGER to land, external.
    world = World()
    free_ball = world.add_body(Body("free", 1.0, (0, 5), radius_m=0.1))
    slow_ball = world.add_body(Body("slow", 1.0, (10, 5), radius_m=0.1))
    world.add_bubble(SpeedBubble(center=(10, 3), radius_m=3.5, time_factor=0.2))
    world.run(6.0)
    free_data = world.history.body("free")
    slow_data = world.history.body("slow")
    free_time = free_data["t"][np.argmax(free_data["on_ground"])]
    slow_time = slow_data["t"][np.argmax(slow_data["on_ground"])]
    print(f"cadmium drop: free ball lands at {free_time:.3f} s, slowed ball at "
          f"{slow_time:.3f} s (ratio {slow_time / free_time:.1f}, expect ~5)")
    assert abs(slow_time / free_time - 5.0) < 0.3


def check_compounding_breaks_zero_sum():
    # Miles banks 20 charge points of misery, takes a near-lethal wound,
    # and burns the goldmind: 99 HP healed for 9.9 charge — a 10x return
    # that plain feruchemy (notebook 04's Wayne) could never show.
    world = World()
    miles = world.add_body(Body("miles", 90, (0, 0.3)))
    health = world.add_power(Health(miles, max_health=100, natural_regen_per_second=0))
    goldmind = world.add_power(GoldFeruchemy(health, initial_reserve_health_points=20))
    compounder = world.add_power(GoldCompounding(health, goldmind, metal_supply_grams=10))

    health.damage(99)
    compounder.active = True
    world.run(2.0)
    charge_spent = 20 - goldmind.reserve_health_points
    print(f"compounding: healed {health.current - 1:.1f} HP for {charge_spent:.1f} "
          f"charge points (10x return)")
    assert abs(health.current - 100) < 0.1
    assert abs(charge_spent - 9.9) < 0.1


def check_miles_dies_when_the_metal_runs_out():
    # Under steady 30 HP/s damage Miles holds the line easily — until the
    # gold is gone, and then he dies like anyone else.
    world = World()
    miles = world.add_body(Body("miles", 90, (0, 0.3)))
    health = world.add_power(Health(miles, max_health=100, natural_regen_per_second=0))
    goldmind = world.add_power(GoldFeruchemy(health, initial_reserve_health_points=50))
    compounder = world.add_power(GoldCompounding(health, goldmind, metal_supply_grams=1.5))
    world.add_power(Poison(health, damage_per_second=30))
    goldmind.store(0)  # he's busy being shot; charge comes from the bank
    compounder.active = True

    world.run(8.0)
    mid_run_health = health.current
    world.run(8.0)
    print(f"miles: at 8 s health {mid_run_health:.0f}/100 (tanking 30 HP/s), "
          f"at 16 s health {health.current:.0f}/100, metal {compounder.metal_supply_grams:.2f} g")
    assert mid_run_health > 90, "with metal, 30 HP/s should barely scratch him"
    assert health.is_dead, "without metal, Hundredlives runs out of lives"


if __name__ == "__main__":
    check_free_fall()
    check_momentum_conserving_mass_change()
    check_anchored_launch()
    check_midair_coin_is_no_anchor()
    check_coin_drop_launch()
    check_feruchemy_is_zero_sum()
    check_storing_midfall_speeds_you_up()
    check_bubble_compresses_time()
    check_exit_speed_is_emergent()
    check_wayne_heals_fast_in_a_bubble()
    check_cadmium_stretches_time()
    check_compounding_breaks_zero_sum()
    check_miles_dies_when_the_metal_runs_out()
    print("all probes passed")
