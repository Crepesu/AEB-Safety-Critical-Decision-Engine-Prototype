
"""Legacy shim: enums moved to ``aeb.core.enums`` (deprecated path).

Migrate to::

	from aeb.core.enums import WeatherCondition

Scheduled for removal in 0.4.0; migrate imports now.
"""
from .core import enums as _core_enums
from ._shim import publish_shim as _publish_shim

_publish_shim(globals(), _core_enums, "aeb.enums", "aeb.core.enums")
