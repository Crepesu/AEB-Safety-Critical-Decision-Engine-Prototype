
"""Legacy shim: models moved to ``aeb.core.models`` (deprecated path).

Migrate to::

	from aeb.core.models import DetectedObject

Scheduled for removal in 0.4.0; please migrate.
"""
from .core import models as _core_models
from ._shim import publish_shim as _publish_shim

_publish_shim(globals(), _core_models, "aeb.models", "aeb.core.models")
