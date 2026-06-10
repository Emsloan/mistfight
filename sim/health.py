"""Flesh and blood: health, natural healing, and steady harm.

Deliberately simple — health is a number, healing is a rate, poison is a
negative rate. No wound types, no body parts, no over-simming. The one
load-bearing rule: anything that lives in a body's bloodstream (regeneration,
poison) runs on that body's LOCAL clock, so a speed bubble accelerates your
healing and your poison together. That is not a special case; these
components just read the body's local tick like everything else.
"""


class Health:
    def __init__(self, body, max_health=100.0, natural_regen_per_second=0.5):
        self.body = body
        self.max_health = float(max_health)
        self.natural_regen_per_second = float(natural_regen_per_second)
        self.current = self.max_health

    @property
    def is_dead(self):
        return self.current <= 0.0

    def damage(self, amount):
        self.current = max(0.0, self.current - amount)

    def _local_dt(self, dt_seconds):
        local = self.body.local_dt_seconds
        return dt_seconds if local is None else local

    def tick(self, dt_seconds):
        if self.is_dead:
            return
        dt_local = self._local_dt(dt_seconds)
        self.current = min(self.max_health,
                           self.current + self.natural_regen_per_second * dt_local)


class Poison:
    """Steady damage carried in the victim's own bloodstream — it ticks on
    the victim's local clock. A bubble fast-forwards the poisoning and the
    recovery alike; it cannot save you from what's already inside you."""

    def __init__(self, health, damage_per_second):
        self.health = health
        self.damage_per_second = float(damage_per_second)
        self.active = True

    def tick(self, dt_seconds):
        if not self.active or self.health.is_dead:
            return
        dt_local = self.health._local_dt(dt_seconds)
        self.health.damage(self.damage_per_second * dt_local)
