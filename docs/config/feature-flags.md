# Feature Flag Registry

**Related ADR:** [ADR-0006: Release Management Strategy](../architecture/0006-release-management-strategy.md)

---

## Naming Convention

Flags are named after their requirement ID:

```
FEATURE_{SUBSYSTEM}_{REQUIREMENT_NUMBER}_{SHORT_DESCRIPTION}
```

Examples:
- `FEATURE_SUB_PR_0007_PATIENT_SEARCH`
- `FEATURE_SUB_MM_0005_FHIR_MEDICATION`
- `FEATURE_SYS_REQ_0004_FHIR_EXCHANGE`

## Flag Registry

| Flag Name | Req ID | Description | Lifecycle Stage | Dev | QA | Staging | Prod |
|---|---|---|---|---|---|---|---|
| `FEATURE_SUB_PR_0007_PATIENT_SEARCH` | SUB-PR-0007 | Patient search by last name, DOB, or ID | Create | off | off | off | off |
| `FEATURE_SUB_PR_0008_PAGINATION` | SUB-PR-0008 | Paginated patient list queries | Create | off | off | off | off |
| `FEATURE_SUB_CW_0005_CLINICAL_ALERTS` | SUB-CW-0005 | Clinical alerts for critical conditions in encounter notes | Create | off | off | off | off |
| `FEATURE_SUB_CW_0007_STATUS_VALIDATION` | SUB-CW-0007 | Encounter status transition validation | Create | off | off | off | off |
| `FEATURE_SUB_MM_0005_FHIR_MEDICATION` | SUB-MM-0005 | FHIR R4 MedicationRequest and MedicationDispense | Create | off | off | off | off |
| `FEATURE_SUB_MM_0009_REFILL_TRACKING` | SUB-MM-0009 | Track remaining refills, prevent zero-refill fills | Create | off | off | off | off |
| `FEATURE_SUB_RA_0003_AUDIT_LOG_QUERY` | SUB-RA-0003 | Audit log query interface with filters | Create | off | off | off | off |
| `FEATURE_SUB_RA_0007_CSV_EXPORT` | SUB-RA-0007 | Report export to CSV format | Create | off | off | off | off |
| `FEATURE_SYS_REQ_0004_FHIR_EXCHANGE` | SYS-REQ-0004 | HL7 FHIR R4 patient data exchange | Create | off | off | off | off |
| `FEATURE_SUB_PR_0009_WOUND_ASSESSMENT` | SUB-PR-0009 | AI wound/condition photo assessment via MONAI + TensorRT | Create | off | off | off | off |
| `FEATURE_SUB_PR_0010_PATIENT_ID_VERIFY` | SUB-PR-0010 | Patient identity verification via ArcFace + TensorRT | Create | off | off | off | off |
| `FEATURE_SUB_PR_0011_DOCUMENT_OCR` | SUB-PR-0011 | Document OCR text extraction via PaddleOCR + TensorRT | Create | off | off | off | off |

## Always-On Features (No Flag)

Some features are foundational security or infrastructure requirements that must never be disabled in any environment. These do **not** use feature flags.

| Feature | Req IDs | Reason | Dev Workaround |
|---|---|---|---|
| Authentication & User Management | SUB-AU-0001 – SUB-AU-0016 | Core security gate; disabling would expose PHI | Auth bypass mode (`NEXT_PUBLIC_AUTH_BYPASS_ENABLED`) — see [environments.md](environments.md) |

**Auth Bypass Mode (SUB-AU-0016):** The frontend provides a dev-only bypass that injects a mock user and shows a non-dismissible yellow warning banner. This is controlled by `NEXT_PUBLIC_AUTH_BYPASS_*` environment variables, **not** by the feature flag system. It must never be enabled outside local development.

## Flag Lifecycle

```
Create → Develop → Test-Dev → Test-QA → Test-Staging → Enable-Prod → Monitor → Remove
```

| Stage | Description | Who Acts |
|---|---|---|
| **Create** | Flag added to code and registry, defaults to `false` | Developer |
| **Develop** | Feature implemented behind flag | Developer |
| **Test-Dev** | Flag enabled in Dev, developer verifies | Developer |
| **Test-QA** | Flag enabled in QA, QA team runs tests | QA Team |
| **Test-Staging** | Flag enabled in Staging, product owner validates | Product Owner |
| **Enable-Prod** | Flag enabled in Production | Change Control Board |
| **Monitor** | Feature live, monitoring for issues (min. 2 sprints) | Operations |
| **Remove** | Flag removed from code, feature permanently on | Developer |

## Implementation

### Backend (Python)

```python
from pms.feature_flags import flags

if flags.is_enabled("FEATURE_SUB_PR_0007_PATIENT_SEARCH"):
    # new search endpoint logic
```

### Frontend (TypeScript)

```typescript
import { isFeatureEnabled } from '@/config/featureFlags';

if (isFeatureEnabled('FEATURE_SUB_PR_0007_PATIENT_SEARCH')) {
  // render search component
}
```

### Android (Kotlin)

```kotlin
import com.utexas.pms.config.FeatureFlags

if (FeatureFlags.isEnabled("FEATURE_SUB_PR_0007_PATIENT_SEARCH")) {
    // show search UI
}
```

## Rules

1. **Every not-yet-implemented requirement gets a flag** before development starts
2. **Flags default to `false`** — new code is never accidentally exposed
3. **Only the change control board** can approve enabling flags in Production
4. **Remove flags within 2 sprints** after stable Production release
5. **Update this registry** whenever a flag changes lifecycle stage
