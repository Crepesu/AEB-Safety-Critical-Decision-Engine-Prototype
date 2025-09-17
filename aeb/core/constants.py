"""Core constants module (relocated)."""

class SafetyConstants:
	MAX_DETECTION_RANGE = 50.0      # Req 1: 50m detection range
	MIN_TTC_THRESHOLD = 1.5         # Req 4: 1.5s TTC threshold
	MAX_RESPONSE_TIME = 0.1         # Req 6: 100ms response time
	WARNING_ADVANCE_TIME = 0.5      # Req 5: 0.5s warning before braking
	MIN_DETECTION_ACCURACY = 0.95   # Req 2: 95% classification accuracy
	WEATHER_ACCURACY_THRESHOLD = 0.9 # Req 7: 90% accuracy in adverse weather
	MAX_FALSE_POSITIVE_RATE = 0.0001 # Req 9: <1 per 10,000km
	REQUIRED_AVAILABILITY = 0.9999   # Req 8: 99.99% availability
