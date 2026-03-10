# Availity Payer List API 2.0.0 — Developer Reference
**Experiment 47 · PMS Integration · MPS Inc.**  
Source: Availity AWS Payer List Swagger Spec (payerList-document.json)  
Last Updated: March 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Base URLs & Endpoints Summary](#3-base-urls--endpoints-summary)
4. [GET /availity-payer-list — Query Payers](#4-get-availity-payer-list--query-payers)
5. [Response Model — Payer](#5-response-model--payer)
6. [Payer.processingRoutes Fields](#6-payerprocessingroutes-fields)
7. [Enum Reference Tables](#7-enum-reference-tables)
8. [HTTP Status Code Reference](#8-http-status-code-reference)
9. [Sample curl Calls](#9-sample-curl-calls)
10. [Sample Python Integration](#10-sample-python-integration)
11. [Key Differences from Other Availity APIs](#11-key-differences-from-other-availity-apis)
12. [PMS Integration Patterns](#12-pms-integration-patterns)

---

## 1. Overview

The **Availity AWS Payer List API 2.0.0** is the discovery layer for all other Availity HIPAA transaction APIs. It returns a catalog of payers available through Availity along with the specific transactions each payer supports, enrollment requirements, submission modes, and cost tiers.

**Primary use cases:**

- Populate payer dropdowns in PMS / EHR intake and scheduling screens
- Validate that a given payer supports a specific transaction (270, 278I, 276, etc.) before submitting
- Determine whether enrollment is required before submitting to a payer
- Filter payers by submission mode (`API`, `RealTime`) to identify Availity REST-compatible payers
- Detect mock/test payers (`100000001`, `100000002`) for sandbox testing
- Drive nightly payer list refresh to keep PMS payer tables current

**What this API does NOT do:**

- Submit any HIPAA transactions — use the Coverages, Claim Statuses, or Service Reviews APIs for that
- Return member-level or claim-level data
- Require async polling — all responses are synchronous

---

## 2. Authentication

**Scheme:** OAuth 2.0 Client Credentials (`application` flow)  
**Token URL:** `https://api.availity.com/v1/token`

### Required Scopes

| Scope | Plan |
|---|---|
| `aws-availity-payer-list` | Base access |
| `aws-availity-payer-list-standard` | Standard |

> Note: These scopes are **different** from the HIPAA transaction scopes used by Coverages, Claim Statuses, and Service Reviews. You need separate credentials or a token with both scope sets if combining this API with transaction APIs.

### Token Request

```bash
curl -X POST "https://api.availity.com/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials\
      &client_id=${AVAILITY_CLIENT_ID}\
      &client_secret=${AVAILITY_CLIENT_SECRET}\
      &scope=aws-availity-payer-list"
```

### Token Response

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

> Token TTL = **5 minutes**. The payer list changes infrequently — cache the full list response for hours or days, not just the token.

---

## 3. Base URLs & Endpoints Summary

| Environment | Base URL |
|---|---|
| Production | `https://api.availity.com/epdm-payer-list-aws/v1` |
| QUA / Sandbox | `https://qua.api.availity.com/epdm-payer-list-aws/v1` |

> Base path is **`/epdm-payer-list-aws/v1`** — entirely different from the `/v1` and `/v2` paths used by Coverages, Claim Statuses, and Service Reviews.

| Method | Path | Operation | Description |
|---|---|---|---|
| `GET` | `/availity-payer-list` | `getCustomPayerList` | Query available payers and their supported transactions |

This API has **one endpoint** and **one HTTP method**. All filtering is done via query parameters.

---

## 4. GET /availity-payer-list — Query Payers

**`GET https://api.availity.com/epdm-payer-list-aws/v1/availity-payer-list`**

- **Accept:** `application/json`
- **Auth:** Bearer token with `aws-availity-payer-list` scope
- **Response:** Synchronous array of `Payer` objects — no polling required

### Query Parameters

All parameters are optional. Omitting all parameters returns the full payer list.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `payerId` | string | No | Filter by a specific Availity payer ID (e.g., `"BCBSF"`, `"14545"`) |
| `transactionType` | array of string | No | Filter to payers supporting specific X12 transaction codes (see enum below). Repeatable: `?transactionType=270&transactionType=278I` |
| `submissionMode` | array of string | No | Filter by submission method: `Portal`, `Batch`, `RealTime`, `API`. Repeatable. |
| `availability` | string | No | `"available"` — payers not requiring an additional Availity contract; `"contract required"` — opposite |
| `enrollmentRequired` | boolean | No | `true` — only payers requiring enrollment; `false` — only payers that do not |

### transactionType Enum Values

| Code | X12 Transaction | Description |
|---|---|---|
| `270` | X12 270 | Eligibility and Benefits Inquiry |
| `276` | X12 276 | Claim Status Inquiry |
| `278I` | X12 278 | Health Care Services Inquiry (Prior Auth) |
| `835` | X12 835 | Claim Payment / Advice (ERA) |
| `837P` | X12 837P | Professional Claims |
| `837PEncounter` | X12 837P | Professional Encounters |
| `837PPredetermination` | X12 837P | Professional Pre-Determination |
| `837I` | X12 837I | Facility Claims (Institutional) |
| `837IEncounter` | X12 837I | Facility Encounter |
| `837IPredetermination` | X12 837I | Institutional Pre-Determination |
| `837D` | X12 837D | Dental Claims |
| `837DEncounter` | X12 837D | Dental Encounter |
| `837DPredetermination` | X12 837D | Dental Pre-Determination |
| `277RFAI` | X12 277 | Attachment Request |
| `275` | X12 275 | Unsolicited Attachment |
| `278N` | X12 278 | Notice of Admission |
| `ClaimStatusSummary` | Availity | Claim Status Summary (Value-Add) |
| `ClaimStatusDetail` | Availity | Claim Status Detail (Value-Add) |
| `ClaimStatusValueAdd` | Availity | Claim Status Plus Value Add |

### submissionMode Enum Values

| Value | Description |
|---|---|
| `Portal` | Submitted via Availity Essentials web portal |
| `Batch` | Submitted as batch EDI file |
| `RealTime` | Submitted in real time via EDI |
| `API` | Submitted via Availity REST API ← **use this to find API-compatible payers** |

### Response

Returns a JSON array of `Payer` objects. No envelope — the array is the response body.

```json
[
  { "payerId": "...", "name": "...", ... },
  { "payerId": "...", "name": "...", ... }
]
```

| HTTP Code | Description |
|---|---|
| `200` (default) | Success — array of `Payer` objects |

---

## 5. Response Model — Payer

Each element in the response array is a `Payer` object.

| Field | Type | Example | Description |
|---|---|---|---|
| `payerId` | string | `"14545"` | Unique Availity payer identifier — **use this as the `payerId` / `payer.id` in all transaction API calls** |
| `name` | string | `"FLORIDA BLUE (BCBS FLORIDA)"` | Common name identifying the health plan |
| `displayName` | string | `"FLORIDA BLUE"` | Name displayed in Availity Essentials UI |
| `shortName` | string | `"BCBS_OF_FL"` | Abbreviated name used in batch file naming conventions |
| `processingRoutes` | object | | Container for all transaction routes available for this payer (see Section 6) |

---

## 6. Payer.processingRoutes Fields

The `processingRoutes` object describes the transactions available for a payer and the terms under which they can be submitted.

| Field | Type | Example | Description |
|---|---|---|---|
| `transactionDescription` | string | `"Eligibility and Benefits Inquiry"` | Human-readable transaction type (see enum in Section 7) |
| `submissionMode` | string | `"API"` | How the transaction is submitted: `Portal`, `Batch`, `RealTime`, `API` |
| `enrollmentRequired` | boolean | `true` | Whether enrollment with Availity is required before submitting |
| `enrollmentMode` | string | `"Paperless"` | Type of enrollment process (see enum in Section 7) |
| `availability` | boolean | `true` | Whether this transaction is available under current contract (`true`) or requires additional Availity contract (`false`) |
| `gateway` | string | `"Gateway"` | Whether Availity is the gateway for this payer/route |
| `rebateTier` | string | `"Par"` | Cost tier for this route (see enum in Section 7) |
| `passThroughRate` | string | `"0"` | Pass-through rate for the route |
| `effectiveDate` | string | `"2011-09-18T01:48:45.000+0000"` | Date this transaction became available |
| `recentlyAdded` | string | `"2022-11-18T01:48:45.000+0000"` | Date this route was added |
| `newTierNotice` | string | `"New Tier Begins on 2022-12-01 - Comprehensive"` | Notice of upcoming tier/cost change, if applicable |
| `additionalInfo` | string | `"The 270 requires a GS02 value of LLX1210001..."` | Payer-specific notes about the transaction — **read this carefully before submitting** |

---

## 7. Enum Reference Tables

### transactionDescription (processingRoutes)

| Value | X12 Code | PMS Use |
|---|---|---|
| `Eligibility and Benefits Inquiry` | 270/271 | Pre-service eligibility check → Coverages API |
| `Claim Status Inquiry` | 276/277 | AR follow-up → Claim Statuses API |
| `Health Care Services Inquiry` | 278I | Prior authorization → Service Reviews API |
| `Claim Payment/Advice` | 835 | ERA / remittance |
| `Professional Claims` | 837P | Claim submission |
| `Professional Encounters` | 837P | Encounter submission (capitation) |
| `Professional Pre-Determination` | 837P | Pre-determination (non-binding auth estimate) |
| `Facility Claims` | 837I | Institutional claim submission |
| `Facility Encounter` | 837I | Institutional encounter |
| `Institutional Pre-Determination` | 837I | Institutional pre-determination |
| `Dental Claims` | 837D | Dental claim submission |
| `Dental Encounter` | 837D | Dental encounter |
| `Dental Pre-Determination` | 837D | Dental pre-determination |
| `Attachment` | 277RFAI | Request for additional information / attachment |
| `Unsolicited Attachment` | 275 | Proactively submitted clinical attachments |
| `Notice of Admission` | 278N | Inpatient admission notification |
| `Claim Status Summary` | — | Availity value-add claim status summary |
| `Claim Status Detail` | — | Availity value-add claim status detail |
| `Claim Status Plus Value Add` | — | Availity value-add combined claim status |

### enrollmentMode

| Value | Description |
|---|---|
| `Paperless` | Fully electronic — no paper required |
| `Auto Complete` | Enrollment completed automatically on first submission |
| `Payer Portal Enrollment` | Provider must enroll via payer's own portal |
| `Paper` | Physical paperwork must be submitted to payer |
| `Manual Payer Submission` | Availity submits enrollment manually on provider's behalf |
| `Email Attachment` | Enrollment form submitted via email attachment |

### rebateTier

| Value | Description |
|---|---|
| `Base` | Base tier — lowest cost |
| `Standard` | Standard tier |
| `Comprehensive` | Comprehensive tier — broadest access |
| `Par` | Participating provider rate |
| `NonPar` | Non-participating provider rate |
| `NonParPlus` | Non-participating plus |
| `Transitional` | Transitional pricing tier |
| `Other` | Other pricing arrangement |

---

## 8. HTTP Status Code Reference

| Code | Meaning | Action |
|---|---|---|
| `200` | Success — payer array returned | Process result |
| `401` | Unauthorized | Refresh token; check scope (`aws-availity-payer-list`) |
| `403` | Forbidden | Insufficient contract or scope |
| `500` | Internal Server Error | Retry with backoff |

---

## 9. Sample curl Calls

### 9.1 Get Token (Payer List Scope)

```bash
TOKEN=$(curl -s -X POST "https://api.availity.com/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials\
      &client_id=${AVAILITY_CLIENT_ID}\
      &client_secret=${AVAILITY_CLIENT_SECRET}\
      &scope=aws-availity-payer-list" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

---

### 9.2 Get Full Payer List (No Filters)

```bash
curl -X GET \
  "https://api.availity.com/epdm-payer-list-aws/v1/availity-payer-list" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 9.3 Look Up a Single Payer by ID

```bash
curl -X GET \
  "https://api.availity.com/epdm-payer-list-aws/v1/availity-payer-list?payerId=BCBSF" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 9.4 Find All Payers Supporting Eligibility (270) via API Submission Mode

```bash
curl -X GET \
  "https://api.availity.com/epdm-payer-list-aws/v1/availity-payer-list\
?transactionType=270\
&submissionMode=API" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 9.5 Find All Payers Supporting Prior Auth (278I) via API — Available Without Additional Contract

```bash
curl -X GET \
  "https://api.availity.com/epdm-payer-list-aws/v1/availity-payer-list\
?transactionType=278I\
&submissionMode=API\
&availability=available" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 9.6 Find Payers Supporting Both Eligibility AND Claim Status via API

```bash
# Note: transactionType is a repeatable array parameter
curl -X GET \
  "https://api.availity.com/epdm-payer-list-aws/v1/availity-payer-list\
?transactionType=270\
&transactionType=276\
&submissionMode=API" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 9.7 Find Payers That Do NOT Require Enrollment

```bash
curl -X GET \
  "https://api.availity.com/epdm-payer-list-aws/v1/availity-payer-list\
?transactionType=270\
&enrollmentRequired=false" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 9.8 Get Demo / Mock Payers (Sandbox Testing)

```bash
# Mock payer IDs are 100000001 and 100000002
curl -X GET \
  "https://api.availity.com/epdm-payer-list-aws/v1/availity-payer-list\
?payerId=100000001" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

## 10. Sample Python Integration

### 10.1 Payer List Client

```python
# app/services/availity_payer_list.py
import asyncio
import httpx
from typing import Optional


class AvailityPayerListClient:

    BASE_PATH = "/epdm-payer-list-aws/v1/availity-payer-list"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.availity.com",
        scope: str = "aws-availity-payer-list",
    ):
        self.client_id     = client_id
        self.client_secret = client_secret
        self.base_url      = base_url
        self.scope         = scope

    async def get_token(self) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v1/token",
                data={
                    "grant_type":    "client_credentials",
                    "client_id":     self.client_id,
                    "client_secret": self.client_secret,
                    "scope":         self.scope,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            return resp.json()["access_token"]

    # ──────────────────────────────────────────────────────────────
    # GET /availity-payer-list
    # ──────────────────────────────────────────────────────────────
    async def get_payers(
        self,
        payer_id: Optional[str]          = None,
        transaction_types: Optional[list[str]] = None,
        submission_modes: Optional[list[str]]  = None,
        availability: Optional[str]      = None,   # "available" | "contract required"
        enrollment_required: Optional[bool] = None,
    ) -> list[dict]:
        """
        Query the Availity payer list with optional filters.
        Returns a list of Payer objects.
        """
        token = await self.get_token()

        # Build params — httpx handles repeated keys for array params
        params = {}
        if payer_id:
            params["payerId"] = payer_id
        if transaction_types:
            params["transactionType"] = transaction_types
        if submission_modes:
            params["submissionMode"] = submission_modes
        if availability:
            params["availability"] = availability
        if enrollment_required is not None:
            params["enrollmentRequired"] = str(enrollment_required).lower()

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}{self.BASE_PATH}",
                params=params,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept":        "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    # ──────────────────────────────────────────────────────────────
    # Convenience methods
    # ──────────────────────────────────────────────────────────────

    async def get_all_payers(self) -> list[dict]:
        """Return full payer list — cache this result."""
        return await self.get_payers()

    async def get_payer_by_id(self, payer_id: str) -> Optional[dict]:
        """Look up a single payer by Availity payer ID."""
        results = await self.get_payers(payer_id=payer_id)
        return results[0] if results else None

    async def get_api_payers(
        self,
        transaction_type: str = "270",
    ) -> list[dict]:
        """Return payers supporting a transaction via REST API submission."""
        return await self.get_payers(
            transaction_types=[transaction_type],
            submission_modes=["API"],
        )

    async def get_payers_no_enrollment(
        self,
        transaction_type: str = "270",
    ) -> list[dict]:
        """Return payers for a transaction that do not require enrollment."""
        return await self.get_payers(
            transaction_types=[transaction_type],
            enrollment_required=False,
        )
```

### 10.2 Payer List Utilities

```python
# app/services/payer_list_utils.py

TRANSACTION_MAP = {
    "270":                "Eligibility and Benefits Inquiry",
    "276":                "Claim Status Inquiry",
    "278I":               "Health Care Services Inquiry",
    "835":                "Claim Payment/Advice",
    "837P":               "Professional Claims",
    "837I":               "Facility Claims",
    "837D":               "Dental Claims",
    "ClaimStatusSummary": "Claim Status Summary",
    "ClaimStatusDetail":  "Claim Status Detail",
    "ClaimStatusValueAdd":"Claim Status Plus Value Add",
}


def get_routes_for_transaction(
    payer: dict,
    transaction_description: str,
) -> list[dict]:
    """
    Extract all processingRoutes entries matching a given transaction description.
    processingRoutes may be a single object or a list depending on payer.
    """
    routes = payer.get("processingRoutes", {})

    # Normalize to list
    if isinstance(routes, dict):
        routes = [routes]
    elif not isinstance(routes, list):
        routes = []

    return [
        r for r in routes
        if r.get("transactionDescription") == transaction_description
    ]


def supports_api_transaction(payer: dict, transaction_description: str) -> bool:
    """True if payer supports the given transaction via API submission mode."""
    routes = get_routes_for_transaction(payer, transaction_description)
    return any(r.get("submissionMode") == "API" for r in routes)


def requires_enrollment(payer: dict, transaction_description: str) -> bool:
    """True if any route for this transaction requires enrollment."""
    routes = get_routes_for_transaction(payer, transaction_description)
    return any(r.get("enrollmentRequired") for r in routes)


def get_additional_info(payer: dict, transaction_description: str) -> list[str]:
    """
    Return payer-specific notes for a transaction.
    Always read additionalInfo before submitting — may contain required GS02 values.
    """
    routes = get_routes_for_transaction(payer, transaction_description)
    return [
        r["additionalInfo"]
        for r in routes
        if r.get("additionalInfo")
    ]


def build_pms_payer_record(payer: dict) -> dict:
    """
    Build a flat dict suitable for inserting into a PMS payer table.
    Checks API support for the three core Exp 47 transactions.
    """
    return {
        "payerId":       payer.get("payerId"),
        "name":          payer.get("name"),
        "displayName":   payer.get("displayName"),
        "shortName":     payer.get("shortName"),
        # ── API transaction support flags ─────────────────────
        "supportsEligibilityApi":  supports_api_transaction(
            payer, "Eligibility and Benefits Inquiry"
        ),
        "supportsClaimStatusApi":  supports_api_transaction(
            payer, "Claim Status Inquiry"
        ),
        "supportsPriorAuthApi":    supports_api_transaction(
            payer, "Health Care Services Inquiry"
        ),
        # ── Enrollment requirements ───────────────────────────
        "eligibilityEnrollmentRequired": requires_enrollment(
            payer, "Eligibility and Benefits Inquiry"
        ),
        "claimStatusEnrollmentRequired": requires_enrollment(
            payer, "Claim Status Inquiry"
        ),
        "priorAuthEnrollmentRequired":   requires_enrollment(
            payer, "Health Care Services Inquiry"
        ),
        # ── Payer-specific notes ──────────────────────────────
        "eligibilityNotes": get_additional_info(
            payer, "Eligibility and Benefits Inquiry"
        ),
        "claimStatusNotes": get_additional_info(
            payer, "Claim Status Inquiry"
        ),
        "priorAuthNotes":   get_additional_info(
            payer, "Health Care Services Inquiry"
        ),
    }


def filter_api_eligible_payers(
    payers: list[dict],
    required_transactions: list[str] = None,
) -> list[dict]:
    """
    Filter payer list to only those supporting all required transactions via API.

    Args:
        payers: Full payer list from get_all_payers()
        required_transactions: List of transactionDescription values to require.
                               Defaults to the three core Exp 47 transactions.
    """
    if required_transactions is None:
        required_transactions = [
            "Eligibility and Benefits Inquiry",
            "Claim Status Inquiry",
            "Health Care Services Inquiry",
        ]

    return [
        p for p in payers
        if all(supports_api_transaction(p, tx) for tx in required_transactions)
    ]
```

### 10.3 Nightly Payer List Refresh

```python
# app/tasks/payer_list_refresh.py
import asyncio
import os
from datetime import datetime, timezone

client = AvailityPayerListClient(
    client_id     = os.environ["AVAILITY_CLIENT_ID"],
    client_secret = os.environ["AVAILITY_CLIENT_SECRET"],
)


async def refresh_payer_table():
    """
    Nightly job: pull full payer list from Availity and upsert into PMS payer table.
    Flags payers supporting the three core Exp 47 API transactions.
    """
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting payer list refresh...")

    # 1. Fetch full list
    payers = await client.get_all_payers()
    print(f"  Fetched {len(payers)} payers from Availity")

    # 2. Build PMS records
    records = [build_pms_payer_record(p) for p in payers]

    # 3. Stats
    api_270  = sum(1 for r in records if r["supportsEligibilityApi"])
    api_276  = sum(1 for r in records if r["supportsClaimStatusApi"])
    api_278  = sum(1 for r in records if r["supportsPriorAuthApi"])
    api_all  = sum(1 for r in records if all([
        r["supportsEligibilityApi"],
        r["supportsClaimStatusApi"],
        r["supportsPriorAuthApi"],
    ]))

    print(f"  Payers with 270 API: {api_270}")
    print(f"  Payers with 276 API: {api_276}")
    print(f"  Payers with 278I API: {api_278}")
    print(f"  Payers with all three APIs: {api_all}")

    # 4. Upsert into PMS
    for record in records:
        await pms.upsert_payer(record)

    print(f"  Upserted {len(records)} records into PMS payer table")


async def validate_payer_before_submit(
    payer_id: str,
    transaction: str,  # "270", "278I", "276"
) -> dict:
    """
    Called before submitting a transaction — validates payer supports it via API,
    checks enrollment status, and surfaces any payer-specific notes.
    """
    DESCRIPTION_MAP = {
        "270":  "Eligibility and Benefits Inquiry",
        "276":  "Claim Status Inquiry",
        "278I": "Health Care Services Inquiry",
    }

    tx_desc = DESCRIPTION_MAP.get(transaction)
    if not tx_desc:
        raise ValueError(f"Unknown transaction type: {transaction}")

    payer = await client.get_payer_by_id(payer_id)
    if not payer:
        return {
            "valid":   False,
            "reason":  f"Payer {payer_id} not found in Availity payer list",
        }

    api_supported  = supports_api_transaction(payer, tx_desc)
    enrollment_req = requires_enrollment(payer, tx_desc)
    notes          = get_additional_info(payer, tx_desc)

    return {
        "valid":              api_supported,
        "payerId":            payer.get("payerId"),
        "payerName":          payer.get("name"),
        "transaction":        transaction,
        "apiSupported":       api_supported,
        "enrollmentRequired": enrollment_req,
        "additionalInfo":     notes,
        "reason":             None if api_supported else (
            f"Payer {payer_id} does not support {transaction} via API submission"
        ),
    }
```

### 10.4 Usage Example

```python
import asyncio
import os

client = AvailityPayerListClient(
    client_id     = os.environ["AVAILITY_CLIENT_ID"],
    client_secret = os.environ["AVAILITY_CLIENT_SECRET"],
)

async def main():

    # ── Look up a specific payer ──────────────────────────────────
    payer = await client.get_payer_by_id("BCBSF")
    if payer:
        record = build_pms_payer_record(payer)
        print(f"Payer: {record['name']}")
        print(f"  270 API: {record['supportsEligibilityApi']}")
        print(f"  276 API: {record['supportsClaimStatusApi']}")
        print(f"  278I API: {record['supportsPriorAuthApi']}")
        print(f"  Notes: {record['eligibilityNotes']}")

    # ── Validate before submitting ────────────────────────────────
    validation = await validate_payer_before_submit("BCBSF", "270")
    if not validation["valid"]:
        print(f"BLOCKED: {validation['reason']}")
        return

    if validation["enrollmentRequired"]:
        print("WARNING: Enrollment required before submitting to this payer")

    for note in validation["additionalInfo"]:
        print(f"PAYER NOTE: {note}")

    # ── Find all API-capable payers for all three core transactions ─
    all_payers = await client.get_all_payers()
    api_payers = filter_api_eligible_payers(all_payers)
    print(f"\nPayers supporting 270 + 276 + 278I via API: {len(api_payers)}")
    for p in api_payers[:5]:
        print(f"  {p['payerId']:15} {p['name']}")

asyncio.run(main())
```

---

## 11. Key Differences from Other Availity APIs

| Aspect | Coverages / Claim Statuses / Service Reviews | Payer List API |
|---|---|---|
| **Purpose** | Submit HIPAA transactions | Discover what transactions payers support |
| **X12 Transaction** | 270, 276, 278 | None — metadata only |
| **Base path** | `/v1` or `/v2` | **`/epdm-payer-list-aws/v1`** |
| **OAuth scope** | `healthcare-hipaa-transactions` | **`aws-availity-payer-list`** |
| **HTTP methods** | GET, POST, PUT, DELETE | **GET only** |
| **Async / polling** | Yes — 202 → poll | **No — synchronous response** |
| **Response format** | Single object or ResultSet | **Direct JSON array (no envelope)** |
| **Rate limit strategy** | Per-transaction | **Cache aggressively — list rarely changes** |
| **Produces** | `application/json` | `application.json` *(typo in spec — treat as `application/json`)* |
| **Sandbox payer IDs** | `100000001`, `100000002` | Same IDs appear in payer list |

---

## 12. PMS Integration Patterns

### Pattern 1 — Payer Dropdown Population

```python
async def get_payer_dropdown_options(transaction: str = "270") -> list[dict]:
    """
    Returns a sorted list of {payerId, displayName} for populating UI dropdowns.
    Filters to payers supporting the given transaction via API.
    """
    payers = await client.get_payers(
        transaction_types=[transaction],
        submission_modes=["API"],
        availability="available",
    )
    return sorted(
        [{"payerId": p["payerId"], "label": p["displayName"]} for p in payers],
        key=lambda x: x["label"],
    )
```

### Pattern 2 — Pre-Submission Payer Validation Gate

```python
async def pre_submission_gate(payer_id: str, transaction: str) -> None:
    """
    Raises ValueError with a clear message if payer does not support
    the requested transaction via Availity API.
    Call this before invoking Coverages, Claim Statuses, or Service Reviews.
    """
    validation = await validate_payer_before_submit(payer_id, transaction)

    if not validation["valid"]:
        raise ValueError(
            f"Cannot submit {transaction} for payer {payer_id}: "
            f"{validation['reason']}"
        )

    if validation["enrollmentRequired"]:
        enrolled = await pms.check_enrollment_status(payer_id, transaction)
        if not enrolled:
            raise ValueError(
                f"Enrollment required for {transaction} with {payer_id} "
                f"but no enrollment on file. Complete enrollment before submitting."
            )

    # Log any payer-specific notes for audit trail
    for note in validation["additionalInfo"]:
        await pms.log_payer_note(payer_id, transaction, note)
```

### Pattern 3 — Nightly Payer List Cache Refresh (Cron)

```python
# Schedule this nightly — payer list changes slowly but does change
# Recommended: run at 2:00 AM local time, cache results in DB

import asyncio
from datetime import datetime, timezone

async def nightly_payer_refresh_job():
    try:
        await refresh_payer_table()
        await pms.set_setting(
            "payer_list_last_refreshed",
            datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        await pms.alert_ops(f"Payer list refresh failed: {e}")
        raise
```

### Pattern 4 — Detect Payer-Specific Submission Requirements

```python
async def get_payer_submission_notes(payer_id: str) -> dict:
    """
    Surfaces payer-specific GS02 values, enrollment modes, and
    other submission requirements before the first API call.
    Critical: some payers require specific GS02 segment values in EDI.
    """
    payer = await client.get_payer_by_id(payer_id)
    if not payer:
        return {}

    result = {}
    for tx_code, tx_desc in {
        "270":  "Eligibility and Benefits Inquiry",
        "276":  "Claim Status Inquiry",
        "278I": "Health Care Services Inquiry",
    }.items():
        notes = get_additional_info(payer, tx_desc)
        enrollment_mode = None

        routes = get_routes_for_transaction(payer, tx_desc)
        if routes:
            enrollment_mode = routes[0].get("enrollmentMode")

        result[tx_code] = {
            "notes":          notes,
            "enrollmentMode": enrollment_mode,
        }

    return result
```

---

*Source: Availity AWS Payer List 2.0.0 Swagger Specification (payerList-document.json) · Swagger 2.0 · Host: api.availity.com · BasePath: /epdm-payer-list-aws/v1*
