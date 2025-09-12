"""Decision-making engine implementing safety rules and logging."""
import time
from datetime import datetime
from typing import Optional
from .enums import SystemState
from .models import DetectedObject
from .constants import SafetyConstants

class SafetyDecisionEngine:
    """Safety-critical decision making with fail-safe behavior"""

    def __init__(self):
        self.system_state = SystemState.OPERATIONAL
        self.last_decision_time = time.time()
        self.warning_issued = False
        self.emergency_active = False
        self.event_log = []

    def make_safety_decision(self, threat_detected: bool, threat_object: Optional[DetectedObject],
                             ttc: float, sensor_reliability: float) -> dict:
        """Core safety decision logic with timing constraints"""
        decision_start_time = time.time()

        if sensor_reliability < 0.5:
            self.system_state = SystemState.SENSOR_FAILURE
            return {
                'action': 'FAIL_SAFE',
                'warning': True,
                'braking': False,
                'message': 'SENSOR FAILURE - DRIVER TAKEOVER REQUIRED',
                'response_time': time.time() - decision_start_time
            }

        if not threat_detected:
            self.warning_issued = False
            self.emergency_active = False
            self.system_state = SystemState.OPERATIONAL

        if threat_detected and ttc <= SafetyConstants.MIN_TTC_THRESHOLD + SafetyConstants.WARNING_ADVANCE_TIME:
            if not self.warning_issued:
                self.warning_issued = True
                self.system_state = SystemState.WARNING

        if threat_detected and ttc <= SafetyConstants.MIN_TTC_THRESHOLD:
            self.emergency_active = True
            self.system_state = SystemState.EMERGENCY_BRAKING
            self.log_emergency_event(threat_object, ttc)
            decision_time = time.time() - decision_start_time
            if decision_time > SafetyConstants.MAX_RESPONSE_TIME:
                self.event_log.append({
                    'timestamp': datetime.now(),
                    'event': 'RESPONSE_TIME_VIOLATION',
                    'actual_time': decision_time,
                    'required_time': SafetyConstants.MAX_RESPONSE_TIME
                })
            return {
                'action': 'EMERGENCY_BRAKE',
                'warning': True,
                'braking': True,
                'message': f'EMERGENCY BRAKING - TTC: {ttc:.2f}s',
                'response_time': decision_time,
                'threat_object': threat_object
            }
        elif self.warning_issued:
            return {
                'action': 'WARNING',
                'warning': True,
                'braking': False,
                'message': f'COLLISION WARNING - TTC: {ttc:.2f}s',
                'response_time': time.time() - decision_start_time,
                'threat_object': threat_object
            }
        return {
            'action': 'MONITOR',
            'warning': False,
            'braking': False,
            'message': 'MONITORING - ALL CLEAR',
            'response_time': time.time() - decision_start_time
        }

    def log_emergency_event(self, threat_object: Optional[DetectedObject], ttc: float):
        self.event_log.append({
            'timestamp': datetime.now(),
            'event': 'EMERGENCY_BRAKING',
            'ttc': ttc,
            'object_type': threat_object.type.value if threat_object else 'unknown',
            'object_distance': threat_object.distance if threat_object else 0,
            'system_state': self.system_state.value
        })
