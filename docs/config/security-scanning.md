# Security Scanning Configuration

This document describes the three security scanning tools integrated across all PMS repositories: SonarCloud, CodeRabbit, and Snyk.

## SonarCloud

**Purpose:** Static code analysis, code coverage tracking, and quality gate enforcement.

### Organization & Projects

| Project Key | Repository |
|---|---|
| `ammar-utexas_pms-backend` | pms-backend |
| `ammar-utexas_pms-frontend` | pms-frontend |
| `ammar-utexas_pms-android` | pms-android |

**Organization:** `ammar-utexas`

### Configuration Files

Each repo contains:
- `sonar-project.properties` — project key, source/test paths, coverage report paths
- `.github/workflows/sonarqube.yml` — CI workflow that runs tests, generates coverage, and invokes SonarCloud

### Quality Gates

The default SonarCloud quality gate applies:
- No new bugs
- No new vulnerabilities
- No new security hotspots reviewed as unsafe
- Code coverage on new code >= 80%
- Duplicated lines on new code < 3%

The quality gate step uses `continue-on-error: true` until thresholds are tuned for the project.

### Required Secret

| Secret | Where | Source |
|---|---|---|
| `SONAR_TOKEN` | GitHub org or per-repo secrets | SonarCloud > My Account > Security > Generate Token |

### Setup Steps

1. Log in to [sonarcloud.io](https://sonarcloud.io) with your GitHub account
2. Create the organization `ammar-utexas` (or import from GitHub)
3. Create 3 projects matching the `sonar.projectKey` values above
4. Generate a token and add it as `SONAR_TOKEN` in GitHub secrets
5. Push the workflow files — scans will run automatically on the next PR

---

## CodeRabbit

**Purpose:** AI-powered code review on pull requests, configured with HIPAA-aware review instructions.

### Configuration

Each repo contains a `.coderabbit.yaml` file with:
- **Path-specific instructions** referencing requirement IDs (SYS-REQ-0002, SYS-REQ-0003, SYS-REQ-0005)
- **Path filters** to skip generated/vendor files
- **Profile:** `chill` (suggestions, not blocking)

### HIPAA Review Rules

CodeRabbit is instructed to verify:
- **SYS-REQ-0002:** Encryption on PHI fields (models, data layer)
- **SYS-REQ-0003:** Audit logging on patient data access (routers, services)
- **SYS-REQ-0005:** RBAC checks precede data access (routers, UI)

### Setup Steps

1. Install the CodeRabbit GitHub App from [github.com/marketplace/coderabbit](https://github.com/marketplace/coderabbit)
2. Grant access to the `ammar-utexas` organization repositories
3. No secrets required — CodeRabbit reads `.coderabbit.yaml` from each repo automatically

---

## Snyk

**Purpose:** Dependency vulnerability scanning, static application security testing (SAST), and container image scanning.

### Scan Types Per Repo

| Repo | Dependencies | SAST (Code) | Container |
|---|---|---|---|
| pms-backend | `snyk/actions/python-3.12` | `snyk/actions/python-3.12` (code test) | `snyk/actions/docker` |
| pms-frontend | `snyk/actions/node` | `snyk/actions/node` (code test) | `snyk/actions/docker` |
| pms-android | `snyk/actions/gradle-jdk17` | `snyk/actions/node` (code test) | N/A |

### Configuration

Each repo contains `.github/workflows/snyk-security.yml` with:
- Separate jobs for each scan type
- `--severity-threshold=medium` to filter low-severity findings
- SARIF output uploaded to GitHub Code Scanning via `github/codeql-action/upload-sarif@v3`
- `continue-on-error: true` so scans report findings without blocking CI

### Evidence Storage

- **GitHub Code Scanning:** SARIF results appear in the repo's Security tab > Code scanning alerts
- **Snyk Dashboard:** Full scan history at [app.snyk.io](https://app.snyk.io)
- **Retention:** GitHub Code Scanning retains alerts until dismissed; Snyk retains per plan limits

### Required Secret

| Secret | Where | Source |
|---|---|---|
| `SNYK_TOKEN` | GitHub org or per-repo secrets | Snyk > Account Settings > Auth Token |

### Setup Steps

1. Create a Snyk account at [app.snyk.io](https://app.snyk.io)
2. Copy your auth token from Account Settings
3. Add it as `SNYK_TOKEN` in GitHub secrets (org level recommended)
4. Push the workflow files — scans will run automatically on the next PR

---

## Verification

After merging the configuration files and setting up secrets:

1. **SonarCloud:** Open a PR — the `SonarCloud Analysis` check should appear in PR checks
2. **CodeRabbit:** Open a PR — CodeRabbit should post a review comment automatically
3. **Snyk:** Open a PR — the `Snyk Security Scan` check should appear; findings appear in GitHub Security tab

All three tools use `continue-on-error: true` initially. Once baselines are established, remove this flag to enforce quality gates.
