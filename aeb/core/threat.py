"""Core threat assessment (relocated)."""
from typing import List, Tuple, Optional
from .models import DetectedObject
from .constants import SafetyConstants
from .enums import ObjectType

class ThreatAssessment:
	def __init__(self, vehicle_speed: float):
		self.vehicle_speed = vehicle_speed

	def calculate_time_to_collision(self, obj: DetectedObject) -> float:
		vehicle_speed_ms = self.vehicle_speed / 3.6
		relative_velocity = vehicle_speed_ms - obj.velocity[0]
		if relative_velocity <= 0:
			return float('inf')
		ttc = obj.distance / relative_velocity
		return max(0, ttc)

	def assess_collision_risk(self, objects: List[DetectedObject]) -> Tuple[bool, Optional[DetectedObject], float, float]:
		highest_risk_object = None
		min_ttc_trigger = float('inf')
		min_ttc_all = float('inf')
		emergency_required = False
		for obj in objects:
			if abs(obj.position[1]) > 2.0:
				continue
			ttc = self.calculate_time_to_collision(obj)
			if ttc < min_ttc_all:
				min_ttc_all = ttc
			threshold = SafetyConstants.MIN_TTC_THRESHOLD
			if obj.type == ObjectType.VEHICLE:
				threshold = 1.0
			if ttc < threshold and ttc < min_ttc_trigger:
				min_ttc_trigger = ttc
				highest_risk_object = obj
				emergency_required = True
		return emergency_required, highest_risk_object, min_ttc_trigger, min_ttc_all
