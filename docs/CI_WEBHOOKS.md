# CI Webhooks & Automation Guide

This document explains how to wire external events so the pipeline and quality gates run automatically on each change.

## 1. GitHub -> Jenkins (Build Trigger)
Use either a GitHub App (preferred for multibranch) or classic repository webhook.

### Option A: GitHub App (Multibranch)
1. Jenkins: Manage Jenkins -> System -> GitHub -> Add GitHub Server -> Create GitHub App.
2. Follow instructions; install the generated App on the repository/organization.
3. Create a *Multibranch Pipeline* job in Jenkins referencing the repo (uses the App credentials).
4. Jenkins automatically discovers branches & PRs; builds trigger on push / PR updates.

### Option B: Classic Webhook (Single Pipeline Job)
1. In Jenkins job configuration, check: "GitHub hook trigger for GITScm polling".
2. GitHub: Repo Settings -> Webhooks -> Add Webhook:
   - Payload URL: `https://<jenkins-host>/github-webhook/`
   - Content type: `application/json`
   - Secret: generate a random string (store in Jenkins if you want validation)
   - Events: *Just the push event* (optionally add *Pull requests*)
3. Test delivery; expect HTTP 200 in the response panel.

### Troubleshooting
| Symptom | Cause | Fix |
|---------|-------|-----|
| 404 on webhook | Missing trailing `/github-webhook/` | Correct URL path |
| No build triggered | Job not configured for hook | Enable trigger / verify credentials |
| Timeout | Jenkins not publicly reachable | Expose via reverse proxy or tunnel |

## 2. SonarCloud / SonarQube -> Jenkins (Quality Gate Webhook)
Speeds up `waitForQualityGate()` by pushing the analysis result instead of polling.

1. Sonar (Cloud or Server): Administration -> Configuration -> Webhooks -> Create:
   - Name: `jenkins-quality-gate`
   - URL: `https://<jenkins-host>/sonarqube-webhook/`
2. Save; no secret required for Jenkins plugin (you can add one only if you wrap and validate manually).
3. Run a build; observe Jenkins advancing past the Quality Gate stage promptly.

### Sample Delivery Payload (Structure)
See `sonar-webhook.example.json` in the repo for an example body. Jenkins plugin parses fields like `qualityGate.status`.

## 3. Environment Variables & Credentials
| Purpose | Name (suggested) | Location |
|---------|------------------|----------|
| Sonar token | `SONAR_TOKEN` | Jenkins Credentials (Secret Text) |
| PyPI publish (future) | `PYPI_TOKEN` | Jenkins Credentials |
| Docker registry | `DOCKER_PASSWORD` / `DOCKER_USERNAME` | Jenkins Credentials |

## 4. Pipeline Snippets
**Quality Gate:**
```groovy
stage('Quality Gate') {
  steps {
    timeout(time: 3, unit: 'MINUTES') {
      script {
        def qg = waitForQualityGate()
        if (qg.status != 'OK') {
          error "Quality Gate failed: ${qg.status}"
        }
      }
    }
  }
}
```

**Sonar Scanner (token via env):**
```groovy
withSonarQubeEnv('SonarLocal') {
  withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
    sh """
      sonar-scanner \
        -Dproject.settings=sonar-project.properties \
        -Dsonar.projectVersion=${BUILD_NUMBER}
    """
  }
}
```

## 5. Security Hardening Checklist
- Enforce HTTPS for Jenkins and restrict webhook ingress to GitHub/Sonar IP ranges if possible.
- Rotate tokens regularly; revoke unused tokens.
- Separate untrusted PR builds from release/publish stages (use conditions or branch filters).
- Consider adding a bot user with minimal scopes for automation rather than personal tokens.

## 6. Verification Steps
1. Push a commit -> Jenkins build auto-starts.
2. Build runs Sonar scan -> Sonar processes background task.
3. Sonar sends webhook -> Jenkins quality gate stage completes quickly.
4. Pipeline continues (or fails) based on gate status.

## 7. Future Enhancements
- Add GitHub PR decoration (SonarCloud) for inline issue & coverage diff.
- Add Slack / Teams notification on failed quality gate via Jenkins post action.
- Add dependency vulnerability gate (parse `pip-audit.json` severity >= HIGH).
- Introduce build status badge in README referencing Jenkins & Sonar metrics.

---
This guide complements `docs/SONARQUBE_SETUP.md` and the main README CI section.
