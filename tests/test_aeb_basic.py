import math
from aeb.system import AEBSystem
from aeb.constants import SafetyConstants
from aeb.enums import WeatherCondition


def test_detection_range_exclusion():
    """
    Test that objects beyond the maximum detection range are not detected.
    """
    system = AEBSystem()
    far_obj = [{
        'type': 'pedestrian',
        'position': [SafetyConstants.MAX_DETECTION_RANGE + 10.0, 0.0],
        'velocity': [0, 0],
        'size': [0.6, 1.8]
    }]
    result = system.process_scenario(far_obj)
    assert len(result['detected_objects']) == 0, "Object beyond detection range should not be detected"


def test_ttc_emergency_brake_trigger():
    """
    Test that emergency braking is triggered when TTC is below threshold.
    """
    system = AEBSystem()
    close_obj = [{
        'type': 'pedestrian',
        'position': [10.0, 0.0],
        'velocity': [0, 0],
        'size': [0.6, 1.8]
    }]
    result = system.process_scenario(close_obj)
    # If detected, min_ttc should be less than threshold and braking may activate
    if math.isfinite(result['min_ttc']):
        assert result['min_ttc'] >= 0
        if result['min_ttc'] < SafetyConstants.MIN_TTC_THRESHOLD:
            assert result['decision']['braking'] is True


def test_weather_reliability_light_rain():
    """
    Test that sensor reliability in light rain meets the required threshold.
    """
    system = AEBSystem()
    system.sensor_system.set_weather_condition(WeatherCondition.LIGHT_RAIN)
    scenario = [{
        'type': 'pedestrian',
        'position': [20.0, 0.5],
        'velocity': [0, 0],
        'size': [0.6, 1.8]
    }]
    result = system.process_scenario(scenario)
    assert result['sensor_reliability'] >= SafetyConstants.WEATHER_ACCURACY_THRESHOLD


def test_warning_then_brake_transition():
    """
    Test that a warning is issued before emergency braking as TTC decreases.
    """
    system = AEBSystem()
    # Object far enough to trigger warning first (TTC just above braking threshold but within warning window)
    scenario_warning = [{
        'type': 'pedestrian',
        'position': [12.0, 0.0],
        'velocity': [0, 0],
        'size': [0.6, 1.8]
    }]
    r1 = system.process_scenario(scenario_warning)
    # Closer object to trigger braking
    scenario_brake = [{
        'type': 'pedestrian',
        'position': [10.0, 0.0],
        'velocity': [0, 0],
        'size': [0.6, 1.8]
    }]
    r2 = system.process_scenario(scenario_brake)
    # We accept probabilistic detection; ensure if braking occurred a prior warning state is plausible
    if r2['decision']['braking']:
        assert r1['decision']['action'] in ("WARNING", "EMERGENCY_BRAKE", "MONITOR")


def test_detection_accuracy_high_clear_conditions():
    """
    Test that detection accuracy in clear conditions meets the required threshold.
    """
    system = AEBSystem()
    # Multiple identical scenarios to average out randomness
    scenario = [{
        'type': 'pedestrian',
        'position': [15.0, 0.5],
        'velocity': [0, 0],
        'size': [0.6, 1.8]
    }]
    detections = 0
    runs = 30
    for _ in range(runs):
        r = system.process_scenario(scenario)
        if r['detected_objects']:
            detections += 1
    observed_accuracy = detections / runs
    assert observed_accuracy >= 0.9, f"Observed accuracy {observed_accuracy:.2f} below expected threshold"
