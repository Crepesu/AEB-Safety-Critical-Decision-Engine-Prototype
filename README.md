# AEB Safety-Critical Decision Engine Prototype

Prototype for an Autonomous Emergency Braking (AEB) decision engine focused on pedestrian and cyclist protection in urban scenarios. Implements simplified requirement-driven logic for detection, threat assessment, and decision-making.

## Features
- Modular architecture (sensors, threat assessment, decision engine, simulation)
- Requirement-linked constants for traceability
- Simulation harness validating key safety requirements (detection range, TTC threshold, response time, weather, fail-safe)
- Performance reporting and event logging for emergency braking

## Quick Start
```powershell
# Create & activate virtual environment (Windows PowerShell)
python -m venv .venv
./.venv/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt

# (Option 1) Launch the Tkinter GUI prototype (one-shot & animated modes)
# Preferred (module form adds project root automatically):
python -m aeb.aeb_gui

# Alternate (direct file) – now supported via runtime path fix:
python aeb/aeb_gui.py

# (Option 2) Run simulation requirement validation (prints requirement checks)
python -c "from aeb.core.simulation import AEBSimulation; AEBSimulation().run_requirement_validation_tests()"

# (Option 3) Programmatic usage example
python -c "from aeb.core.system import AEBSystem; s=AEBSystem(); r=s.process_scenario([{'type':'pedestrian','position':[12.0,1.0],'velocity':[0,0],'size':[0.6,1.8]}]); print(r['decision'], r['min_ttc'])"

# (Installed) Package root convenience imports
python -c "from aeb import AEBSystem, SafetyConstants; print('TTC threshold', SafetyConstants.MIN_TTC_THRESHOLD)"
```

### Running the GUI
The GUI provides both a single-evaluation mode and an animated time‑stepped mode of the AEB decision engine.

Core actions (right control panel):
1. Run Random Scenario – one-shot evaluation of a random scenario.
2. Setup Manual Scenario – dialog to add one object with chosen type & distance.
3. Run Animated Scenario – starts a time-stepped simulation updating positions & TTC.
4. Stop Animation – terminates an active animated run.
5. Clear – resets the canvas & status indicators.

Visual elements:
- Ego vehicle (rounded rectangle) color encodes state: blue=normal, amber=warning, red=braking.
- Colored circles: detected objects (red=pedestrian, green=cyclist, yellow=vehicle).
- Dashed white center line over a gray road.
- Status section shows: System State, Warning, Braking (color‑coded) plus live Min TTC in animation.

Animated mode differences:
- Objects move toward the ego vehicle at a constant ego speed (≈13.9 m/s) minus object velocity.
- Min TTC label updates each tick.
- Simulation stops on: emergency braking, collision threshold, max time, or user stop.

Log panel (now scrollable) contents:
- Count of detected objects
- Threat evaluation (and min TTC if applicable)
- System state string
- Decision action (monitor / warning / emergency_brake)
- Warning + braking flags
- Human‑readable message

### Manual Scenario Tips
- Distance (m) is longitudinal distance in front of ego vehicle.
- Lateral (m) negative is left, positive is right (approx 1 m → 20 px vertical shift).
- Object types: `pedestrian`, `cyclist`, `vehicle`.

### Exiting
Close the window normally or press Ctrl+C in the terminal if foreground‑blocked.

### Troubleshooting
- If fonts look odd, they fall back to system defaults; optional tweak in `aeb_gui.py`.
- Ensure you are running Python 3.10+ (per `pyproject.toml`).
- If you modify core logic modules, the GUI picks up changes on next run (no hot reload).
- `ModuleNotFoundError: No module named 'aeb'` when using `python aeb/aeb_gui.py`: this file now injects the parent directory into `sys.path`, but if issues persist run via `python -m aeb.aeb_gui` from the project root.

## Package Layout (0.3.0+)
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
Legacy flat shim modules are still present for backward compatibility but now emit DeprecationWarnings. Migrate to `aeb.core.*` imports.

### Deprecation Schedule (Shim Modules)
The former flat modules (`aeb.constants`, `aeb.enums`, `aeb.models`, `aeb.sensors`, `aeb.threat`, `aeb.decision`, `aeb.system`) are deprecated.

