"""Gold Compounding — Miles Hundredlives' exploit.

When an Allomancer burns a metal that is also their own filled metalmind,
the burn returns the stored attribute massively amplified — canon cites
roughly tenfold (Sazed and Wax both, accuracy uncertain, so it's a named
constant). This is the one place feruchemy's zero-sum bookkeeping breaks:
store 1 health point of misery, burn it back as 10 points of healing.
Allomancy foots the bill.

What it costs instead: METAL. Burning consumes the physical gold, and the
metal supply is Miles' only true budget. These experiments exist to find
where that budget runs out.

Modeling choices, stated:
- Burning consumes charge and metal only for healing actually delivered
  (no waste while at full health). This is generous to Miles, so any
  breaking point we find is his BEST case.
- Metal cost per charge point is a knob (METAL_GRAMS_PER_CHARGE_POINT);
  it sets his endurance, not the shape of the loop.
- Runs on the Compounder's local clock, like all flesh-bound processes.
"""

COMPOUNDING_MULTIPLIER = 10.0
METAL_GRAMS_PER_CHARGE_POINT = 0.05


class GoldCompounding:
    def __init__(self, health, goldmind, metal_supply_grams,
                 max_burn_charge_per_second=10.0):
        self.health = health
        self.goldmind = goldmind
        self.metal_supply_grams = float(metal_supply_grams)
        self.max_burn_charge_per_second = float(max_burn_charge_per_second)
        self.active = False

    def tick(self, dt_seconds):
        if not self.active or self.health.is_dead:
            return
        local = self.health.body.local_dt_seconds
        dt_local = dt_seconds if local is None else local

        wound = self.health.max_health - self.health.current
        if wound <= 0:
            return

        burnable_charge = min(
            self.max_burn_charge_per_second * dt_local,
            self.goldmind.reserve_health_points,
            self.metal_supply_grams / METAL_GRAMS_PER_CHARGE_POINT,
        )
        healing_delivered = min(burnable_charge * COMPOUNDING_MULTIPLIER, wound)
        charge_consumed = healing_delivered / COMPOUNDING_MULTIPLIER

        self.health.current += healing_delivered
        self.goldmind.reserve_health_points -= charge_consumed
        self.metal_supply_grams -= charge_consumed * METAL_GRAMS_PER_CHARGE_POINT
