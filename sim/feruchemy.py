"""Feruchemical iron: the ironmind (weight storage).

The model, stated precisely because feruchemy is deceptively nuanced:

- A Ferring is in exactly one of three states per metalmind: STORING,
  TAPPING, or NEITHER. It is a continuous flow, not a transaction.
- While storing you are genuinely diminished the whole time: storing at
  fraction 0.5 means your mass is half its base value for as long as the
  dial is set, and the deficit flows into the ironmind.
- While tapping you are augmented: tapping at fraction 1.0 means carrying
  double your base mass, draining the ironmind to pay for it.
- The bookkeeping is zero-sum (plain feruchemy never profits): the reserve
  is measured in kilogram-seconds, and what flows in is exactly what is
  available to flow back out. You may tap at a different RATE than you
  stored — a week of half-weight banked can come back as a few seconds of
  crushing mass.
- Canon (Word of Brandon): iron stores MASS, not gravity's effect, and
  momentum is conserved when mass changes mid-motion. The body's
  change_mass handles that, which is where the strangeness lives: start
  storing mid-fall and you speed UP.

Compounding is deliberately not in this module. It breaks the zero-sum
rule via allomancy and will arrive with Miles.
"""


class IronFeruchemy:
    def __init__(self, body, initial_reserve_kg_seconds=0.0):
        self.body = body
        self.base_mass_kg = body.mass_kg
        self.reserve_kg_seconds = float(initial_reserve_kg_seconds)
        self.store_fraction = 0.0  # 0..1, portion of base mass flowing into the ironmind
        self.tap_fraction = 0.0    # >= 0, extra base-mass multiples drawn out

    def store(self, fraction):
        if not 0.0 <= fraction < 1.0:
            raise ValueError("store fraction must be in [0, 1) — you can't store ALL of yourself")
        self.store_fraction = fraction
        self.tap_fraction = 0.0

    def tap(self, fraction):
        if fraction < 0.0:
            raise ValueError("tap fraction must be non-negative")
        self.tap_fraction = fraction
        self.store_fraction = 0.0

    def stop(self):
        self.store_fraction = 0.0
        self.tap_fraction = 0.0

    def tick(self, dt_seconds):
        # Feruchemy runs on the Ferring's own clock: storing inside a speed
        # bubble fills the metalmind faster in world time, normally in local.
        local = self.body.local_dt_seconds
        dt_local = dt_seconds if local is None else local

        if self.store_fraction > 0.0:
            self.reserve_kg_seconds += self.base_mass_kg * self.store_fraction * dt_local
            target_mass = self.base_mass_kg * (1.0 - self.store_fraction)
        elif self.tap_fraction > 0.0:
            drain = self.base_mass_kg * self.tap_fraction * dt_local
            if drain > self.reserve_kg_seconds:
                # The ironmind runs dry mid-tap: snap back to base mass.
                self.reserve_kg_seconds = 0.0
                self.tap_fraction = 0.0
                target_mass = self.base_mass_kg
            else:
                self.reserve_kg_seconds -= drain
                target_mass = self.base_mass_kg * (1.0 + self.tap_fraction)
        else:
            target_mass = self.base_mass_kg

        if target_mass != self.body.mass_kg:
            self.body.change_mass(target_mass)  # conserves momentum