| Deprecated Import | Preferred Replacement | Notes |
|-------------------|-----------------------|-------|
| `from aeb.system import AEBSystem` | `from aeb.core.system import AEBSystem` | Shim emits a DeprecationWarning |
| `from aeb.decision import SafetyDecisionEngine` | `from aeb.core.decision import SafetyDecisionEngine` | Proxy re-export only |
| `from aeb.threat import ThreatAssessment` | `from aeb.core.threat import ThreatAssessment` | Same symbols re-exported |
| `from aeb.sensors import SensorSystem` | `from aeb.core.sensors import SensorSystem` | 1:1 mapping |
| `from aeb.models import DetectedObject` | `from aeb.core.models import DetectedObject` | 1:1 mapping |
| `from aeb.enums import WeatherCondition` | `from aeb.core.enums import WeatherCondition` | Enum set unchanged |
| `from aeb.constants import SafetyConstants` | `from aeb.core.constants import SafetyConstants` | Constants unchanged |

Removal target: version **0.4.0**. Update any remaining legacy imports before upgrading to 0.4.x.

Rationale: Keeps backward compatibility for a short window while encouraging explicit, clearer module paths.

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
```powershell
./.venv/Scripts/Activate.ps1
pytest -q
```
Tests currently exercise detection range, TTC emergency triggering, weather reliability, warning→brake transition, and detection accuracy sampling.

If `pytest` is not installed:
```powershell
pip install pytest
```

## How to Run (Summary)
| Mode | Command | Notes |
|------|---------|-------|
| GUI | `python aeb/aeb_gui.py` | Interactive, resizable canvas, panels, animated & one-shot modes |
| Simulation (requirements) | See Option 2 command above | Prints pass/fail for key requirements |
| Programmatic (library) | Import `AEBSystem` from `aeb.core.system` | Integrate into other tooling |
| Tests | `pytest -q` | Ensure environment activated |

## Migration (Pre-0.3.0 -> 0.3.0)
Replace imports: `from aeb.system import AEBSystem` → `from aeb.core.system import AEBSystem`.
Root re-exports exist for convenience but explicit `aeb.core.*` is preferred.

## Continuous Integration (Jenkins)
This repository contains a declarative `Jenkinsfile` that defines the CI pipeline:

Stages (High HD variant):
1. Checkout – Retrieves the source.
2. Setup Python – venv + dependencies + toolchain (pytest-cov, flake8, coverage, bandit, pip-audit, sonar-scanner).
3. Lint – Style / basic static checks (`flake8`).
4. Tests – Pytest with coverage + JUnit XML + Cobertura XML.
5. Code Quality – SonarQube scan (`sonar-project.properties` governs sources/tests & coverage linkage). Non-blocking by default; gate later.
6. Security – Dependency scan (`pip-audit`) + static security scan (`bandit`) archiving JSON outputs for triage.
7. Build Artifact – Wheel build archived for promotion.
8. Build Docker Image – Container image of service (`Dockerfile`).
9. Deploy (Test Env) – Runs container locally, health check via `/health`.
10. Monitoring (Smoke) – Calls `/sample-decision` to validate runtime logic & archives response.
11. Release – Simulated tagging step (extend to real publish flow as needed).

Artifacts & Reports:
- Coverage: `coverage.xml` (Cobertura) published via `publishCoverage` (requires Jenkins Coverage plugin or equivalent).
- Wheel artifact(s): archived under `dist/*.whl` for download.
- (Optional) JUnit XML: Add `--junitxml=junit-results.xml` to pytest command if you want rich test trend charts; current config leaves JUnit step permissive.

Required Jenkins Plugins (recommended):
- Pipeline
- Warnings NG (optional for lint parsing)
- Cobertura or Generic Coverage (depending on Jenkins version; recent versions use built-in Coverage API)
- AnsiColor

To enable stricter quality gates:
```groovy
// Replace in Tests stage steps block
sh "${VENV_DIR}/bin/pytest --junitxml=junit-results.xml -q --cov=aeb --cov-report=xml:${COVERAGE_FILE} --cov-report=term --maxfail=1"
// Make Lint fail build
sh "${VENV_DIR}/bin/flake8 aeb" // remove || true
```

