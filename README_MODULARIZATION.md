# AEB Prototype Modularization & Architecture Update

## Overview
The project has been refactored to introduce a clearer modular architecture:

- `aeb/core/` now contains the actual implementations for constants, enums, models, sensors, threat assessment, decision engine, and system integration.
- Top‑level legacy shim modules retained temporarily (now emit DeprecationWarnings) to ease migration; planned removal in a future release.
- GUI has been componentized under `aeb/ui/components/`:
  - `canvas_view.py` encapsulates drawing and resize handling.
  - `panels/controls_panel.py`, `status_panel.py`, `history_panel.py`, `metrics_panel.py` provide discrete UI sections.
- A centralized theming system lives in `aeb/theme.py` (theme toggle UI intentionally deferred).

## Key Benefits
- Easier maintenance and extension (add new panels or core logic without touching monoliths).
- Clear separation between domain logic (`aeb/core`) and presentation (`aeb/ui`).
- Leaner package surface (only one authoritative implementation of each module under `aeb/core`).
- Resizable canvas with responsive redrawing via `CanvasView` and static/dynamic layers for performance.

## New Structure (excerpt)
```
aeb/
  core/
    constants.py
    enums.py
    models.py
    sensors.py
    threat.py
    decision.py
    system.py
    simulation.py
  ui/
    components/
      canvas_view.py
      panels/
        controls_panel.py
        status_panel.py
        history_panel.py
        metrics_panel.py
  theme.py
  aeb_gui.py
```

## Updating Imports
Preferred (explicit layout):
```python
from aeb.core.system import AEBSystem
```

Package root convenience re-exports exist for frequently used symbols:
```python
from aeb import AEBSystem, SafetyConstants
```
This is optional; explicit `aeb.core.*` imports are clearer.

## Extending the GUI
To add a new panel:
1. Create a file under `aeb/ui/components/panels/your_panel.py`.
2. Subclass `tk.Frame` and expose minimal methods.
3. Instantiate and pack/grid it inside `AEBGuiApp.create_widgets` (or refactor into a layout manager).

## Theming
Use color/font tokens from `aeb/theme.py` instead of hardcoding values. This prepares for a future runtime theme switch.

## Canvas Rendering Notes
`CanvasView` separates static elements (road, lane markings) from dynamic objects to minimize redraw cost. On resize, static is re-rendered and dynamic layer is repainted with scaling.

## Migration Guidance
Legacy shim modules now warn on import. Update any remaining legacy imports (`from aeb.system ...`) to `from aeb.core.system ...`.

Deprecation note: Shims are scheduled for removal in **0.4.0**. A small internal helper (`aeb/_shim.py`) centralizes the proxy + warning logic to keep maintenance overhead low until removal. Begin migrating now to avoid future breaks.

See the main `README.md` for consolidated "How to Run" instructions (GUI, simulation, tests, programmatic usage).

## Next Potential Improvements
- Add theme toggle UI (deferred per instructions).
- Introduce unit tests for panel components and core relocation integrity.
- Factor out metrics aggregation into its own service class.
- Add packaging metadata (`pyproject.toml`) for distribution.

---
Updated after shim removal cleanup.
