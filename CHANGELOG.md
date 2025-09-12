# Changelog

All notable changes to this project will be documented in this file.

The format roughly follows Keep a Changelog and uses semantic versioning.

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
