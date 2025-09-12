"""Data models for detected objects."""
from dataclasses import dataclass
from typing import Tuple
from .enums import ObjectType

@dataclass
class DetectedObject:
    """Represents an object detected by the AEB sensor system"""
    id: int
    type: ObjectType
    position: Tuple[float, float]  # (x, y) coordinates
    velocity: Tuple[float, float]  # (vx, vy) velocity
    confidence: float  # Detection confidence (0.0 - 1.0)
    distance: float
    size: Tuple[float, float]  # (width, height)
