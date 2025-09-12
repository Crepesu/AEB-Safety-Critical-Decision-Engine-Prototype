"""Simulation environment for testing AEB system requirements."""
from .system import AEBSystem
from .enums import WeatherCondition
from .constants import SafetyConstants

class AEBSimulation:
    """Simulation environment for testing AEB system requirements"""

    def __init__(self):
        self.aeb_system = AEBSystem()
        self.scenario_results = []

    def create_pedestrian_crossing_scenario(self):
        return [{
            'type': 'pedestrian',
            'position': [25.0, 1.5],
            'velocity': [-1.5, 0],
            'size': [0.6, 1.8]
        }]

    def create_cyclist_scenario(self):
        return [{
            'type': 'cyclist',
            'position': [30.0, 0.5],
            'velocity': [3.0, 0],
            'size': [0.6, 1.8]
        }]

    def create_false_positive_scenario(self):
        return [{
            'type': 'pedestrian',
            'position': [20.0, 4.0],
            'velocity': [1.0, 0],
            'size': [0.6, 1.8]
        }]

    def run_requirement_validation_tests(self):
        print("=== AEB System Requirement Validation Tests ===\n")
        print("Testing Req 1: 50m Detection Range")
        far_scenario = [{
            'type': 'pedestrian',
            'position': [60.0, 1.0],
            'velocity': [0, 0],
            'size': [0.6, 1.8]
        }]
        result = self.aeb_system.process_scenario(far_scenario)
        print(f"Objects beyond 50m detected: {len(result['detected_objects'])} (should be 0)")
        print(f"\u2713 Req 1 {'PASSED' if len(result['detected_objects']) == 0 else 'FAILED'}\n")

        print("Testing Req 4: Emergency Braking TTC Threshold")
        close_scenario = [{
            'type': 'pedestrian',
            'position': [10.0, 1.0],
            'velocity': [0, 0],
            'size': [0.6, 1.8]
        }]
        result = self.aeb_system.process_scenario(close_scenario)
        print(f"Emergency braking triggered: {result['decision']['braking']}")
        print(f"TTC: {result['min_ttc']:.2f}s (threshold: {SafetyConstants.MIN_TTC_THRESHOLD}s)")
        print(f"\u2713 Req 4 {'PASSED' if result['decision']['braking'] and result['min_ttc'] < SafetyConstants.MIN_TTC_THRESHOLD else 'FAILED'}\n")

        print("Testing Req 6: Response Time <100ms")
        emergency_scenario = self.create_pedestrian_crossing_scenario()
        result = self.aeb_system.process_scenario(emergency_scenario)
        response_time = result['decision']['response_time'] * 1000
        print(f"Response time: {response_time:.2f}ms (requirement: <100ms)")
        print(f"\u2713 Req 6 {'PASSED' if response_time < 100 else 'FAILED'}\n")

        print("Testing Req 7: Weather Performance")
        self.aeb_system.sensor_system.set_weather_condition(WeatherCondition.LIGHT_RAIN)
        self.aeb_system.process_scenario(emergency_scenario)
        rain_reliability = self.aeb_system.sensor_system.get_sensor_reliability()
        print(f"Sensor reliability in rain: {rain_reliability:.2f} (requirement: >0.9)")
        print(f"\u2713 Req 7 {'PASSED' if rain_reliability >= SafetyConstants.WEATHER_ACCURACY_THRESHOLD else 'FAILED'}\n")

        print("Testing Req 10: Sensor Failure Response")
        self.aeb_system.sensor_system.simulate_sensor_failure("camera")
        self.aeb_system.sensor_system.simulate_sensor_failure("radar")
        failure_result = self.aeb_system.process_scenario(emergency_scenario)
        fail_safe_activated = failure_result['decision']['action'] == 'FAIL_SAFE'
        print(f"Fail-safe activated on sensor failure: {fail_safe_activated}")
        print(f"\u2713 Req 10 {'PASSED' if fail_safe_activated else 'FAILED'}\n")

        print("=== Performance Summary ===")
        report = self.aeb_system.get_performance_report()
        for key, value in report.items():
            if key != 'event_log':
                print(f"{key}: {value}")
        return report
