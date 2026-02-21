# Release Process

**Related ADR:** [ADR-0006: Release Management Strategy](../architecture/0006-release-management-strategy.md)

---

## Release Cadence

- **Sprint length:** 2 weeks
- **Release candidate (RC):** Cut at end of each sprint
- **Production release:** After RC passes QA and Staging gates

## Release Workflow

### 1. Feature Development (Dev Environment)

1. Developer creates feature branch from `main`
2. New code guarded behind feature flag (default: `false`)
3. PR opened, CI runs lint + test + security scan
4. PR merged to `main` → auto-deploys to Dev
5. Feature flag enabled in Dev for manual verification

### 2. Release Candidate (QA Environment)

1. At sprint end, create RC tags across repos involved in the release:
   ```bash
   git tag v0.2.0-rc.1
   git push origin v0.2.0-rc.1
   ```
2. Deploy RC to QA environment (manual trigger)
3. Enable relevant feature flags in QA
4. QA team runs regression test suite
5. If issues found: fix → tag `v0.2.0-rc.2` → repeat

### 3. Staging Validation

1. **Gate:** QA team signs off on RC
2. Deploy RC to Staging (uses sanitized production data)
3. Enable feature flags matching production rollout plan
4. Product owner validates user-facing behavior
5. Run system-level integration tests (TST-SYS-*)
6. Update [Release Compatibility Matrix](../specs/release-compatibility-matrix.md)

### 4. Production Release

1. **Gate:** Change control board approves release
2. Create release tag (remove `-rc` suffix):
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
3. Deploy to Production
4. Enable feature flags per rollout plan (gradual or all-at-once)
5. Monitor for 24 hours
6. Update CHANGELOG.md with final release notes

## Approval Gates Summary

| Transition | Gate | Who Approves |
|---|---|---|
| Dev → QA | CI passes (lint, test, security) | Automated |
| QA → Staging | QA team sign-off | QA Lead |
| Staging → Prod | Change control board | Product Owner + Tech Lead |

## Rollback Strategy

In order of preference:

1. **Toggle feature flag off** (preferred)
   - Zero downtime, instant effect
   - Use when the issue is isolated to flagged code

2. **Redeploy previous tag**
   - Roll back to last known-good version
   - Use when the issue is in unflagged code or infrastructure

3. **Hotfix forward**
   - Create hotfix branch from release tag, fix, tag as patch release
   - Use when rollback isn't feasible (e.g., database migration already applied)

## Release Checklist Template

```markdown
## Release: v{VERSION} — {DATE}

### Pre-Release
- [ ] All PRs for this release merged to main
- [ ] CHANGELOG.md updated with all changes
- [ ] RC tag created and pushed
- [ ] QA regression suite passed
- [ ] Staging validation completed
- [ ] Compatibility matrix updated
- [ ] Change control board approved

### Deployment
- [ ] Production tag created and pushed
- [ ] Deployment completed successfully
- [ ] Health checks passing
- [ ] Feature flags enabled per rollout plan

### Post-Release
- [ ] 24-hour monitoring window completed
- [ ] No critical issues reported
- [ ] CHANGELOG.md finalized
- [ ] Subsystem versions updated if applicable
- [ ] Notify stakeholders of release
```

## Hotfix Process

1. Branch from the release tag: `git checkout -b hotfix/v0.2.1 v0.2.0`
2. Apply fix and add tests
3. Tag as patch: `git tag v0.2.1`
4. Deploy through expedited pipeline (Dev → Staging → Prod, skip QA if critical)
5. Cherry-pick fix back to `main`
6. Update CHANGELOG.md
