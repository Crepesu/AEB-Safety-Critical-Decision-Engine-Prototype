"""AEB Safety-Critical Decision Engine Prototype package.

Public API now sources symbols directly from the ``aeb.core`` subpackage.
Legacy top-level shim modules have been removed to reduce redundancy.

Import examples:

    from aeb.core.system import AEBSystem
    from aeb.core.constants import SafetyConstants

Convenience re-exports are provided at the package root for the most
commonly used classes; explicit ``aeb.core`` imports remain the
recommended style for clarity.
"""

from .core.constants import SafetyConstants
from .core.enums import ObjectType, WeatherCondition, SystemState
from .core.models import DetectedObject
from .core.sensors import SensorSystem
from .core.threat import ThreatAssessment
from .core.decision import SafetyDecisionEngine
from .core.system import AEBSystem
from .core.simulation import AEBSimulation

__all__ = [
    "SafetyConstants",
    "ObjectType",
    "WeatherCondition",
    "SystemState",
    "DetectedObject",
    "SensorSystem",
    "ThreatAssessment",
    "SafetyDecisionEngine",
    "AEBSystem",
    "AEBSimulation",
]
