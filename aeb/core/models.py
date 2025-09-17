"""Core data models (relocated)."""
from dataclasses import dataclass
from typing import Tuple
from .enums import ObjectType

@dataclass
class DetectedObject:
	id: int
	type: ObjectType
	position: Tuple[float, float]
	velocity: Tuple[float, float]
	confidence: float
	distance: float
	size: Tuple[float, float]
