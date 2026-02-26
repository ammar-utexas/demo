# Release Compatibility Matrix

**Related ADR:** [ADR-0006: Release Management Strategy](../architecture/0006-release-management-strategy.md)

---

## Purpose

This matrix records which combinations of repository versions have been tested together through system-level integration tests (TST-SYS-*). Only version combinations that appear here with status "Certified" should be deployed to Production.

## Certified Releases

| Release Name | Backend Version | Frontend Version | Android Version | AI Version | Subsystem Versions | System Test Run ID | Date | Status |
|---|---|---|---|---|---|---|---|---|
| v0.1.0-initial | 0.1.0 | 0.1.0 | 0.1.0 | — | SUB-PR-v0.0, SUB-CW-v0.0, SUB-MM-v0.0, SUB-RA-v0.0 | — | 2026-02-15 | Scaffold Only |

## How to Update

1. After deploying a version combination to Staging, run the full system test suite (TST-SYS-0001 through TST-SYS-0010)
2. Record the test run ID using the format from [Testing Strategy](../testing/testing-strategy.md): `RUN-YYYY-MM-DD-NNN`
3. Add a row to the table above with all version numbers and the test run ID
4. Set status to:
   - **Certified** — All system tests passed
   - **Partial** — Some tests passed, known issues documented
   - **Failed** — Critical test failures, do not deploy
   - **Scaffold Only** — No system tests run yet (initial scaffold)

## Version Lookup

To find the current version of each repo:

| Repository | Version Location |
|---|---|
| pms-backend | `pyproject.toml` → `version` |
| pms-frontend | `package.json` → `version` |
| pms-android | `app/build.gradle.kts` → `versionName` |
| pms-ai | `pyproject.toml` → `version` |
| Subsystems | [Subsystem Versions](subsystem-versions.md) |
