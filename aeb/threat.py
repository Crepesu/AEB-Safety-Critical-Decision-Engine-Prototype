
"""Legacy shim: threat assessment moved to ``aeb.core.threat`` (deprecated path).

Migrate to::

	from aeb.core.threat import ThreatAssessment

This shim proxies the public API; scheduled for removal in 0.4.0.
"""
from .core import threat as _core_threat
from ._shim import publish_shim as _publish_shim

_publish_shim(globals(), _core_threat, "aeb.threat", "aeb.core.threat")
