## SonarQube Integration Guide

### 1. Run Local SonarQube (Optional)
If you want a local server instead of SonarCloud, spin up SonarQube + Postgres using the provided compose file:
```bash
docker compose -f docker-compose.sonar.yml up -d
```
Access UI at: http://localhost:9000 (default credentials: admin / admin – you will be prompted to change password).

### 2. Create Project & Token (SonarQube or SonarCloud)
SonarQube (self-hosted): Projects → Create Project → Manually → use key matching `sonar.projectKey`.
SonarCloud: After login, click *+* → *Analyze new project* → select the GitHub repo; project key auto-generated (can override). 
Then generate a user token (My Account → Security) and store it in Jenkins Credentials as Secret Text (`SONAR_TOKEN`).

### 3. Configure Jenkins
Global Configuration:
1. Add Sonar server (Manage Jenkins → System → SonarQube servers) with a name (e.g., `SonarLocal`). For SonarCloud include the URL `https://sonarcloud.io` and optionally organization.
2. Ensure *SonarQube Scanner* or built-in tool is available (Manage Jenkins → Tools) OR use a container/agent with scanner pre-installed.

Update the Jenkinsfile Code Quality stage (example – token injected, version dynamic):
```groovy
stage('Code Quality') {
  steps {
    withSonarQubeEnv('SonarLocal') {
      withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
        sh "${VENV_DIR}/bin/sonar-scanner -Dproject.settings=sonar-project.properties -Dsonar.login=${SONAR_TOKEN}"
      }
    }
  }
}
```
Add quality gate wait (after scan, before security or deploy):
```groovy
stage('Quality Gate') {
  steps {
    timeout(time: 5, unit: 'MINUTES') {
      waitForQualityGate abortPipeline: true
    }
  }
}
```

### 4. Webhook (Quality Gate Feedback)
SonarQube/SonarCloud notifies Jenkins via webhook so `waitForQualityGate` returns promptly.

In SonarQube UI: Administration → Configuration → Webhooks → Create:
| Field | Value |
|-------|-------|
| Name | Jenkins |
| URL | http://<jenkins-host>/sonarqube-webhook/ |

No secret required unless you configured one. Jenkins must have SonarQube plugin which exposes the `/sonarqube-webhook/` endpoint.

### 5. `sonar-project.properties` Highlights & Hardening
| Property | Purpose | Recommendation |
|----------|---------|----------------|
| `sonar.sources` | Source roots | Narrow to code dirs (e.g., `aeb,service.py`) |
| `sonar.tests` | Tests directory | Keep tests out of sources to avoid duplication noise |
| `sonar.python.coverage.reportPaths` | Coverage linkage | Ensure generated before scan |
| `sonar.exclusions` | Skip non-essential files | Exclude shim, cache, generated code |
| `sonar.cpd.exclusions` | Duplication ignore | Keep tests excluded |
| (omit) `sonar.token` | Secret auth | Remove from file; rely on env `SONAR_TOKEN` |
| (optional) `sonar.coverage.exclusions` | Exclude UI / glue | Use for hard-to-test peripheral code |

### 6. Local Manual Scan (Optional)
You can run locally (needs `sonar-scanner` installed):
```bash
pytest -q --cov=aeb --cov-report=xml:coverage.xml
sonar-scanner -Dproject.settings=sonar-project.properties -Dsonar.login=<TOKEN>
```

### 7. Sample Webhook Payload
`sonar-webhook.example.json` in repo outlines typical structure; Jenkins plugin parses it automatically.

### 8. Adding a Quality Gate
In SonarQube: Quality Gates → Create or edit → Conditions (e.g.):
- Coverage on New Code >= 80%
- Maintainability Rating = A
- Security Hotspots Reviewed = 100%
Attach gate to your project (Administration → Quality Gate).

### 9. Troubleshooting
| Issue | Fix |
|-------|-----|
| `project not found` | Project key mismatch; update sonar-project.properties |
| `Unauthorized` | Wrong token / not passed to scanner |
| Quality gate step hangs | Webhook not configured or Jenkins unreachable |
| No coverage | Ensure test stage produced coverage.xml before scan |

---
### 10. SonarCloud PR Decoration
Enable under Project Settings → General Settings → Pull Request Decoration (install SonarCloud GitHub App). Adds inline issues & quality gate status on PRs.

---
This document supports achieving a high quality gate maturity and satisfying pipeline Code Quality criteria.