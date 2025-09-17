"""Core AEBSystem integration (relocated)."""
from typing import List
import numpy as np
from .sensors import SensorSystem
from .threat import ThreatAssessment
from .decision import SafetyDecisionEngine
from .constants import SafetyConstants
from .models import DetectedObject

class AEBSystem:
	def __init__(self, vehicle_speed: float = 30.0):
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
		detected_objects = self.sensor_system.detect_objects(scenario_objects)
		threat_detected, threat_object, min_ttc_trigger, min_ttc_all = self.threat_assessment.assess_collision_risk(detected_objects)
		sensor_reliability = self.sensor_system.get_sensor_reliability()
		decision = self.decision_engine.make_safety_decision(threat_detected, threat_object, min_ttc_trigger, sensor_reliability)
		self.update_metrics(decision, detected_objects, scenario_objects)
		return {
			'detected_objects': detected_objects,
			'threat_detected': threat_detected,
			'threat_object': threat_object,
			'min_ttc': min_ttc_trigger,
			'min_ttc_all': min_ttc_all,
			'decision': decision,
			'sensor_reliability': sensor_reliability,
			'system_state': self.decision_engine.system_state.value
		}

	def update_metrics(self, decision: dict, detected: List[DetectedObject], actual: List[dict]):
		self.performance_metrics['total_decisions'] += 1
		if decision['action'] == 'EMERGENCY_BRAKE':
			self.performance_metrics['emergency_braking_events'] += 1
		self.performance_metrics['response_times'].append(decision['response_time'])
		in_range_actual = [o for o in actual if (o['position'][0]**2 + o['position'][1]**2) ** 0.5 <= SafetyConstants.MAX_DETECTION_RANGE]
		baseline = max(1, len(in_range_actual))
		accuracy = min(1.0, len(detected) / baseline)
		self.performance_metrics['detection_accuracy'].append(accuracy)

	def get_performance_report(self) -> dict:
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