class SteelFeruchemy:
    """The steelmind (speed storage) — a Steelrunner's metal.

    Canon (Coppermind): steel stores PHYSICAL SPEED. Tapping moves the body
    many times faster; storing leaves the Ferring sluggish, 'like moving
    through molasses'. It has nothing to do with time — a Steelrunner is NOT
    a personal bendalloy bubble. The boundary (Elliott's framing, canon
    silent on details like heartbeat): the magic taxes or amplifies the
    body's MECHANICAL OUTPUT, while internal chemistry — healing, poison,
    aging — ticks at the normal local rate. The handwaive stops at the skin.

    Mechanically this is a dial on a Legs component: storing at fraction f
    means moving at (1 - f) of normal; tapping at t means (1 + t). Zero-sum
    like all plain feruchemy: the reserve is measured in speed-seconds
    (one second of full normal speed forgone or regained).

    The crucial difference from a bubble, which the sim makes measurable:
    velocity earned at steel-speed is REAL KINETIC STATE the world keeps —
    a Steelrunner's leap carries it. A bubble can only reschedule; it can
    never add velocity (the when-not-where theorem, notebook 07).
    """

    def __init__(self, legs, initial_reserve_speed_seconds=0.0):
        self.legs = legs
        self.reserve_speed_seconds = float(initial_reserve_speed_seconds)
        self.store_fraction = 0.0  # 0..1 of normal speed forgone
        self.tap_fraction = 0.0    # extra multiples of normal speed drawn out

    def store(self, fraction):
        if not 0.0 <= fraction < 1.0:
            raise ValueError("store fraction must be in [0, 1) — you can't store ALL your speed")
        self.store_fraction = fraction
        self.tap_fraction = 0.0

    def tap(self, fraction):
        if fraction < 0.0:
            raise ValueError("tap fraction must be non-negative")
        self.tap_fraction = fraction
        self.store_fraction = 0.0

    def stop(self):
        self.store_fraction = 0.0
        self.tap_fraction = 0.0

    def tick(self, dt_seconds):
        local = self.legs.body.local_dt_seconds
        dt_local = dt_seconds if local is None else local

        if self.store_fraction > 0.0:
            self.reserve_speed_seconds += self.store_fraction * dt_local
            self.legs.speed_multiplier = 1.0 - self.store_fraction
        elif self.tap_fraction > 0.0:
            drain = self.tap_fraction * dt_local
            if drain > self.reserve_speed_seconds:
                # The steelmind runs dry mid-stride.
                self.reserve_speed_seconds = 0.0
                self.tap_fraction = 0.0
                self.legs.speed_multiplier = 1.0
            else:
                self.reserve_speed_seconds -= drain
                self.legs.speed_multiplier = 1.0 + self.tap_fraction
        else:
            self.legs.speed_multiplier = 1.0


# You can be sickly, but you can't store yourself to death. Modeling choice.
MINIMUM_HEALTH_WHILE_STORING = 1.0


class GoldFeruchemy:
    """The goldmind (health storage) — Wayne's and Miles' feruchemical half.

    Storing drains current health directly into the goldmind: the Ferring is
    genuinely, continuously less healthy the whole time the dial is set —
    Wayne coughing through a sick week to bank the gold. Tapping converts
    banked health back into current health at any rate, so a week of misery
    can come back as seconds of supercharged recovery.

    Zero-sum in health points: what flows in is exactly what can flow out.
    Tapping only draws what actually heals (no waste above max health) —
    a modeling choice, stated here. Runs on the Ferring's local clock, like
    all flesh-bound processes.
    """

    def __init__(self, health, initial_reserve_health_points=0.0):
        self.health = health
        self.reserve_health_points = float(initial_reserve_health_points)
        self.store_rate_hp_per_second = 0.0
        self.tap_rate_hp_per_second = 0.0

    def store(self, rate_hp_per_second):
        if rate_hp_per_second < 0:
            raise ValueError("store rate must be non-negative")
        self.store_rate_hp_per_second = rate_hp_per_second
        self.tap_rate_hp_per_second = 0.0

    def tap(self, rate_hp_per_second):
        if rate_hp_per_second < 0:
            raise ValueError("tap rate must be non-negative")
        self.tap_rate_hp_per_second = rate_hp_per_second
        self.store_rate_hp_per_second = 0.0

    def stop(self):
        self.store_rate_hp_per_second = 0.0
        self.tap_rate_hp_per_second = 0.0

    def tick(self, dt_seconds):
        if self.health.is_dead:
            return
        local = self.health.body.local_dt_seconds
        dt_local = dt_seconds if local is None else local

        if self.store_rate_hp_per_second > 0.0:
            storable = max(0.0, self.health.current - MINIMUM_HEALTH_WHILE_STORING)
            transfer = min(self.store_rate_hp_per_second * dt_local, storable)
            self.health.current -= transfer
            self.reserve_health_points += transfer
        elif self.tap_rate_hp_per_second > 0.0:
            wound = self.health.max_health - self.health.current
            heal = min(self.tap_rate_hp_per_second * dt_local,
                       self.reserve_health_points, wound)
            self.health.current += heal
            self.reserve_health_points -= heal
