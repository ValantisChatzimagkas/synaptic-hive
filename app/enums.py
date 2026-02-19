"""
Shared enumerations used across database models and API schemas.
Single source of truth for all enum values.
"""

from enum import Enum


class IndustryType(str, Enum):
    """Industry classification for factories"""

    AUTOMOTIVE = "automotive"
    METALWORKING = "metalworking"
    TEXTILE = "textile"
    ELECTRONICS = "electronics"
    FOOD_PROCESSING = "food_processing"


class MachineType(str, Enum):
    """Types of industrial machines"""

    WELDING = "welding"
    PRESS = "press"
    LATHE = "lathe"
    ASSEMBLY = "assembly"
    CONVEYOR = "conveyor"
