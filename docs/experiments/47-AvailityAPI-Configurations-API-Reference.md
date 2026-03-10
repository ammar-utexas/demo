# Availity Configurations API 1.0.0 — Developer Reference
**Experiment 47 · PMS Integration · MPS Inc.**  
Source: Availity Configurations Swagger Spec (configurationdocument.json)  
Last Updated: March 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Base URLs & Endpoints Summary](#3-base-urls--endpoints-summary)
4. [GET /configurations — Retrieve Configurations](#4-get-configurations--retrieve-configurations)
5. [Response Models](#5-response-models)
   - [ResultSet](#51-resultset)
   - [Configuration](#52-configuration)
   - [Element](#53-element)
   - [FieldCondition](#54-fieldcondition)
   - [ObjectType](#55-objecttype)
   - [ErrorResponse](#56-errorresponse)
6. [Element Type Reference](#6-element-type-reference)
7. [Conditional Logic Reference](#7-conditional-logic-reference)
8. [requiredFieldCombinations Logic](#8-requiredFieldcombinations-logic)
9. [HTTP Status Code Reference](#9-http-status-code-reference)
10. [Sample curl Calls](#10-sample-curl-calls)
11. [Sample Python Integration](#11-sample-python-integration)
12. [How Configurations Relate to the Other Exp 47 APIs](#12-how-configurations-relate-to-the-other-exp-47-apis)
13. [PMS Integration Patterns](#13-pms-integration-patterns)

---

## 1. Overview

The **Availity Configurations 1.0.0 API** returns payer-specific input form display and validation rules for HIPAA transactions. It answers the question: **"For this payer and this transaction type, which fields are required, allowed, conditionally required, and how must they be formatted?"**

This is the metadata layer that should be called **before** submitting to any of the three Exp 47 transaction APIs. Without it, you are guessing at payer-specific field requirements — leading to avoidable `400 Bad Request` rejections.

**What the Configurations API provides:**

- Which fields are `required`, `optional`, or `not allowed` for a given payer/transaction
- Conditional rules — a field may be required only *when* another field has a specific value
- `requiredFieldCombinations` — complex OR-group rules where at least one set of fields from a group must be populated
- Field-level validation: `minLength`, `maxLength`, `pattern` (regex), `min`/`max` dates
- UI rendering hints: `type` (Text, Enumeration, Date, Boolean, etc.), `label`, `order`, `hidden`, `mode` (DropDown vs RadioGroup)
- Allowed values lists and conditional value lists (`values`, `valuesWhen`)
- Nested field structures via `Object`, `ObjectArray`, and `Section` elements

**Typical call sequence in PMS:**

```
1. GET /epdm-payer-list-aws/v1/availity-payer-list   → confirm payer supports transaction
2. GET /v1/configurations?type=coverages&payerId=BCBSF → fetch field rules for that payer
3. Apply rules to validate PMS form data
4. POST /v1/coverages (or /v2/service-reviews, etc.)  → submit with confidence
```

---

## 2. Authentication

**Scheme:** OAuth 2.0 Client Credentials (`application` flow)  
**Token URL:** `https://api.availity.com/v1/token`

### Required Scopes

| Scope | Plan |
|---|---|
| `healthcare-hipaa-transactions` | Standard |
| `healthcare-hipaa-transactions-standard` | Standard (explicit) |
| `healthcare-hipaa-transactions-highvolume` | High Volume |
| `healthcare-hipaa-transactions-highvolume-standard` | High Volume Standard |
| `healthcare-hipaa-transactions-highvolume-unlimited` | Unlimited |
| `rcm-coverages` | RCM add-on |
| `rcm-coverages-standard` | RCM Standard |

> Same `healthcare-hipaa-transactions` scope family as Coverages, Claim Statuses, and Service Reviews. No separate scope needed.

### Token Request

```bash
curl -X POST "https://api.availity.com/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials\
      &client_id=${AVAILITY_CLIENT_ID}\
      &client_secret=${AVAILITY_CLIENT_SECRET}\
      &scope=healthcare-hipaa-transactions"
```

---

## 3. Base URLs & Endpoints Summary

| Environment | Base URL |
|---|---|
| Production | `https://api.availity.com/v1` |
| QUA / Sandbox | `https://qua.api.availity.com/v1` |

| Method | Path | Operation | Description |
|---|---|---|---|
| `GET` | `/configurations` | `findConfigurations` | Retrieve payer-specific field rules for a transaction type |

This API has **one endpoint** and **one HTTP method**. The response is synchronous — no polling required.

> **Note:** When multiple configurations match (e.g., no `payerId` filter), Availity may return **abbreviated versions**. Always include `payerId` to get the full payer-specific configuration.

---

## 4. GET /configurations — Retrieve Configurations

**`GET https://api.availity.com/v1/configurations`**

- **Accept:** `application/json` or `application/xml`
- **Auth:** Bearer token

### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `type` | string | ✅ **REQUIRED** | The configuration type — identifies which transaction/form the config applies to (e.g., `"coverages"`, `"service-reviews"`, `"claim-statuses"`) |
| `subtypeId` | string | No | Sub-type filter — further narrows the configuration (e.g., specific service type or transaction subtype) |
| `payerId` | string | No | Availity payer ID — **always include this** to get the full payer-specific configuration rather than a generic abbreviated version |

### Known `type` Values

| type | Associated Transaction API |
|---|---|
| `coverages` | Coverages API (270/271 eligibility) |
| `service-reviews` | Service Reviews API (278 prior auth) |
| `claim-statuses` | Claim Statuses API (276/277) |

> The full list of valid `type` values is not enumerated in the spec — query without `payerId` first to discover what types exist for your contract.

### Responses

| HTTP Code | Description | Schema |
|---|---|---|
| `200 OK` | Configurations found | `ResultSet` |
| `400 Bad Request` | Missing required `type` parameter or validation error | `ErrorResponse` |
| `401 Unauthorized` | Invalid or missing token | `ErrorResponse` |
| `403 Forbidden` | Insufficient scope | `ErrorResponse` |
| `500 Internal Server Error` | Server error | `ErrorResponse` |

---

## 5. Response Models

### 5.1 ResultSet

Top-level response wrapper.

| Field | Type | Description |
|---|---|---|
| `configurations[]` | array of `Configuration` | Matching configuration records |
| `count` | integer | Number of records in this page |
| `totalCount` | integer | Total matching records |
| `limit` | integer | Page size limit |
| `offset` | integer | Page offset |
| `links` | object | Pagination link URLs (`href`) |

---

### 5.2 Configuration

A single payer-specific form configuration. The core response object.

| Field | Type | Description |
|---|---|---|
| `payerId` | string | Availity payer ID this configuration applies to |
| `payerName` | string | Payer name |
| `type` | string | Configuration type (matches the `type` query param) |
| `subtypeId` | string | Configuration subtype ID |
| `subtypeValue` | string | Human-readable subtype value |
| `categoryId` | string | Configuration category ID |
| `categoryValue` | string | Human-readable category value |
| `sourceId` | string | Configuration source ID |
| `version` | string | Configuration version |
| `settings` | object | Key-value string pairs — payer-specific settings |
| `elements` | object (map) | **The field rules** — map of field name → `Element`. This is the primary payload. |
| `requiredFieldCombinations` | object (map) | Complex OR-group field requirement rules (see Section 8) |

---

### 5.3 Element

Each key in `Configuration.elements` is a field name; the value is an `Element` describing that field's rules for the given payer.

#### Display / Identity Fields

| Field | Type | Description |
|---|---|---|
| `label` | string | Human-friendly field label for UI display |
| `type` | string | Element type — drives UI rendering and serialization (see Section 6) |
| `mode` | string | Display mode for enumerable fields: `"DropDown"` or `"RadioGroup"` |
| `order` | integer | Rendering order within the parent element |
| `hidden` | boolean | If `true`, do not display this field in the UI |
| `groups` | array of string | UI grouping labels |
| `information` | array of string | Informational text to display with the field |
| `helpTopicId` | string | Help topic ID for contextual help |
| `errorMessage` | string | Custom error message to display on validation failure |
| `defaultValue` | any | Default value to pre-populate |

#### Validation Fields

| Field | Type | Description |
|---|---|---|
| `required` | boolean | Field is unconditionally required |
| `allowed` | boolean | Field is allowed (if `false`, do not send this field) |
| `minLength` | integer | Minimum character length |
| `maxLength` | integer | Maximum character length |
| `min` | date-time | Minimum allowed date (for `Date` type elements) |
| `max` | date-time | Maximum allowed date (for `Date` type elements) |
| `pattern` | string | Regular expression the value must match |
| `repeats` | boolean | Whether this field can repeat (multi-value) |
| `minRepeats` | integer | Minimum number of repetitions |
| `maxRepeats` | integer | Maximum number of repetitions |

#### Allowed Values

| Field | Type | Description |
|---|---|---|
| `values` | any | List of allowed values or link to allowed values |
| `valuesWhen` | object (map) | Conditional allowed values — key is a condition name, value is array of allowed value objects |

#### Conditional Validation Fields

These fields override the base validation rules when a condition is met. Each is a map of condition-name → `FieldCondition` (see Section 5.4).

| Field | Type | Description |
|---|---|---|
| `requiredWhen` | map → `FieldCondition` | Field becomes required when condition is true |
| `notRequiredWhen` | map → `FieldCondition` | Field is NOT required when condition is true (overrides `required`) |
| `allowedWhen` | map → `FieldCondition` | Field is allowed when condition is true |
| `notAllowedWhen` | map → `FieldCondition` | Field is NOT allowed when condition is true |
| `maxLengthWhen` | map → array of `FieldCondition` | Conditional max length overrides |
| `patternWhen` | map → array of `FieldCondition` | Conditional regex pattern overrides |

#### Child Structure Fields

| Field | Type | Description |
|---|---|---|
| `elements` | map → `Element` | Child elements (for `Section`, `Object`, `ObjectArray` types) |
| `objectTypes` | map → `ObjectType` | Type prototypes for `ObjectArray` elements — defines distinct subtypes within an array (see Section 5.5) |

---

### 5.4 FieldCondition

Used in all conditional element fields (`requiredWhen`, `allowedWhen`, etc.). Defines the condition under which the rule applies, evaluated against the **value of the field referenced by the condition map key**.

| Field | Type | Description |
|---|---|---|
| `equalTo` | string | Condition is true when referenced field equals this value |
| `containedIn` | array of string | Condition is true when referenced field value is in this list |
| `greaterThan` | string | Condition is true when referenced field value is greater than this |
| `greaterEqual` | string | Condition is true when referenced field value is ≥ this |
| `lessThan` | string | Condition is true when referenced field value is less than this |
| `lessEqual` | string | Condition is true when referenced field value is ≤ this |
| `maxLength` | integer | Condition is true when referenced field length ≤ this value |
| `pattern` | integer | Regex pattern condition |
| `values` | any | Possible values or link to possible values |

> **Reading a condition:** The map key is the field name being evaluated; the `FieldCondition` value specifies how to evaluate it. For example, `requiredWhen: { "subscriberRelationshipCode": { "containedIn": ["01","19"] } }` means "this field is required when `subscriberRelationshipCode` is `01` or `19`."

---

### 5.5 ObjectType

Used within `Element.objectTypes` for `ObjectArray` elements. Defines the shape, constraints, and discriminators for each distinct subtype within an object array (e.g., different procedure qualifier types).

| Field | Type | Description |
|---|---|---|
| `label` | string | Human-readable label for this object type |
| `required` | boolean | Whether at least one instance of this type is required |
| `minInstances` | integer | Minimum number of instances of this object type |
| `maxInstances` | integer | Maximum number of instances of this object type |
| `fieldValues` | map → `FieldCondition` | Discriminator field values that identify this object type |
| `requiredWhen` | map → `FieldCondition` | Object type is required when condition is true |
| `notRequiredWhen` | map → `FieldCondition` | Object type is not required when condition is true |
| `allowedWhen` | map → `FieldCondition` | Object type is allowed when condition is true |
| `notAllowedWhen` | map → `FieldCondition` | Object type is not allowed when condition is true |

---

### 5.6 ErrorResponse

| Field | Type | Description |
|---|---|---|
| `userMessage` | string | High-level human-readable error message |
| `developerMessage` | string | Technical error detail |
| `statusCode` | integer | HTTP-equivalent status code |
| `reasonCode` | integer | Internal reason code |
| `errors[]` | array of `FieldError` | Per-field errors (`field`, `errorMessage`, `code`, `index`) |

---

## 6. Element Type Reference

The `Element.type` field drives how a field should be rendered in the UI and how its value should be serialized in the transaction API request.

| type | UI Widget | Serialization | Notes |
|---|---|---|---|
| `Text` | Standard text input | String | Most common type |
| `Number` | Text input (numeric) | Numeric | Serialized as a number, not a string |
| `Boolean` | Checkbox | Boolean (`true`/`false`) | |
| `Date` | Date picker | `YYYY-MM-DD` or date-time | Respects `min`/`max` bounds |
| `Enumeration` | Searchable inline dropdown | String | Values from `values` or `valuesWhen`; `mode` may override to RadioGroup |
| `Collection` | Searchable REST-backed dropdown | String | Values fetched from a backing API endpoint |
| `Section` | Grouping container with text | N/A | Not submitted; contains child `elements` |
| `Object` | Grouping with metadata | Object | Like Section but with additional metadata; contains child `elements` |
| `ObjectArray` | Repeating group | Array of objects | Controlled by `minRepeats`, `maxRepeats`, `objectTypes` |
| `Information` | Display-only text | N/A | Not submitted; informational label only |
| `Unsupported` | Not rendered | N/A | Do not display or submit |

---

## 7. Conditional Logic Reference

Configurations use a rich conditional system. The general pattern is:

```
Element.{rule}When = {
  "fieldName": FieldCondition
}
```

Where `fieldName` is another element key in the same configuration and `FieldCondition` describes the trigger.

### Evaluation Order (highest to lowest precedence)

1. `notAllowedWhen` — if any condition matches, the field must not be sent
2. `allowedWhen` — field is only allowed if a condition matches (exclusive allowed)
3. `notRequiredWhen` — if any condition matches, the field is not required (overrides `required: true`)
4. `requiredWhen` — if any condition matches, the field becomes required
5. `required` — unconditional required flag
6. `allowed` — unconditional allowed flag
7. `maxLengthWhen` / `patternWhen` — apply when their conditions match

### Example — Conditional Required

```json
"patient.suffix": {
  "type": "Text",
  "label": "Suffix",
  "required": false,
  "requiredWhen": {
    "subscriber.memberId": { "equalTo": "" }
  }
}
```
→ `patient.suffix` is required only when `subscriber.memberId` is empty.

### Example — Conditional Not Allowed

```json
"medicaidId": {
  "type": "Text",
  "label": "Medicaid ID",
  "notAllowedWhen": {
    "payer.id": { "containedIn": ["BCBSF", "AETNA"] }
  }
}
```
→ `medicaidId` must not be sent when the payer is BCBSF or AETNA.

### Example — Conditional Max Length

```json
"groupNumber": {
  "type": "Text",
  "maxLength": 20,
  "maxLengthWhen": {
    "insuranceTypeCode": [{ "equalTo": "HM" }]
  }
}
```
→ `groupNumber` has a different max length when insurance type is HM.

---

## 8. requiredFieldCombinations Logic

The `Configuration.requiredFieldCombinations` object defines complex OR-group field requirements that cannot be expressed with per-element `required` flags alone.

### Structure

```json
"requiredFieldCombinations": {
  "groupName": [
    ["fieldA", "fieldB"],
    ["fieldC"],
    ["fieldD", "fieldE", "fieldF"]
  ]
}
```

### Semantics

Each entry in the outer object is a named rule group. The value is an **array of arrays**. The rule is satisfied when **at least one inner array has all its fields populated**.

Reading the example above: the rule is satisfied if any one of the following is true:
- Both `fieldA` **and** `fieldB` are provided, **OR**
- `fieldC` is provided, **OR**
- All three of `fieldD`, `fieldE`, **and** `fieldF` are provided

### Example — Member Identification

A common payer pattern: you must identify the member by at least one of these combinations:

```json
"requiredFieldCombinations": {
  "memberIdentification": [
    ["memberId"],
    ["patientLastName", "patientFirstName", "patientBirthDate"],
    ["patientSSN"]
  ]
}
```

→ The request is valid if any of these is provided:
- `memberId` alone, **OR**
- All three of `patientLastName` + `patientFirstName` + `patientBirthDate`, **OR**
- `patientSSN` alone

### Validation Algorithm

```python
def validate_required_combinations(
    submitted_fields: dict,
    required_field_combinations: dict,
) -> list[str]:
    """
    Returns a list of violation messages.
    An empty list means all combination rules pass.
    """
    violations = []

    for group_name, combinations in required_field_combinations.items():
        # At least one combination must be fully satisfied
        satisfied = any(
            all(
                submitted_fields.get(field) not in (None, "", [], {})
                for field in combo
            )
            for combo in combinations
        )
        if not satisfied:
            options = " OR ".join(
                "(" + " + ".join(combo) + ")"
                for combo in combinations
            )
            violations.append(
                f"Rule '{group_name}': must provide at least one of: {options}"
            )

    return violations
```

---

## 9. HTTP Status Code Reference

| Code | Meaning | Action |
|---|---|---|
| `200` | OK — configurations returned | Process `ResultSet` |
| `400` | Bad Request — missing `type` or invalid params | Check `ErrorResponse.errors[]` |
| `401` | Unauthorized | Refresh token |
| `403` | Forbidden — scope insufficient | Check OAuth scope |
| `500` | Internal Server Error | Retry with backoff |

---

## 10. Sample curl Calls

### 10.1 Get Token

```bash
TOKEN=$(curl -s -X POST "https://api.availity.com/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials\
      &client_id=${AVAILITY_CLIENT_ID}\
      &client_secret=${AVAILITY_CLIENT_SECRET}\
      &scope=healthcare-hipaa-transactions" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

---

### 10.2 Get Coverages (270) Configuration for a Specific Payer

```bash
curl -X GET \
  "https://api.availity.com/v1/configurations\
?type=coverages\
&payerId=BCBSF" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 10.3 Get Service Reviews (278I) Configuration for a Specific Payer

```bash
curl -X GET \
  "https://api.availity.com/v1/configurations\
?type=service-reviews\
&payerId=AETNA" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 10.4 Get Claim Status (276) Configuration for a Specific Payer

```bash
curl -X GET \
  "https://api.availity.com/v1/configurations\
?type=claim-statuses\
&payerId=00611" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 10.5 Get All Configurations for a Type (No Payer Filter — Abbreviated)

```bash
# Returns abbreviated configurations for all payers supporting this type
# Use for discovery only — not for validation
curl -X GET \
  "https://api.availity.com/v1/configurations?type=coverages" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 10.6 Get Configuration with Subtype

```bash
curl -X GET \
  "https://api.availity.com/v1/configurations\
?type=service-reviews\
&subtypeId=professional\
&payerId=BCBSF" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

## 11. Sample Python Integration

### 11.1 Configurations Client

```python
# app/services/availity_configurations.py
import httpx
from typing import Optional


class AvailityConfigurationsClient:

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://api.availity.com",
        scope: str = "healthcare-hipaa-transactions",
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

    async def get_configurations(
        self,
        config_type: str,                   # "coverages", "service-reviews", "claim-statuses"
        payer_id: Optional[str] = None,
        subtype_id: Optional[str] = None,
    ) -> dict:
        """
        Fetch payer-specific configurations for a transaction type.
        Returns the full ResultSet.
        Always include payer_id for full (non-abbreviated) configurations.
        """
        token = await self.get_token()
        params = {"type": config_type}
        if payer_id:
            params["payerId"] = payer_id
        if subtype_id:
            params["subtypeId"] = subtype_id

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/v1/configurations",
                params=params,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept":        "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_configuration(
        self,
        config_type: str,
        payer_id: str,
        subtype_id: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Fetch the single most-specific configuration for a payer.
        Returns the first Configuration object, or None if not found.
        """
        result_set = await self.get_configurations(config_type, payer_id, subtype_id)
        configs = result_set.get("configurations", [])
        return configs[0] if configs else None
```

### 11.2 Configuration Validator

```python
# app/services/configuration_validator.py
from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# FieldCondition evaluation
# ──────────────────────────────────────────────────────────────────────────────

def evaluate_condition(field_value: Any, condition: dict) -> bool:
    """
    Evaluate a FieldCondition against an actual field value.
    Returns True if the condition is satisfied.
    """
    if not condition:
        return False

    val = str(field_value) if field_value is not None else ""

    if "equalTo" in condition:
        return val == condition["equalTo"]

    if "containedIn" in condition:
        return val in condition["containedIn"]

    if "greaterThan" in condition:
        try:
            return float(val) > float(condition["greaterThan"])
        except (ValueError, TypeError):
            return False

    if "greaterEqual" in condition:
        try:
            return float(val) >= float(condition["greaterEqual"])
        except (ValueError, TypeError):
            return False

    if "lessThan" in condition:
        try:
            return float(val) < float(condition["lessThan"])
        except (ValueError, TypeError):
            return False

    if "lessEqual" in condition:
        try:
            return float(val) <= float(condition["lessEqual"])
        except (ValueError, TypeError):
            return False

    if "maxLength" in condition:
        return len(val) <= condition["maxLength"]

    return False


def evaluate_condition_map(
    submitted: dict,
    condition_map: dict,
) -> bool:
    """
    Evaluate a condition map (fieldName → FieldCondition).
    Returns True if ANY condition in the map is satisfied (OR logic).
    """
    for field_name, condition in condition_map.items():
        value = submitted.get(field_name)
        if evaluate_condition(value, condition):
            return True
    return False


# ──────────────────────────────────────────────────────────────────────────────
# Per-element validation
# ──────────────────────────────────────────────────────────────────────────────

def validate_element(
    field_name: str,
    element: dict,
    submitted: dict,
) -> list[str]:
    """
    Validate a single submitted field against its Element configuration rules.
    Returns a list of error strings (empty = valid).
    """
    errors = []
    value  = submitted.get(field_name)
    has_value = value not in (None, "", [], {})

    # ── 1. notAllowedWhen ─────────────────────────────────────────
    not_allowed_when = element.get("notAllowedWhen", {})
    if not_allowed_when and evaluate_condition_map(submitted, not_allowed_when):
        if has_value:
            errors.append(
                f"'{field_name}': field is not allowed under current conditions"
            )
        return errors  # no further checks if not allowed

    # ── 2. allowedWhen (exclusive) ────────────────────────────────
    allowed_when = element.get("allowedWhen", {})
    if allowed_when and not evaluate_condition_map(submitted, allowed_when):
        if has_value:
            errors.append(
                f"'{field_name}': field is only allowed under specific conditions "
                f"which are not met"
            )
        return errors

    # ── 3. Unconditional not allowed ──────────────────────────────
    if element.get("allowed") is False and has_value:
        errors.append(f"'{field_name}': field is not allowed for this payer")
        return errors

    # ── 4. Required checks ────────────────────────────────────────
    not_required_when = element.get("notRequiredWhen", {})
    required_when     = element.get("requiredWhen", {})
    is_required       = element.get("required", False)

    if not_required_when and evaluate_condition_map(submitted, not_required_when):
        is_required = False
    elif required_when and evaluate_condition_map(submitted, required_when):
        is_required = True

    if is_required and not has_value:
        label = element.get("label", field_name)
        errors.append(f"'{field_name}' ({label}): field is required")

    if not has_value:
        return errors  # no further checks if no value submitted

    str_value = str(value)

    # ── 5. Length validation ──────────────────────────────────────
    min_len = element.get("minLength")
    max_len = element.get("maxLength")

    # Check conditional max length overrides
    max_len_when = element.get("maxLengthWhen", {})
    for cond_name, conditions in max_len_when.items():
        if isinstance(conditions, list):
            for cond in conditions:
                if evaluate_condition(submitted.get(cond_name), cond):
                    max_len = cond.get("maxLength", max_len)
                    break

    if min_len and len(str_value) < min_len:
        errors.append(
            f"'{field_name}': minimum length is {min_len}, got {len(str_value)}"
        )
    if max_len and len(str_value) > max_len:
        errors.append(
            f"'{field_name}': maximum length is {max_len}, got {len(str_value)}"
        )

    # ── 6. Pattern validation ─────────────────────────────────────
    import re
    pattern = element.get("pattern")

    # Check conditional pattern overrides
    pattern_when = element.get("patternWhen", {})
    for cond_name, conditions in pattern_when.items():
        if isinstance(conditions, list):
            for cond in conditions:
                if evaluate_condition(submitted.get(cond_name), cond):
                    pattern = cond.get("pattern", pattern)
                    break

    if pattern:
        try:
            if not re.fullmatch(pattern, str_value):
                error_msg = element.get("errorMessage") or (
                    f"'{field_name}': value does not match required pattern"
                )
                errors.append(error_msg)
        except re.error:
            pass  # malformed pattern — skip

    # ── 7. Enumeration / values check ────────────────────────────
    element_type = element.get("type")
    if element_type in ("Enumeration",):
        allowed_values = element.get("values")
        if isinstance(allowed_values, list):
            allowed_strings = [
                str(v.get("code", v.get("value", v)))
                if isinstance(v, dict) else str(v)
                for v in allowed_values
            ]
            if str_value not in allowed_strings:
                errors.append(
                    f"'{field_name}': value '{str_value}' not in allowed values"
                )

    return errors


# ──────────────────────────────────────────────────────────────────────────────
# Full configuration validator
# ──────────────────────────────────────────────────────────────────────────────

def validate_against_configuration(
    configuration: dict,
    submitted: dict,
    prefix: str = "",
) -> list[str]:
    """
    Validate a submitted field dictionary against a full Configuration object.
    Recursively validates nested Section/Object/ObjectArray elements.
    Returns list of error strings — empty list means valid.
    """
    all_errors = []
    elements = configuration.get("elements", {})

    for field_name, element in elements.items():
        full_name = f"{prefix}{field_name}" if prefix else field_name
        element_type = element.get("type", "Text")

        # Skip unsupported and information-only elements
        if element_type in ("Unsupported", "Information"):
            continue

        # Recurse into Section and Object
        if element_type in ("Section", "Object") and element.get("elements"):
            child_submitted = submitted.get(field_name, {})
            if isinstance(child_submitted, dict):
                child_errors = validate_against_configuration(
                    {"elements": element["elements"]},
                    child_submitted,
                    prefix=f"{full_name}.",
                )
                all_errors.extend(child_errors)
            continue

        # Validate ObjectArray items
        if element_type == "ObjectArray":
            items = submitted.get(field_name, [])
            if not isinstance(items, list):
                items = [items]
            for i, item in enumerate(items):
                if element.get("elements"):
                    item_errors = validate_against_configuration(
                        {"elements": element["elements"]},
                        item,
                        prefix=f"{full_name}[{i}].",
                    )
                    all_errors.extend(item_errors)
            # Check repeat counts
            min_rep = element.get("minRepeats", 0)
            max_rep = element.get("maxRepeats")
            if len(items) < min_rep:
                all_errors.append(
                    f"'{full_name}': minimum {min_rep} items required, got {len(items)}"
                )
            if max_rep and len(items) > max_rep:
                all_errors.append(
                    f"'{full_name}': maximum {max_rep} items allowed, got {len(items)}"
                )
            continue

        # Standard element validation
        element_errors = validate_element(field_name, element, submitted)
        for err in element_errors:
            all_errors.append(err.replace(f"'{field_name}'", f"'{full_name}'"))

    # requiredFieldCombinations
    combo_errors = validate_required_combinations(
        submitted,
        configuration.get("requiredFieldCombinations", {}),
    )
    all_errors.extend(combo_errors)

    return all_errors


def validate_required_combinations(
    submitted: dict,
    required_field_combinations: dict,
) -> list[str]:
    """
    Validate OR-group field combination rules.
    Returns violation messages — empty means all rules pass.
    """
    violations = []

    for group_name, combinations in required_field_combinations.items():
        satisfied = any(
            all(
                submitted.get(field) not in (None, "", [], {})
                for field in combo
            )
            for combo in combinations
        )
        if not satisfied:
            options = " OR ".join(
                "(" + " + ".join(combo) + ")"
                for combo in combinations
            )
            violations.append(
                f"Rule '{group_name}': must provide at least one of: {options}"
            )

    return violations
```

### 11.3 Usage Example

```python
import asyncio
import os

config_client = AvailityConfigurationsClient(
    client_id     = os.environ["AVAILITY_CLIENT_ID"],
    client_secret = os.environ["AVAILITY_CLIENT_SECRET"],
)


async def submit_eligibility_with_validation(
    payer_id: str,
    submission: dict,
) -> dict:
    """
    Fetch payer config, validate submission, then call Coverages API.
    Raises ValueError with field-level detail if validation fails.
    """
    # 1. Fetch payer-specific field rules
    config = await config_client.get_configuration(
        config_type = "coverages",
        payer_id    = payer_id,
    )

    if not config:
        print(f"No configuration found for payer {payer_id} — submitting without validation")
    else:
        # 2. Validate
        errors = validate_against_configuration(config, submission)
        if errors:
            raise ValueError(
                f"Submission failed payer validation for {payer_id}:\n"
                + "\n".join(f"  • {e}" for e in errors)
            )

    # 3. Submit to Coverages API
    from app.services.availity_api import AvailityClient
    coverages_client = AvailityClient(
        client_id     = os.environ["AVAILITY_CLIENT_ID"],
        client_secret = os.environ["AVAILITY_CLIENT_SECRET"],
    )
    return await coverages_client.check_eligibility(**submission)


async def main():
    payer_id = "BCBSF"

    # Build submission
    submission = {
        "payerId":          payer_id,
        "memberId":         "XYZ123456789",
        "patientLastName":  "DOE",
        "patientFirstName": "JANE",
        "patientBirthDate": "1985-06-15",
        "providerNpi":      "1234567890",
        "serviceType":      "30",
        "asOfDate":         "2025-03-01",
    }

    try:
        coverage = await submit_eligibility_with_validation(payer_id, submission)
        print(f"Eligibility status: {coverage.get('statusCode')}")
    except ValueError as e:
        print(f"Validation error:\n{e}")

asyncio.run(main())
```

---

## 12. How Configurations Relate to the Other Exp 47 APIs

The Configurations API is the **validation layer** that sits in front of all three transaction APIs. The recommended call sequence for every submission:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Step 1 — Payer List API                                            │
│  GET /epdm-payer-list-aws/v1/availity-payer-list?payerId=X         │
│  → Confirms payer supports the transaction via API                  │
│  → Flags enrollment requirements and payer-specific notes           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│  Step 2 — Configurations API                                        │
│  GET /v1/configurations?type={coverages|service-reviews|...}        │
│                           &payerId=X                                │
│  → Fetches field-level rules: required, allowed, maxLength, pattern │
│  → Fetches requiredFieldCombinations (OR-group member ID rules)     │
│  → Validates submission before it reaches the payer                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│  Step 3 — Transaction API                                           │
│  POST /v1/coverages                (eligibility)                    │
│  POST /v2/service-reviews          (prior auth)                     │
│  POST /v1/claim-statuses           (claim status)                   │
│  → Submitted with confidence — payer-specific rules already applied │
└─────────────────────────────────────────────────────────────────────┘
```

### Configuration Type to Transaction API Mapping

| `type` param | Transaction API | X12 |
|---|---|---|
| `coverages` | `POST /v1/coverages` | 270/271 |
| `service-reviews` | `POST /v2/service-reviews` | 278I |
| `claim-statuses` | `POST /v1/claim-statuses` | 276/277 |

### What the Config Catches That the Transaction API Won't Explain

| Problem | Without Config | With Config |
|---|---|---|
| Missing required field | 400 from payer, vague message | Field-level error before submission |
| Field not allowed for this payer | 400 or silent rejection | Flagged as `notAllowed` before submission |
| Wrong member ID format | Rejected by payer | Caught by `pattern` or `maxLength` rule |
| Complex member ID OR-group | Rejected — no clear reason | `requiredFieldCombinations` violation surfaced |
| Conditional required field missed | 400 with cryptic payer code | `requiredWhen` condition caught locally |

---

## 13. PMS Integration Patterns

### Pattern 1 — Configuration Cache (Nightly Refresh per Payer)

```python
# Cache configurations per payer + type — they change rarely
# Refresh nightly alongside the payer list

async def refresh_configuration_cache(
    payer_ids: list[str],
    transaction_types: list[str] = None,
):
    if transaction_types is None:
        transaction_types = ["coverages", "service-reviews", "claim-statuses"]

    for payer_id in payer_ids:
        for tx_type in transaction_types:
            config = await config_client.get_configuration(tx_type, payer_id)
            if config:
                cache_key = f"availity_config:{tx_type}:{payer_id}"
                await cache.set(cache_key, config, ttl_seconds=86400)  # 24h
```

### Pattern 2 — Dynamic Form Rendering from Configuration

```python
def build_form_schema(configuration: dict) -> list[dict]:
    """
    Convert an Availity Configuration into an ordered list of form field
    definitions suitable for dynamic UI rendering.
    Excludes Unsupported and Information elements from rendered output.
    """
    RENDERABLE = {"Text", "Number", "Boolean", "Date", "Enumeration", "Collection"}

    fields = []
    for field_name, element in configuration.get("elements", {}).items():
        el_type = element.get("type", "Text")
        if el_type not in RENDERABLE:
            continue

        fields.append({
            "name":         field_name,
            "label":        element.get("label", field_name),
            "type":         el_type,
            "mode":         element.get("mode"),
            "order":        element.get("order", 999),
            "required":     element.get("required", False),
            "hidden":       element.get("hidden", False),
            "minLength":    element.get("minLength"),
            "maxLength":    element.get("maxLength"),
            "pattern":      element.get("pattern"),
            "values":       element.get("values"),
            "defaultValue": element.get("defaultValue"),
            "information":  element.get("information", []),
            "hasConditions": any([
                element.get("requiredWhen"),
                element.get("notRequiredWhen"),
                element.get("allowedWhen"),
                element.get("notAllowedWhen"),
            ]),
        })

    return sorted(fields, key=lambda f: f["order"])
```

### Pattern 3 — Pre-Submit Validation Pipeline

```python
async def pre_submit_validate(
    payer_id: str,
    transaction_type: str,    # "coverages" | "service-reviews" | "claim-statuses"
    submission: dict,
) -> tuple[bool, list[str]]:
    """
    Full pre-submission validation:
      1. Fetch config from cache or API
      2. Run element-level validation
      3. Run requiredFieldCombinations validation
    Returns (is_valid, errors).
    """
    cache_key = f"availity_config:{transaction_type}:{payer_id}"
    config = await cache.get(cache_key)

    if not config:
        config = await config_client.get_configuration(transaction_type, payer_id)
        if config:
            await cache.set(cache_key, config, ttl_seconds=86400)

    if not config:
        # No config available — warn but do not block
        return True, ["WARNING: No configuration found — submitting without payer validation"]

    errors = validate_against_configuration(config, submission)
    return len(errors) == 0, errors
```

---

*Source: Availity Configurations 1.0.0 Swagger Specification (configurationdocument.json) · Swagger 2.0 · Host: api.availity.com · BasePath: /v1*
