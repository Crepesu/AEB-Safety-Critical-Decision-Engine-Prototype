"""Core enums (relocated)."""
from enum import Enum

class ObjectType(Enum):
	PEDESTRIAN = "pedestrian"
	CYCLIST = "cyclist"
	VEHICLE = "vehicle"
	STATIC_OBSTACLE = "static"
	UNKNOWN = "unknown"

class WeatherCondition(Enum):
	CLEAR = "clear"
	LIGHT_RAIN = "light_rain"
	FOG = "fog"
	NIGHT = "night"

class SystemState(Enum):
	OPERATIONAL = "operational"
	WARNING = "warning"
	EMERGENCY_BRAKING = "emergency_braking"
	SENSOR_FAILURE = "sensor_failure"
	FAIL_SAFE = "fail_safe"
