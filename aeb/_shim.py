"""Internal utilities for legacy shim modules.

Not part of the public API. These helpers exist solely to reduce duplicated
boilerplate while the deprecated top-level shim modules remain available.
"""
from __future__ import annotations

from types import ModuleType
from typing import Dict, Any
import warnings

def publish_shim(
	target_globals: Dict[str, Any],
	core_module: ModuleType,
	deprecated_module_path: str,
	new_module_path: str,
	removal_version: str = "0.4.0",
) -> None:
	"""Populate a deprecated shim module namespace.

	Parameters
	----------
	target_globals:
		The ``globals()`` dict of the shim module.
	core_module:
		Imported core module object whose public names (``__all__``) will be re-exported.
	deprecated_module_path:
		Fully-qualified import path of the deprecated shim (e.g. ``'aeb.system'``).
	new_module_path:
		Replacement module path (e.g. ``'aeb.core.system'``).
	removal_version:
		Planned version in which the shim will be removed.
	"""
	public = list(getattr(core_module, "__all__", []))
	target_globals["__all__"] = public
	for name in public:
		# Re-export each symbol.
		target_globals[name] = getattr(core_module, name)

	# One-time deprecation warning sentinel key (module segment uppercased)
	segment = deprecated_module_path.rsplit(".", 1)[-1].upper()
	sentinel = f"_AEB_SHIM_WARNED_{segment}"
	if not target_globals.get(sentinel):
		warnings.warn(
			f"Importing from '{deprecated_module_path}' is deprecated; use '{new_module_path}'. "
			f"Scheduled for removal in {removal_version}.",
			DeprecationWarning,
			stacklevel=2,
		)
		target_globals[sentinel] = True

__all__ = ["publish_shim"]