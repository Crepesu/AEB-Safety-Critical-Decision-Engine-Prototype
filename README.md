# AEB Safety-Critical Decision Engine Prototype

Prototype for an Autonomous Emergency Braking (AEB) decision engine focused on pedestrian and cyclist protection in urban scenarios. Implements simplified requirement-driven logic for detection, threat assessment, and decision-making.

## Features
- Modular architecture (sensors, threat assessment, decision engine, simulation)
- Requirement-linked constants for traceability
- Simulation harness validating key safety requirements (detection range, TTC threshold, response time, weather, fail-safe)
- Performance reporting and event logging for emergency braking

## Quick Start
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Package Layout
```
aeb/
  constants.py
  enums.py
  models.py
  sensors.py
  threat.py
  decision.py
  system.py
  simulation.py
main.py
```

## Core Requirements (Subset Demonstrated)
1. Detection range: 50m
2. Detection accuracy: ≥95% (simulated metric)
4. Time-To-Collision threshold: 1.5s vulnerable users (1.0s vehicles)
5. Warning issued 0.5s before braking when possible
6. Decision response time <100ms
7. Weather robustness ≥90% reliability
10. Fail-safe on significant sensor failure
12. Emergency event logging

## Running Tests
(Will be added with basic pytest style tests under `tests/`).

## License
MIT
