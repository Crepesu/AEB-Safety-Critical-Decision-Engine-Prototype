
"""
Threat assessment logic for collision risk evaluation.
Implements TTC calculation and risk assessment for emergency braking.
"""
from typing import List, Tuple, Optional
from .models import DetectedObject
from .constants import SafetyConstants
from .enums import ObjectType


class ThreatAssessment:
    """
    Core safety-critical threat assessment engine.
    Calculates time-to-collision (TTC) and determines if emergency braking is required.
    """

    def __init__(self, vehicle_speed: float):
        """
        Initialize with the current vehicle speed in km/h.
        """
        self.vehicle_speed = vehicle_speed  # km/h

    def calculate_time_to_collision(self, obj: DetectedObject) -> float:
        """
        Calculate time-to-collision (TTC) for a detected object.
        Req 3: Calculate TTC for detected objects.
        Returns infinity if object is moving away or at same speed.
        """
        vehicle_speed_ms = self.vehicle_speed / 3.6  # Convert km/h to m/s
        relative_velocity = vehicle_speed_ms - obj.velocity[0]
        if relative_velocity <= 0:
            return float('inf')  # No collision if object is moving away or faster
        ttc = obj.distance / relative_velocity
        return max(0, ttc)

    def assess_collision_risk(self, objects: List[DetectedObject]) -> Tuple[bool, Optional[DetectedObject], float]:
        """
        Assess if emergency braking is required based on detected objects.
        Returns:
            (emergency_required, highest_risk_object, min_ttc)
        Only considers objects within a 4m lane width (|y| <= 2.0).
        Uses different TTC thresholds for vehicles vs. vulnerable users.
        """
        highest_risk_object = None
        min_ttc = float('inf')
        emergency_required = False

        for obj in objects:
            # Skip objects not in vehicle path (simplified lane filter)
            if abs(obj.position[1]) > 2.0:  # Assume 4m lane width
                continue

            ttc = self.calculate_time_to_collision(obj)

            # Use lower TTC threshold for vehicles, higher for VRUs
            threshold = SafetyConstants.MIN_TTC_THRESHOLD
            if obj.type == ObjectType.VEHICLE:
                threshold = 1.0

            # Track the object with the minimum TTC below threshold
            if ttc < threshold and ttc < min_ttc:
                min_ttc = ttc
                highest_risk_object = obj
                emergency_required = True

        return emergency_required, highest_risk_object, min_ttc
