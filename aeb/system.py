
"""
Integration of sensors, threat assessment, and decision engine.
Coordinates the main AEB system logic and performance metrics.
"""
from typing import List
import numpy as np
from .sensors import SensorSystem
from .threat import ThreatAssessment
from .decision import SafetyDecisionEngine
from .constants import SafetyConstants
from .models import DetectedObject


class AEBSystem:
    """
    Main AEB System integrating all components.
    Orchestrates sensor input, threat assessment, decision making, and metrics.
    """

    def __init__(self, vehicle_speed: float = 30.0):
        """
        Initialize the AEB system and all subcomponents.
        vehicle_speed: initial speed in km/h (default 30).
        """
        self.sensor_system = SensorSystem()
        self.threat_assessment = ThreatAssessment(vehicle_speed)
        self.decision_engine = SafetyDecisionEngine()
        self.vehicle_speed = vehicle_speed
        self.performance_metrics = {
            'total_decisions': 0,
            'emergency_braking_events': 0,
            'false_positives': 0,
            'response_times': [],
            'detection_accuracy': []
        }

    def process_scenario(self, scenario_objects: List[dict]) -> dict:
        """
        Main processing loop for a single scenario.
        Runs detection, threat assessment, decision, and updates metrics.
        Returns a dict with all relevant outputs for analysis.
        """
        detected_objects = self.sensor_system.detect_objects(scenario_objects)
        threat_detected, threat_object, min_ttc = self.threat_assessment.assess_collision_risk(detected_objects)
        sensor_reliability = self.sensor_system.get_sensor_reliability()
        decision = self.decision_engine.make_safety_decision(
            threat_detected, threat_object, min_ttc, sensor_reliability
        )
        self.update_metrics(decision, detected_objects, scenario_objects)
        return {
            'detected_objects': detected_objects,
            'threat_detected': threat_detected,
            'threat_object': threat_object,
            'min_ttc': min_ttc,
            'decision': decision,
            'sensor_reliability': sensor_reliability,
            'system_state': self.decision_engine.system_state.value
        }

    def update_metrics(self, decision: dict, detected: List[DetectedObject], actual: List[dict]):
        """
        Update system performance metrics for requirement validation.
        - Tracks total decisions, emergency events, response times, and detection accuracy.
        - Accuracy only counts actual objects within detection range.
        """
        self.performance_metrics['total_decisions'] += 1
        if decision['action'] == 'EMERGENCY_BRAKE':
            self.performance_metrics['emergency_braking_events'] += 1
        self.performance_metrics['response_times'].append(decision['response_time'])
        # Only count actual objects that are within theoretical detection range for accuracy baseline
        in_range_actual = [o for o in actual if (o['position'][0]**2 + o['position'][1]**2) ** 0.5 <= SafetyConstants.MAX_DETECTION_RANGE]
        baseline = max(1, len(in_range_actual))
        accuracy = min(1.0, len(detected) / baseline)
        self.performance_metrics['detection_accuracy'].append(accuracy)

    def get_performance_report(self) -> dict:
        """
        Generate a performance report for requirement validation.
        Returns summary statistics and compliance flags.
        """
        if not self.performance_metrics['response_times']:
            return {'error': 'No data collected yet'}
        avg_response_time = np.mean(self.performance_metrics['response_times'])
        avg_accuracy = np.mean(self.performance_metrics['detection_accuracy'])
        return {
            'total_decisions': self.performance_metrics['total_decisions'],
            'emergency_events': self.performance_metrics['emergency_braking_events'],
            'avg_response_time': avg_response_time,
            'max_response_time': max(self.performance_metrics['response_times']),
            'avg_detection_accuracy': avg_accuracy,
            'req_6_compliance': avg_response_time <= SafetyConstants.MAX_RESPONSE_TIME,
            'req_2_compliance': avg_accuracy >= SafetyConstants.MIN_DETECTION_ACCURACY,
            'event_log': self.decision_engine.event_log
        }