Windows Agents:
If using Windows nodes, replace `sh` with `powershell` steps and adapt venv path (`${VENV_DIR}\\Scripts\\python.exe`). For example:
```groovy
powershell "python -m venv ${VENV_DIR}"
powershell "${VENV_DIR}\\Scripts\\pip install -r requirements.txt"
```

Parallelization (future):
You can split lint and tests:
```groovy
stage('Quality') {
  parallel {
    stage('Lint') { steps { sh "${VENV_DIR}/bin/flake8 aeb" } }
    stage('Tests') { steps { sh "${VENV_DIR}/bin/pytest -q --cov=aeb --cov-report=xml:${COVERAGE_FILE}" } }
  }
}
```

Environment Caching:
For faster builds, you can cache the `.venv` or `~/.cache/pip` directory using a Jenkins node-level cache or wrapper like `pip-cache` plugin.

Security Note:
Never run untrusted PRs with automatic packaging publish steps. Keep deployment/publish (e.g., to PyPI) in a separate, restricted pipeline with manual approval.

### SonarCloud / SonarQube Setup
See `docs/SONARQUBE_SETUP.md` for detailed provisioning & `docs/CI_WEBHOOKS.md` for webhook automation.

Minimal CI integration pattern (token from Jenkins credentials, version injected at runtime):
```groovy
withSonarQubeEnv('SonarLocal') {
  withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
    sh """
      ${VENV_DIR}/bin/sonar-scanner \
        -Dproject.settings=sonar-project.properties \
        -Dsonar.projectVersion=${BUILD_NUMBER}
    """
  }
}
```
Quality Gate stage (fast feedback when webhook configured):
```groovy
stage('Quality Gate') {
  steps {
    timeout(time: 3, unit: 'MINUTES') {
      script {
        def qg = waitForQualityGate()
        if (qg.status != 'OK') error "Quality Gate failed: ${qg.status}" 
      }
    }
  }
}
```
Best practices:
- Do NOT commit a `sonar.token` property; rely on CI env variable injection.
- Keep `sonar.sources` narrowed to code directories to avoid noise.
- Use coverage + quality gate on *new code* to raise standards incrementally.

### Security Scanning
- pip-audit: Reports vulnerable dependencies (JSON archived as `pip-audit.json`). Resolve by upgrading pinned versions.
- bandit: Flags insecure code patterns (JSON archived as `bandit.json`). Mark acceptable false positives with inline `# nosec` and explain in PR.

### Deployment / Test Environment
The pipeline spins up a disposable container named `aeb_test` exposing port 8000. Endpoints:
 - `/health` – basic liveness
 - `/sample-decision` – executes a sample scenario via `AEBSystem` for integration validation

To externalize deployment (e.g., staging host): replace Docker run step with remote SSH / Kubernetes / ECS action.

### Monitoring & Alerting (Extension Ideas)
- Integrate a lightweight Prometheus exporter inside `service.py` (add `/metrics`).
- Hook Jenkins post-deploy stage to query metrics or error rate and fail fast if thresholds exceeded.
- Add uptime synthetic check (curl in a loop) with backoff; record latency distribution.

### Release Promotion
Current stage simulates tagging. For a real release flow:
1. Require manual `input` approval step.
2. Push Docker image to registry (e.g., `docker.withRegistry`).
3. Publish wheel to an internal PyPI (twine) with signed artifacts.
4. Create Git tag and GitHub/GitLab release notes automatically parsing CHANGELOG section.

### Quality Gates (Recommended Targets)
| Metric | Suggested Gate | Tool |
|--------|----------------|------|
| Coverage | >= 80% line | pytest + coverage |
| Lint errors | 0 critical | flake8 |
| Bandit high | 0 | bandit |
| Deprecated shims | Decreasing count | custom grep check |
| New vulnerabilities | 0 | pip-audit |

Add gates by turning non-fatal commands into hard failures & evaluating JSON outputs.

## License
MIT
