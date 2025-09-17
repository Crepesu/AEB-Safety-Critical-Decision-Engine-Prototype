
"""Legacy shim: sensors moved to ``aeb.core.sensors`` (deprecated path).

Migrate to::

	from aeb.core.sensors import SensorSystem

Scheduled for removal in 0.4.0; migrate soon.
"""
from .core import sensors as _core_sensors
from ._shim import publish_shim as _publish_shim

_publish_shim(globals(), _core_sensors, "aeb.sensors", "aeb.core.sensors")
