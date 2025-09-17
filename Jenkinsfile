pipeline {
    agent any

    options {
        ansiColor('xterm')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timeout(time: 15, unit: 'MINUTES')
    }

    environment {
        PYTHON = 'python3'
        VENV_DIR = '.venv'
        COVERAGE_FILE = 'coverage.xml'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh "${PYTHON} -m venv ${VENV_DIR}"
                sh "${VENV_DIR}/bin/pip install --upgrade pip"
                sh "${VENV_DIR}/bin/pip install -r requirements.txt"
                // Dev / quality / security tools
                sh "${VENV_DIR}/bin/pip install pytest-cov flake8 coverage bandit pip-audit sonar-scanner --extra-index-url https://pypi.org/simple"
            }
        }

        stage('Lint') {
            when { expression { return fileExists('aeb') } }
            steps {
                sh "${VENV_DIR}/bin/flake8 aeb || true" // non-fatal initially
            }
        }

        stage('Tests') {
            steps {
                sh "${VENV_DIR}/bin/pytest -q --cov=aeb --cov-report=xml:${COVERAGE_FILE} --cov-report=term --junitxml=junit-results.xml" 
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'junit-results.xml'
                    publishCoverage adapters: [cobertura(coberturaReportFile: COVERAGE_FILE, failNoReports: false)], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }

        stage('Code Quality') {
            steps {
                script {
                    // Attempt SonarQube scan; if server not configured, continue non-fatally
                    try {
                        withSonarQubeEnv('SonarLocal') { // configure this name in Jenkins global settings
                            withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
                                sh "${VENV_DIR}/bin/sonar-scanner -Dproject.settings=sonar-project.properties -Dsonar.login=${SONAR_TOKEN}" 
                            }
                        }
                    } catch (err) {
                        echo "Sonar scan skipped: ${err.getMessage()}"
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                script {
                    // Wait for webhook callback if scan occurred; timeout to avoid indefinite hang
                    try {
                        timeout(time: 5, unit: 'MINUTES') {
                            waitForQualityGate abortPipeline: false
                        }
                    } catch (err) {
                        echo "Quality gate check skipped or failed: ${err.getMessage()}"
                    }
                }
            }
        }

        stage('Security') {
            steps {
                sh "${VENV_DIR}/bin/pip-audit -r requirements.txt -f json > pip-audit.json || true"
                sh "${VENV_DIR}/bin/bandit -q -r aeb -f json -o bandit.json || true"
            }
            post {
                always {
                    archiveArtifacts artifacts: 'pip-audit.json,bandit.json', allowEmptyArchive: true
                    script {
                        def audit = fileExists('pip-audit.json') ? readJSON file: 'pip-audit.json' : null
                        if (audit && audit.dependencies) {
                            echo "Security scan (pip-audit) found vulnerabilities: ${audit.dependencies.size()} dependencies scanned"
                        }
                    }
                }
            }
        }

        stage('Build Artifact') {
            steps {
                sh "${VENV_DIR}/bin/pip install build"
                sh "${VENV_DIR}/bin/python -m build --wheel --outdir dist/"
            }
            post {
                success { archiveArtifacts artifacts: 'dist/*.whl', fingerprint: true }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("aeb-safety-decision-engine:${env.BUILD_NUMBER}")
                }
            }
        }

        stage('Deploy (Test Env)') {
            steps {
                script {
                    sh 'docker rm -f aeb_test || true'
                    sh 'docker run -d --name aeb_test -p 8000:8000 aeb-safety-decision-engine:${BUILD_NUMBER}'
                    sleep 3
                    sh 'curl -sSf http://localhost:8000/health'
                }
            }
        }

        stage('Monitoring (Smoke)') {
            steps {
                sh 'curl -sSf http://localhost:8000/sample-decision > sample_decision.json'
                archiveArtifacts artifacts: 'sample_decision.json', allowEmptyArchive: true
            }
        }

        stage('Release') {
            when {
                allOf {
                    expression { return env.BRANCH_NAME == 'main' }
                    expression { return env.TAG_NAME != null || env.GIT_TAG_NAME != null || env.GIT_BRANCH == 'refs/heads/main' }
                }
            }
            steps {
                echo 'Simulated release: tagging artifact (no external publish configured).'
            }
        }

    }

    post {
        always { archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true }
        success {
            echo 'Build succeeded.'
        }
        failure {
            echo 'Build failed.'
        }
    }
}