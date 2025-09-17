# Changelog

All notable changes to this project will be documented in this file.

The format roughly follows Keep a Changelog and uses semantic versioning.

## [0.3.0] - 2025-09-18
### Documentation
- Added `docs/CI_WEBHOOKS.md` describing GitHub → Jenkins and Sonar webhook setup.
- Expanded `docs/SONARQUBE_SETUP.md` with SonarCloud variant, token best practices, PR decoration guidance.
- Updated README: unified SonarCloud/SonarQube section, removed inline `sonar.login` example, added quality gate best practices and cross-links.
### Security / Quality
- Dockerfile now runs as non-root user `appuser`.
- Optional HTTPS support added to `service.py` (TLS when cert/key env vars provided).
- Replaced default RNG with `SystemRandom` in simulation & sensors to address security hotspot (S2245) and documented rationale.
### Breaking / Deprecated
- Marked top-level shim modules (`aeb/constants.py`, `enums.py`, `models.py`, `sensors.py`, `threat.py`, `decision.py`, `system.py`, `simulation.py`) as deprecated; they now emit DeprecationWarnings. Canonical modules live under `aeb/core/`.
- Eliminated dynamic fallback import logic in `aeb/__init__.py`; package root re-exports selected core symbols directly.

### Added
- Componentized GUI panels: controls, status, metrics, and scenario history under `aeb/ui/components/panels/`.
- `CanvasView` abstraction with resize handling and static vs dynamic layer separation for performance.
- Central theming module `aeb/theme.py` providing palette & font tokens (future runtime theme toggle ready).
- Simulation class relocated to `aeb/core/simulation.py` and re-exported for convenience through package root.

### Changed
- Refactored root package export surface to a stable curated API (see README for preferred `aeb.core.*` imports).
- Updated `README_MODULARIZATION.md` to reflect finalized structure and removal of legacy compatibility layer.
- Updated main README to (pending update) reflect new directory layout (old flat layout deprecated).

### Fixed
- Removed indentation and structural issues introduced during earlier GUI refactors; stabilized redraw logic.

### Migration Notes
- Replace imports like `from aeb.system import AEBSystem` with `from aeb.core.system import AEBSystem`.
- Deprecation: shim modules will be removed in a future release (target e.g. 0.4.0); begin migration now.

### Internal
- Simplified package initialization eliminating dynamic module scanning for lower import overhead.
 - Added centralized shim utility (`aeb/_shim.py`) to standardize deprecation warnings & re-exports; announced 0.4.0 removal target for legacy flat modules.

---

## [0.1.3] - 2025-09-17
## [0.1.4] - 2025-09-18
### Added
- Scenario history panel with replay & clear options (stores last 20 scenarios).
- Metrics panel tracking total scenarios, threats encountered, and brake events.
- Degradation probability slider (active when detection degradation enabled).
- Performance optimization: static road retained; only dynamic canvas items redrawn each tick.
- Unit tests for GUI utility `choose_color` function.

### Changed
- Refactored metrics update logic into smaller helper methods (reduced complexity).
- Integrated weather & degradation UI grouping with probability control.

### Removed
- Obsolete bottom-right Min TTC label (now only in log for clarity).

### Notes
- Foundation for modular theming & layout grid refactor prepared (pending next release).

### Added
- Scrollable log panel (vertical scrollbar) for improved visibility of multi-line decision output.
- Dynamic ego vehicle color in BOTH one-shot and animated modes (amber = warning, red = braking) for immediate state feedback.

### Changed
- Enlarged window geometry (wider canvas 720px & taller layout) for clearer spatial context and separation of panels.
- Visualization pipeline (single-shot) now processes decision before drawing ego vehicle to apply color state.

### Fixed
- Residual indentation issues introduced during prior layout refactor.

### Notes
- Animation still uses constant ego speed; braking deceleration modeling remains a future enhancement.

## [0.1.1] - 2025-09-17
## [0.1.2] - 2025-09-17
### Added
- Animated scenario mode with time-stepped TTC updates and stop conditions (brake, collision threshold, max duration, manual stop).
- Dynamic minimum TTC label in GUI status panel.

### Changed
- README updated to document animated mode workflow.

### Notes
- Ego speed modeled as constant; future enhancement: apply deceleration profile after braking.

### Added
- High-fidelity Tkinter GUI (`aeb/aeb_gui.py`) for visualizing scenarios, decisions, and system status.
- Comprehensive inline documentation & module docstrings across GUI for educational clarity.

### Changed
- Refactored GUI status display logic to reduce cognitive complexity (extracted `choose_color`, classification sets).
- Expanded README with GUI usage instructions and test invocation examples.

### Fixed
- Indentation / structural issues introduced during earlier GUI refactor pass.

### Notes
- GUI currently performs single-shot scenario evaluation (no time-step animation yet). Planned enhancement: iterative simulation + TTC updates.
## [0.1.0] - 2025-09-12
### Added
- Initial modular AEB safety-critical decision engine prototype.
- Package structure: sensors, threat assessment, decision engine, system integration, simulation harness.
- Requirement-linked constants and enums.
- Safety decision logic with warning vs emergency braking and fail-safe on sensor degradation.
- Event logging for emergency braking and response time violation tracking.
- Weather reliability modeling with calibrated rain performance.
- Basic unit tests: detection range, TTC emergency triggering, weather reliability, warning→brake transition, detection accuracy sampling.
- Packaging: `pyproject.toml`, `requirements.txt`.
- Documentation: README with quick start and requirement overview.

### Changed
- Calibrated weather factors to meet reliability threshold (LIGHT_RAIN set to 0.90, NIGHT 0.92).
- Improved detection accuracy calculation to consider only in-range actual objects.

### Known Gaps / Future
- Availability (Req 8) simulation pending.
- False positive per distance (Req 9) modeling pending.
- Enhanced Monte Carlo metrics export and CI gating to be added.
- Vision (OpenCV) integration deferred to later phase.

---
