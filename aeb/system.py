
"""Legacy shim: AEB system moved to ``aeb.core.system`` (deprecated path).

Migrate to::

	from aeb.core.system import AEBSystem

Scheduled for removal in 0.4.0; update imports.
"""
from .core import system as _core_system
from ._shim import publish_shim as _publish_shim

_publish_shim(globals(), _core_system, "aeb.system", "aeb.core.system")
