
"""Legacy shim: constants moved to ``aeb.core.constants``.

Deprecated path – please migrate to::

	from aeb.core.constants import SafetyConstants

This shim now avoids ``import *`` to satisfy linters while still re-exporting
the public API defined in ``aeb.core.constants.__all__``.

Scheduled for removal in 0.4.0; migrate soon.
"""
from .core import constants as _core_constants
from ._shim import publish_shim as _publish_shim

_publish_shim(globals(), _core_constants, "aeb.constants", "aeb.core.constants")
