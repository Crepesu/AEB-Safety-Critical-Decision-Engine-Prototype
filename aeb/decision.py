
"""Legacy shim: decision engine moved to ``aeb.core.decision`` (deprecated path).

Migrate to::

	from aeb.core.decision import SafetyDecisionEngine

This shim proxies public names; scheduled for removal in 0.4.0.
"""
from .core import decision as _core_decision
from ._shim import publish_shim as _publish_shim

_publish_shim(globals(), _core_decision, "aeb.decision", "aeb.core.decision")
