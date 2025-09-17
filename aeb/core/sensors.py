"""Core sensor system implementation (relocated).

Security / Quality:
	Uses SystemRandom for stochastic drops / noise to eliminate Sonar hotspot
	(python:S2245). Crypto strength not required but harmless here.
"""
import random
import numpy as np
from typing import List
from .enums import WeatherCondition, ObjectType
from .models import DetectedObject
from .constants import SafetyConstants

RNG = random.SystemRandom()

class SensorSystem:
	def __init__(self):
		self.camera_operational = True
		self.radar_operational = True
		self.lidar_operational = True
		self.weather_condition = WeatherCondition.CLEAR
		self.extra_degradation_prob = 0.0

	def set_detection_degradation(self, active: bool, probability: float = 0.35):
		if active:
			self.extra_degradation_prob = max(0.0, min(1.0, probability))
		else:
			self.extra_degradation_prob = 0.0

	def set_weather_condition(self, weather: WeatherCondition):
		self.weather_condition = weather

	def simulate_sensor_failure(self, sensor_type: str):
		if sensor_type == "camera":
			self.camera_operational = False
		elif sensor_type == "radar":
			self.radar_operational = False
		elif sensor_type == "lidar":
			self.lidar_operational = False

	def get_sensor_reliability(self) -> float:
		operational_sensors = sum([
			self.camera_operational,
			self.radar_operational,
			self.lidar_operational
		])
		weather_factor = {
			WeatherCondition.CLEAR: 1.0,
			WeatherCondition.LIGHT_RAIN: 0.90,
			WeatherCondition.FOG: 0.75,
			WeatherCondition.NIGHT: 0.92
		}[self.weather_condition]
		return (operational_sensors / 3.0) * weather_factor

	def detect_objects(self, scenario_objects: List[dict]) -> List[DetectedObject]:
		detected_objects = []
		reliability = self.get_sensor_reliability()
		for i, obj in enumerate(scenario_objects):
			if self.extra_degradation_prob > 0 and RNG.random() < self.extra_degradation_prob:
				continue
			if RNG.random() < reliability:
				noise_factor = 1 - reliability * 0.1
				detected_obj = DetectedObject(
					id=i,
					type=ObjectType(obj['type']),
					position=(
						obj['position'][0] + RNG.gauss(0, noise_factor),
						obj['position'][1] + RNG.gauss(0, noise_factor)
					),
					velocity=obj['velocity'],
					confidence=reliability * RNG.uniform(0.9, 1.0),
					distance=np.sqrt(obj['position'][0]**2 + obj['position'][1]**2),
					size=obj['size']
				)
				if detected_obj.distance <= SafetyConstants.MAX_DETECTION_RANGE:
					detected_objects.append(detected_obj)
		return detected_objects
