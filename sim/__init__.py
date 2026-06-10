"""mistfight simulation core.

Side-view 2D, fixed-tick, deterministic. Powers are modular components
that act on bodies; nothing about any character is special-cased.
"""

from .bodies import Body
from .world import World, GRAVITY_M_PER_S2
from .steelpush import Steelpush
from .feruchemy import IronFeruchemy, GoldFeruchemy, SteelFeruchemy
from .health import Health, Poison
from .bubbles import SpeedBubble
from .compounding import GoldCompounding, COMPOUNDING_MULTIPLIER
from .locomotion import Legs
from .recording import History, plot_heights, animate

__all__ = [
    "Body", "World", "GRAVITY_M_PER_S2", "Steelpush",
    "IronFeruchemy", "GoldFeruchemy", "SteelFeruchemy", "Legs",
    "Health", "Poison", "SpeedBubble",
    "GoldCompounding", "COMPOUNDING_MULTIPLIER",
    "History", "plot_heights", "animate",
]
