# Availity Claim Statuses API 1.0.0 — Developer Reference
**Experiment 47 · PMS Integration · MPS Inc.**  
Source: Availity Claim Statuses Swagger Spec (claims-statuses-document.json)  
Last Updated: March 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Base URLs & Endpoints Summary](#3-base-urls--endpoints-summary)
4. [Async Polling Pattern](#4-async-polling-pattern)
5. [POST /claim-statuses — Search / Initiate](#5-post-claim-statuses--search--initiate)
6. [GET /claim-statuses/{id} — Poll for Full Status](#6-get-claim-statusesid--poll-for-full-status)
7. [DELETE /claim-statuses/{id} — Delete a Record](#7-delete-claim-statusesid--delete-a-record)
8. [Response Models](#8-response-models)
   - [ResultSet (POST response)](#81-resultset-post-200202-response)
   - [ClaimStatusSummary](#82-claimstatussummary)
   - [ClaimStatus (Full — GET response)](#83-claimstatus-full--get-200-response)
   - [ClaimStatusResult](#84-claimstatusresult)
   - [ClaimStatusDetail](#85-claimstatusdetail)
   - [ServiceLine](#86-serviceline)
   - [Subscriber](#87-subscriber)
   - [Patient](#88-patient)
   - [Provider](#89-provider)
   - [Submitter](#810-submitter)
   - [Payer](#811-payer)
   - [ErrorResponse](#812-errorresponse)
9. [HTTP Status Code Reference](#9-http-status-code-reference)
10. [Claim Status Codes & Categories](#10-claim-status-codes--categories)
11. [Sample curl Calls](#11-sample-curl-calls)
12. [Sample Python Integration](#12-sample-python-integration)
13. [Key Differences from Coverages API](#13-key-differences-from-coverages-api)
14. [PMS Integration Patterns](#14-pms-integration-patterns)

---

## 1. Overview

The **Availity Claim Statuses 1.0.0 API** enables healthcare providers and systems to check the status of submitted claims in real time using standardized HIPAA transactions (X12 276/277).

**Key behaviors:**

- `POST /claim-statuses` uses an **unusual pattern**: it is a POST with `X-HTTP-Method-Override: GET` header — functionally a search/query, not a write operation
- The POST returns a `ResultSet` containing an array of `ClaimStatusSummary` objects
- Poll `GET /claim-statuses/{id}` using the `id` from a summary to retrieve the full `ClaimStatus` detail including service line adjudication
- The API is asynchronous — `202 Accepted` means the payer response is pending; poll until `statusCode` reaches `"4"` (Complete)
- Availity caches results until `expirationDate`

---

## 2. Authentication

**Scheme:** OAuth 2.0 Client Credentials (`application` flow)  
**Token URL:** `https://api.availity.com/v1/token`

### Required Scopes

| Scope | Plan |
|---|---|
| `healthcare-hipaa-transactions` | Standard |
| `healthcare-hipaa-transactions-demo` | Demo (sandbox) |
| `healthcare-hipaa-transactions-standard` | Standard (explicit) |
| `healthcare-hipaa-transactions-highvolume` | High Volume |
| `healthcare-hipaa-transactions-highvolume-standard` | High Volume Standard |
| `healthcare-hipaa-transactions-highvolume-unlimited` | Unlimited |

### Token Request

```bash
curl -X POST "https://api.availity.com/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials\
      &client_id=${AVAILITY_CLIENT_ID}\
      &client_secret=${AVAILITY_CLIENT_SECRET}\
      &scope=healthcare-hipaa-transactions healthcare-hipaa-transactions-demo"
```

### Token Response

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 300
}
```

> Token TTL = **5 minutes**. Cache with 4.5-minute effective TTL. Token calls count against your rate limit.

---

## 3. Base URLs & Endpoints Summary

| Environment | Base URL |
|---|---|
| Production | `https://api.availity.com/v1` |
| QUA / Sandbox | `https://qua.api.availity.com/v1` |
| Test | `https://tst.api.availity.com/v1` |

| Method | Path | Operation | Description |
|---|---|---|---|
| `POST` | `/claim-statuses` | `findClaimStatus` | Search for claim statuses (requires `X-HTTP-Method-Override: GET`) |
| `GET` | `/claim-statuses/{id}` | `getClaimStatusById` | Poll for full claim status detail by ID |
| `DELETE` | `/claim-statuses/{id}` | *(unnamed)* | Delete a claim status record |

> **Important:** The `POST /claim-statuses` endpoint **requires** the header `X-HTTP-Method-Override: GET`. This is a query operation masquerading as POST due to HIPAA transaction length constraints on GET query strings. Missing this header will result in an error.

---

## 4. Async Polling Pattern

```
POST /claim-statuses  (X-HTTP-Method-Override: GET)
  → 202 Accepted  → extract id from ResultSet.claimStatuses[n].id
  → 200 OK        → cached hit, may still need polling per record

  For each ClaimStatusSummary.id in ResultSet:

    GET /claim-statuses/{id}
      → statusCode = "0"  → In Progress — wait 2s, poll again
      → statusCode = "1"  → Retrying — payer timeout, poll again
      → statusCode = "4"  → Complete ✓ — full adjudication data available
      → statusCode = "R"  → Request Error — stop, check validationMessages
      → statusCode = "E"  → Communication Error — stop
```

> The POST response returns **one or more** `ClaimStatusSummary` records in `ResultSet.claimStatuses[]`. Each has its own `id` and `statusCode`. Poll each separately.

---

## 5. POST /claim-statuses — Search / Initiate

**`POST https://api.availity.com/v1/claim-statuses`**

- **Content-Type:** `application/x-www-form-urlencoded`
- **Accept:** `application/json` or `application/xml`
- **Auth:** Bearer token
- **Required Header:** `X-HTTP-Method-Override: GET`

### Request Parameters

All form-data (URL-encoded). All optional per spec; payer-specific required fields enforced at submission.

#### Special / Required Header

| Parameter | Type | Required | Description |
|---|---|---|---|
| `X-HTTP-Method-Override` | string | ✅ **REQUIRED** | Must be `GET`. Overrides the POST method for query semantics. |

#### Payer

| Parameter | Type | Description |
|---|---|---|
| `payer.id` | string | Availity payer ID of the health plan |

#### Submitter

| Parameter | Type | Description |
|---|---|---|
| `submitter.id` | string | Submitter's identification number |
| `submitter.lastName` | string | Submitter's last or business name |
| `submitter.firstName` | string | Submitter's first name |
| `submitter.middleName` | string | Submitter's middle name |
| `submitter.suffix` | string | Submitter's suffix |

#### Provider

| Parameter | Type | Description |
|---|---|---|
| `providers.npi` | string | Provider's NPI (10-digit national provider identifier) |
| `providers.taxId` | string | Provider's tax ID |
| `providers.lastName` | string | Provider's last name or organization name |
| `providers.firstName` | string | Provider's first name |
| `providers.middleName` | string | Provider's middle name |
| `providers.suffix` | string | Provider's suffix |
| `providers.payerAssignedProviderId` | string | Payer-assigned provider ID |

#### Subscriber (Policy Holder)

| Parameter | Type | Description |
|---|---|---|
| `subscriber.memberId` | string | Health plan member ID of the subscriber — **primary identifier** |
| `subscriber.lastName` | string | Subscriber's last name |
| `subscriber.firstName` | string | Subscriber's first name |
| `subscriber.middleName` | string | Subscriber's middle name |
| `subscriber.suffix` | string | Subscriber's suffix |

#### Patient

| Parameter | Type | Format | Description |
|---|---|---|---|
| `patient.lastName` | string | | Patient's last name |
| `patient.firstName` | string | | Patient's first name |
| `patient.middleName` | string | | Patient's middle name |
| `patient.suffix` | string | | Patient's suffix |
| `patient.birthDate` | string | date | Patient's date of birth (`YYYY-MM-DD`) |
| `patient.genderCode` | string | | Patient's gender code (`M`, `F`, `U`) |
| `patient.accountNumber` | string | | Provider's patient account number |
| `patient.subscriberRelationshipCode` | string | | Patient's relationship to subscriber (`18`=Self, `01`=Spouse, `19`=Child, `G8`=Other) |

#### Claim Identifiers & Dates

| Parameter | Type | Format | Description |
|---|---|---|---|
| `claimNumber` | string | | Health plan's claim tracking number assigned when original claim was received |
| `claimAmount` | string | | Total charge amount of the original claim |
| `fromDate` | string | date | Service from date (`YYYY-MM-DD`) |
| `toDate` | string | date | Service to date (`YYYY-MM-DD`) |
| `facilityTypeCode` | string | | Facility type code (institutional claims; identifies where services were performed) |
| `frequencyTypeCode` | string | | Frequency type code (institutional claims; identifies claim frequency) |

### Responses

| HTTP Code | Description | Schema |
|---|---|---|
| `200 OK` | Cached results returned immediately | `ResultSet` |
| `202 Accepted` | Request in progress — poll each `id` in result | `ResultSet` |
| `400 Bad Request` | Validation failure | `ErrorResponse` |
| `401 Unauthorized` | Invalid or missing token | `ErrorResponse` |
| `403 Forbidden` | Insufficient scope | `ErrorResponse` |
| `500 Internal Server Error` | Server error | `ErrorResponse` |

---

## 6. GET /claim-statuses/{id} — Poll for Full Status

**`GET https://api.availity.com/v1/claim-statuses/{id}`**

- **Accept:** `application/json` or `application/xml`
- **Auth:** Bearer token

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | ✅ Yes | Claim status ID from `ResultSet.claimStatuses[n].id` |

### Responses

| HTTP Code | Description | Schema |
|---|---|---|
| `200 OK` | Complete — full claim status detail | `ClaimStatus` |
| `202 Accepted` | In progress — keep polling | `ClaimStatus` |
| `400 Bad Request` | Validation failure | `ErrorResponse` |
| `401 Unauthorized` | Invalid or missing token | `ErrorResponse` |
| `403 Forbidden` | Insufficient scope | `ErrorResponse` |
| `404 Not Found` | ID not found or expired | `ErrorResponse` |
| `500 Internal Server Error` | Server error | `ErrorResponse` |

> Returns the full **`ClaimStatus`** model including per-claim `ClaimStatusResult` records, per-service-line adjudication via `ServiceLine`, check/EFT numbers, payment amounts, and denial reason codes.

---

## 7. DELETE /claim-statuses/{id} — Delete a Record

**`DELETE https://api.availity.com/v1/claim-statuses/{id}`**

Deletes a cached claim status record.

### Responses

| HTTP Code | Description |
|---|---|
| `200 OK` | Deleted successfully |

---

## 8. Response Models

### 8.1 ResultSet (POST 200/202 Response)

The top-level response from `POST /claim-statuses`. May contain multiple claim status summaries.

| Field | Type | Description |
|---|---|---|
| `claimStatuses[]` | array of `ClaimStatusSummary` | List of claim status records matching the query |
| `count` | integer | Number of records in this result set |
| `totalCount` | integer | Total number of matching records |
| `limit` | integer | Paging limit |
| `offset` | integer | Paging offset |
| `links` | object | Pagination links (`href` URLs) |

---

### 8.2 ClaimStatusSummary

Lightweight summary returned in the `ResultSet`. Use `id` to poll `GET /claim-statuses/{id}`.

| Field | Type | Description |
|---|---|---|
| `id` | string | **Claim status ID — use for GET/DELETE** |
| `status` | string | Status: `"In Progress"`, `"Complete"`, `"Request Error"`, `"Communication Error"` |
| `statusCode` | string | Status code: `"0"`, `"1"`, `"4"`, `"R"`, `"E"` |
| `controlNumber` | string | Availity-assigned transaction tracking number |
| `customerId` | string | Availity customer ID that owns this record |
| `createdDate` | date-time | When this record was created |
| `updatedDate` | date-time | When this record was last updated |
| `expirationDate` | date-time | When this cached result expires |
| `claimNumber` | string | Claim number from the request |
| `claimAmount` | string | Claim amount from the request |
| `claimCount` | string | Number of distinct claims in the response |
| `fromDate` | date | Service from date |
| `toDate` | date | Service to date |
| `facilityType` | string | Facility type description |
| `facilityTypeCode` | string | Facility type code |
| `frequencyType` | string | Frequency type description |
| `frequencyTypeCode` | string | Frequency type code |
| `payer` | object | Payer summary (id, name) |
| `submitter` | object | Submitter summary |
| `subscriber` | string | Subscriber summary |
| `patient` | object | Patient summary |
| `providers[]` | array | Provider summaries |

---

### 8.3 ClaimStatus (Full — GET 200 Response)

Full detail returned from `GET /claim-statuses/{id}` when `statusCode == "4"`. Contains everything in `ClaimStatusSummary` plus adjudication results.

**Additional fields beyond ClaimStatusSummary:**

| Field | Type | Description |
|---|---|---|
| `claimStatuses[]` | array of `ClaimStatusResult` | One entry per matched claim — full adjudication per claim |
| `patient` | `Patient` | Full patient object (see Section 8.8) |
| `payer` | `Payer` | Full payer object with contact info (see Section 8.11) |
| `providers[]` | array of `Provider` | Full provider objects with claim-level status details |
| `submitter` | `Submitter` | Full submitter object with status details |
| `subscriber` | `Subscriber` | Full subscriber object |
| `userId` | string | User ID of the customer that owns this record |

---

### 8.4 ClaimStatusResult

One entry per matched claim. This is the core adjudication container.

| Field | Type | Description |
|---|---|---|
| `claimControlNumber` | string | Payer's assigned control number / Internal Control Number (ICN) |
| `claimIdentificationNumber` | string | Clearinghouse-assigned trace number of the original claim |
| `patientControlNumber` | string | Patient control number |
| `pharmacyPrescriptionNumber` | string | Pharmacy prescription number |
| `traceId` | string | Referenced transaction trace identifier |
| `voucherNumber` | string | Payer-assigned voucher identifier |
| `fromDate` | date | Claim service from date |
| `toDate` | date | Claim service to date |
| `facilityType` | string | Facility type description |
| `facilityTypeCode` | string | Facility type code of the original institutional claim |
| `frequencyType` | string | Frequency type description |
| `frequencyTypeCode` | string | Frequency type code of the original institutional claim |
| `statusDetails[]` | array of `ClaimStatusDetail` | Claim-level status — adjudication, payment, denial codes |
| `serviceLines[]` | array of `ServiceLine` | Service line–level status and payment detail |

---

### 8.5 ClaimStatusDetail

The atomic adjudication unit — appears at claim level (`ClaimStatusResult.statusDetails[]`), service line level (`ServiceLine.statusDetails[]`), provider level (`Provider.statusDetails[]`), and submitter level (`Submitter.statusDetails[]`).

| Field | Type | Description |
|---|---|---|
| `statusCode` | string | X12 claim status code (e.g., `"1"` = Processed as Primary, `"2"` = Processed as Secondary, `"3"` = Processed as Tertiary, `"4"` = Denied, `"19"` = Pending, `"22"` = Forwarded) |
| `status` | string | Human-readable decode of `statusCode` |
| `categoryCode` | string | X12 claim status category code (e.g., `"A1"` = Acknowledgement, `"F1"` = Finalized, `"P1"` = Pending) |
| `category` | string | Human-readable decode of `categoryCode` |
| `entityCode` | string | X12 entity qualifier code |
| `entity` | string | Human-readable decode of `entityCode` |
| `effectiveDate` | date | Date this status became effective |
| `finalizedDate` | date | Date the original claim was finalized/adjudicated |
| `remittanceDate` | date | Date the original claim was paid |
| `checkNumber` | string | Check or EFT trace number that paid the claim |
| `claimAmount` | string | Charge amount of the original claim |
| `claimAmountUnits` | string | Units for claim amount (e.g., `"dollar"`) |
| `paymentAmount` | string | Amount paid by the health plan |
| `paymentAmountUnits` | string | Units for payment amount |

---

### 8.6 ServiceLine

Per-service-line adjudication — the most granular level of claim status detail.

| Field | Type | Description |
|---|---|---|
| `controlNumber` | string | Service line control number |
| `procedureCode` | string | Procedure code (CPT/HCPCS) |
| `procedure` | string | Human-readable procedure description |
| `procedureQualifierCode` | string | Product or service ID qualifier code |
| `procedureQualifier` | string | Product or service qualifier description |
| `serviceCode` | string | Service identifying number |
| `service` | string | Service description |
| `modifier1Code` / `modifier1` | string | First modifier code and description |
| `modifier2Code` / `modifier2` | string | Second modifier code and description |
| `modifier3Code` / `modifier3` | string | Third modifier code and description |
| `modifier4Code` / `modifier4` | string | Fourth modifier code and description |
| `quantity` | string | Quantity of the product or service |
| `fromDate` | date | Service line from date |
| `toDate` | date | Service line to date |
| `chargeAmount` | string | Line item charge amount |
| `chargeAmountUnits` | string | Units for charge amount |
| `paymentAmount` | string | Line item paid amount |
| `paymentAmountUnits` | string | Units for paid amount |
| `statusDetails[]` | array of `ClaimStatusDetail` | Adjudication detail for this service line |

---

### 8.7 Subscriber

| Field | Type | Description |
|---|---|---|
| `memberId` | string | Health plan member ID ← **key field** |
| `firstName` | string | Subscriber's first name |
| `lastName` | string | Subscriber's last name |
| `middleName` | string | Subscriber's middle name |
| `suffix` | string | Subscriber's suffix |
| `taxId` | string | Subscriber's tax ID |

---

### 8.8 Patient

| Field | Type | Description |
|---|---|---|
| `firstName` | string | Patient's first name |
| `lastName` | string | Patient's last name |
| `middleName` | string | Patient's middle name |
| `suffix` | string | Patient's suffix |
| `birthDate` | date | Patient's date of birth |
| `gender` | string | Patient's gender |
| `genderCode` | string | Patient's gender code |
| `accountNumber` | string | Provider's patient identifier / account number |
| `subscriberRelationship` | string | Patient's relationship to the subscriber |
| `subscriberRelationshipCode` | string | Relationship code (`18`=Self, `01`=Spouse, `19`=Child, `G8`=Other) |

---

### 8.9 Provider

| Field | Type | Description |
|---|---|---|
| `npi` | string | Provider NPI |
| `taxId` | string | Provider tax ID |
| `lastName` | string | Provider last name or organization name |
| `firstName` | string | Provider first name |
| `middleName` | string | Provider middle name |
| `suffix` | string | Provider suffix |
| `payerAssignedProviderId` | string | Payer-assigned provider ID |
| `traceId` | string | Transaction trace identifier |
| `statusDetails[]` | array of `ClaimStatusDetail` | Claim-level status at the provider level |

---

### 8.10 Submitter

| Field | Type | Description |
|---|---|---|
| `id` | string | Submitter identification number |
| `lastName` | string | Submitter last name or organization name |
| `firstName` | string | Submitter first name |
| `middleName` | string | Submitter middle name |
| `suffix` | string | Submitter suffix |
| `traceId` | string | Transaction trace identifier |
| `statusDetails[]` | array of `ClaimStatusDetail` | Status details at the submitter level |

---

### 8.11 Payer

| Field | Type | Description |
|---|---|---|
| `id` | string | Claim status payer ID |
| `name` | string | Claim status payer name |
| `contactName` | string | Payer contact full name |
| `phone` | string | Payer phone number |
| `extension` | string | Phone extension |
| `fax` | string | Payer fax number |
| `emailAddress` | string | Payer email address |
| `ediAccessNumber` | string | EDI access number |

---

### 8.12 ErrorResponse

Returned for all 4xx / 5xx responses.

| Field | Type | Description |
|---|---|---|
| `userMessage` | string | High-level human-readable error message |
| `developerMessage` | string | Technical error detail |
| `statusCode` | integer | HTTP-equivalent status code |
| `reasonCode` | integer | Internal reason code |
| `errors[]` | array of `FieldError` | Per-field validation errors |

#### FieldError

| Field | Type | Description |
|---|---|---|
| `field` | string | Parameter or field that failed |
| `errorMessage` | string | Validation error message |
| `code` | string | Error code |
| `index` | integer | Array index (for repeated fields) |

---

## 9. HTTP Status Code Reference

| Code | Meaning | Action |
|---|---|---|
| `200` | OK — immediate result (cached) | Process `ResultSet` or `ClaimStatus` |
| `202` | Accepted — async in progress | Poll `GET /claim-statuses/{id}` for each record |
| `200` | DELETE success | Done (spec uses 200, not 204, for delete) |
| `400` | Bad Request — validation failure | Check `ErrorResponse.errors[]` |
| `401` | Unauthorized | Refresh token |
| `403` | Forbidden — scope insufficient | Check OAuth scope |
| `404` | Not Found — ID expired or invalid | Resubmit POST |
| `500` | Internal Server Error | Retry with backoff |

---

## 10. Claim Status Codes & Categories

### statusCode (top-level claim status record)

| statusCode | status | Meaning | Action |
|---|---|---|---|
| `"0"` | In Progress | Payer response pending | Poll again in 2s |
| `"1"` | Retrying | Payer timed out; Availity retrying | Poll again in 2–5s |
| `"4"` | Complete | Final response received | Extract data ✓ |
| `"R"` | Request Error | Payer or Availity rejected the request | Check `validationMessages` |
| `"E"` | Communication Error | Network/payer connectivity failure | Alert staff; escalate |

### ClaimStatusDetail.categoryCode (X12 277 Claim Status Categories)

| categoryCode | Meaning |
|---|---|
| `A1` | Acknowledgement / Received |
| `A2` | Acknowledgement / Accepted into Adjudication System |
| `A3` | Acknowledgement / Returned as Unprocessable Claim |
| `A4` | Acknowledgement / Not Found |
| `A5` | Acknowledgement / Split Claim |
| `A6` | Acknowledgement / Rejected for Missing/Invalid Information |
| `A7` | Acknowledgement / Rejected for Missing/Invalid 837 Loop/Segment/Element |
| `A8` | Acknowledgement / Rejected for Invalid Authorization |
| `F1` | Finalized / Payment — claim fully adjudicated and paid |
| `F2` | Finalized / Denial — claim denied |
| `F3` | Finalized / Revised — previously adjudicated claim revised |
| `F4` | Finalized / Forwarded to Additional Entity |
| `P1` | Pending / In Adjudication |
| `P2` | Pending / Payer Review |
| `P3` | Pending / Provider Requested Information |
| `P4` | Pending / Patient Requested Information |

### ClaimStatusDetail.statusCode (X12 277 Claim Status Codes — common)

| statusCode | Meaning |
|---|---|
| `1` | Processed as Primary |
| `2` | Processed as Secondary |
| `3` | Processed as Tertiary |
| `4` | Denied |
| `5` | Pended |
| `10` | Received by plan, but not yet processed |
| `13` | Under Investigation |
| `15` | Payment Initiated |
| `16` | Claim/Encounter not found |
| `19` | Pending — Information Requested |
| `20` | Accepted |
| `21` | Missing or Invalid Information |
| `22` | Forwarded to Correct Carrier |
| `25` | Claim/Encounter received, will be processed per contract |
| `97` | Claim forwarded to third party for determination |

---

## 11. Sample curl Calls

### 11.1 Basic Claim Status Search by Member ID and Date Range

```bash
# Step 1: Get token
TOKEN=$(curl -s -X POST "https://api.availity.com/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials\
      &client_id=${AVAILITY_CLIENT_ID}\
      &client_secret=${AVAILITY_CLIENT_SECRET}\
      &scope=healthcare-hipaa-transactions" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Step 2: Search claim statuses
# NOTE: X-HTTP-Method-Override: GET is REQUIRED
curl -i -X POST "https://api.availity.com/v1/claim-statuses" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "X-HTTP-Method-Override: GET" \
  -d "payer.id=00611\
      &subscriber.memberId=ABC987654321\
      &subscriber.lastName=DOE\
      &subscriber.firstName=JOHN\
      &providers.npi=1234567890\
      &fromDate=2025-01-01\
      &toDate=2025-03-01"
```

### 11.2 Search by Claim Number + Charge Amount

```bash
curl -X POST "https://api.availity.com/v1/claim-statuses" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "X-HTTP-Method-Override: GET" \
  -d "payer.id=BCBSF\
      &providers.npi=1234567890\
      &providers.taxId=123456789\
      &subscriber.memberId=XYZ111222333\
      &claimNumber=20250115ABC\
      &claimAmount=1250.00\
      &fromDate=2025-01-15\
      &toDate=2025-01-15"
```

### 11.3 Institutional Claim with Facility and Frequency Codes

```bash
curl -X POST "https://api.availity.com/v1/claim-statuses" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "X-HTTP-Method-Override: GET" \
  -d "payer.id=MEDICARE\
      &providers.npi=9876543210\
      &subscriber.memberId=1EG4TE5MK72\
      &patient.lastName=SMITH\
      &patient.firstName=MARY\
      &patient.birthDate=1942-03-15\
      &patient.genderCode=F\
      &patient.subscriberRelationshipCode=18\
      &fromDate=2025-02-01\
      &toDate=2025-02-28\
      &facilityTypeCode=11\
      &frequencyTypeCode=1"
```

### 11.4 Poll for Full Claim Status Detail

```bash
# id comes from ResultSet.claimStatuses[n].id in the POST response
CLAIM_STATUS_ID="9384729100283746192"

curl -X GET "https://api.availity.com/v1/claim-statuses/${CLAIM_STATUS_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

### 11.5 Delete a Claim Status Record

```bash
curl -X DELETE "https://api.availity.com/v1/claim-statuses/${CLAIM_STATUS_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
# Returns HTTP 200 OK on success
```

### 11.6 Demo Sandbox — Simulated Responses

```bash
# Simulate a complete, finalized claim response
curl -X POST "https://api.availity.com/v1/claim-statuses" \
  -H "Authorization: Bearer ${DEMO_TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "X-HTTP-Method-Override: GET" \
  -H "X-Api-Mock-Scenario-ID: ClaimStatuses-Complete-i" \
  -H "X-Api-Mock-Response: true" \
  -d "payer.id=00611\
      &subscriber.memberId=SUCC123456789\
      &providers.npi=1234567890\
      &fromDate=2025-01-01\
      &toDate=2025-03-01"

# Simulate denied claim
curl -X POST "https://api.availity.com/v1/claim-statuses" \
  -H "Authorization: Bearer ${DEMO_TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "X-HTTP-Method-Override: GET" \
  -H "X-Api-Mock-Scenario-ID: ClaimStatuses-Denied-i" \
  -H "X-Api-Mock-Response: true" \
  -d "payer.id=00611\
      &subscriber.memberId=SUCC123456789\
      &providers.npi=1234567890\
      &fromDate=2025-01-01\
      &toDate=2025-03-01"
```

---

## 12. Sample Python Integration

### 12.1 Complete Polling Client

```python
# app/services/availity_claim_status.py
import asyncio
import httpx
from typing import Optional


class AvailityClaimStatusClient:

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

    # ──────────────────────────────────────────────────────────────
    # POST /claim-statuses — search
    # ──────────────────────────────────────────────────────────────
    async def search_claim_statuses(self, **params) -> dict:
        """
        Search for claim statuses.
        IMPORTANT: Always sends X-HTTP-Method-Override: GET.
        Returns ResultSet with claimStatuses[] array.
        """
        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v1/claim-statuses",
                data=params,
                headers={
                    "Authorization":       f"Bearer {token}",
                    "Content-Type":        "application/x-www-form-urlencoded",
                    "Accept":              "application/json",
                    "X-HTTP-Method-Override": "GET",  # REQUIRED
                },
            )
            resp.raise_for_status()
            return resp.json()

    # ──────────────────────────────────────────────────────────────
    # GET /claim-statuses/{id} — poll
    # ──────────────────────────────────────────────────────────────
    async def get_claim_status(self, claim_status_id: str) -> dict:
        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/v1/claim-statuses/{claim_status_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept":        "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    # ──────────────────────────────────────────────────────────────
    # DELETE /claim-statuses/{id}
    # ──────────────────────────────────────────────────────────────
    async def delete_claim_status(self, claim_status_id: str) -> bool:
        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.base_url}/v1/claim-statuses/{claim_status_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            return resp.status_code == 200

    # ──────────────────────────────────────────────────────────────
    # Poll a single claim status ID until complete
    # ──────────────────────────────────────────────────────────────
    async def poll_until_complete(
        self,
        claim_status_id: str,
        max_polls: int = 15,
        poll_interval_s: float = 2.0,
    ) -> dict:
        """
        Poll GET /claim-statuses/{id} until statusCode == "4" (Complete)
        or a terminal error state is reached.
        """
        TERMINAL_CODES = {"4", "R", "E"}

        for attempt in range(max_polls):
            result = await self.get_claim_status(claim_status_id)
            status_code = result.get("statusCode", "")

            if status_code in TERMINAL_CODES:
                return result

            await asyncio.sleep(poll_interval_s)

        raise TimeoutError(
            f"Claim status {claim_status_id} did not complete after {max_polls} polls"
        )

    # ──────────────────────────────────────────────────────────────
    # Full workflow: search → poll all results → return complete records
    # ──────────────────────────────────────────────────────────────
    async def get_full_claim_statuses(
        self,
        payer_id: str,
        provider_npi: str,
        subscriber_member_id: str,
        from_date: str,       # YYYY-MM-DD
        to_date: str,         # YYYY-MM-DD
        subscriber_last_name: Optional[str] = None,
        claim_number: Optional[str] = None,
        claim_amount: Optional[str] = None,
        facility_type_code: Optional[str] = None,
        frequency_type_code: Optional[str] = None,
    ) -> list[dict]:
        """
        Full workflow:
          1. POST /claim-statuses to get a ResultSet
          2. For each ClaimStatusSummary, poll GET /claim-statuses/{id}
          3. Return list of fully resolved ClaimStatus objects
        """
        # Build search params — only include non-None values
        params = {
            "payer.id":           payer_id,
            "providers.npi":      provider_npi,
            "subscriber.memberId": subscriber_member_id,
            "fromDate":           from_date,
            "toDate":             to_date,
        }
        if subscriber_last_name:
            params["subscriber.lastName"] = subscriber_last_name
        if claim_number:
            params["claimNumber"] = claim_number
        if claim_amount:
            params["claimAmount"] = claim_amount
        if facility_type_code:
            params["facilityTypeCode"] = facility_type_code
        if frequency_type_code:
            params["frequencyTypeCode"] = frequency_type_code

        # 1. Search
        result_set = await self.search_claim_statuses(**params)
        summaries  = result_set.get("claimStatuses", [])

        if not summaries:
            return []

        # 2. Poll each summary record concurrently
        tasks = [
            self.poll_until_complete(summary["id"])
            for summary in summaries
            if summary.get("id")
        ]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        # 3. Filter out errors; return completed records
        return [
            r for r in completed
            if isinstance(r, dict) and r.get("statusCode") == "4"
        ]
```

### 12.2 Adjudication Extraction Utilities

```python
# app/services/claim_status_parser.py

def extract_claim_summary(claim_status: dict) -> dict:
    """
    Extract top-level claim status fields for PMS display or logging.
    """
    payer      = claim_status.get("payer", {})
    subscriber = claim_status.get("subscriber", {})
    patient    = claim_status.get("patient", {})
    providers  = claim_status.get("providers", [{}])
    provider   = providers[0] if providers else {}

    return {
        "id":            claim_status.get("id"),
        "statusCode":    claim_status.get("statusCode"),
        "status":        claim_status.get("status"),
        "controlNumber": claim_status.get("controlNumber"),
        "claimNumber":   claim_status.get("claimNumber"),
        "claimAmount":   claim_status.get("claimAmount"),
        "claimCount":    claim_status.get("claimCount"),
        "fromDate":      claim_status.get("fromDate"),
        "toDate":        claim_status.get("toDate"),
        "expirationDate": claim_status.get("expirationDate"),
        # ── Payer ──────────────────────────────────────
        "payerId":       payer.get("id"),
        "payerName":     payer.get("name"),
        "payerPhone":    payer.get("phone"),
        "checkNumber":   None,  # extracted from statusDetails below
        # ── Subscriber ─────────────────────────────────
        "memberId":      subscriber.get("memberId"),
        "subLastName":   subscriber.get("lastName"),
        "subFirstName":  subscriber.get("firstName"),
        # ── Patient ────────────────────────────────────
        "patLastName":   patient.get("lastName"),
        "patFirstName":  patient.get("firstName"),
        "patDOB":        patient.get("birthDate"),
        "patAcctNum":    patient.get("accountNumber"),
        # ── Provider ───────────────────────────────────
        "providerNpi":   provider.get("npi"),
        "providerTaxId": provider.get("taxId"),
    }


def extract_adjudication(claim_status: dict) -> list[dict]:
    """
    Flatten all adjudication detail from a complete ClaimStatus into
    a list of records suitable for PMS updates or dashboard display.
    Traverses: ClaimStatus → ClaimStatusResult → ClaimStatusDetail
               and ClaimStatusResult → ServiceLine → ClaimStatusDetail
    """
    rows = []

    for claim_result in claim_status.get("claimStatuses", []):
        claim_ctrl   = claim_result.get("claimControlNumber")
        claim_trace  = claim_result.get("claimIdentificationNumber")
        from_dt      = claim_result.get("fromDate")
        to_dt        = claim_result.get("toDate")

        # ── Claim-level status details ──────────────────
        for detail in claim_result.get("statusDetails", []):
            rows.append({
                "level":             "claim",
                "claimControlNumber": claim_ctrl,
                "claimTraceNumber":  claim_trace,
                "fromDate":          from_dt,
                "toDate":            to_dt,
                "procedureCode":     None,
                "modifier":          None,
                "chargeAmount":      detail.get("claimAmount"),
                "paymentAmount":     detail.get("paymentAmount"),
                "checkNumber":       detail.get("checkNumber"),
                "remittanceDate":    detail.get("remittanceDate"),
                "finalizedDate":     detail.get("finalizedDate"),
                "categoryCode":      detail.get("categoryCode"),
                "category":          detail.get("category"),
                "statusCode":        detail.get("statusCode"),
                "status":            detail.get("status"),
                "entityCode":        detail.get("entityCode"),
                "entity":            detail.get("entity"),
            })

        # ── Service line–level status details ───────────
        for svc in claim_result.get("serviceLines", []):
            procedure = svc.get("procedureCode")
            modifier  = svc.get("modifier1Code")
            charge    = svc.get("chargeAmount")
            paid      = svc.get("paymentAmount")
            svc_from  = svc.get("fromDate")
            svc_to    = svc.get("toDate")

            for detail in svc.get("statusDetails", []):
                rows.append({
                    "level":             "service_line",
                    "claimControlNumber": claim_ctrl,
                    "claimTraceNumber":  claim_trace,
                    "fromDate":          svc_from,
                    "toDate":            svc_to,
                    "procedureCode":     procedure,
                    "modifier":          modifier,
                    "chargeAmount":      charge,
                    "paymentAmount":     paid,
                    "checkNumber":       detail.get("checkNumber"),
                    "remittanceDate":    detail.get("remittanceDate"),
                    "finalizedDate":     detail.get("finalizedDate"),
                    "categoryCode":      detail.get("categoryCode"),
                    "category":          detail.get("category"),
                    "statusCode":        detail.get("statusCode"),
                    "status":            detail.get("status"),
                    "entityCode":        detail.get("entityCode"),
                    "entity":            detail.get("entity"),
                })

    return rows


def is_denied(claim_status: dict) -> bool:
    """True if any claim-level status detail has a denial category (F2) or status code 4."""
    for claim_result in claim_status.get("claimStatuses", []):
        for detail in claim_result.get("statusDetails", []):
            if detail.get("categoryCode") == "F2" or detail.get("statusCode") == "4":
                return True
    return False


def is_paid(claim_status: dict) -> bool:
    """True if any claim-level status detail has a finalized payment category (F1)."""
    for claim_result in claim_status.get("claimStatuses", []):
        for detail in claim_result.get("statusDetails", []):
            if detail.get("categoryCode") == "F1":
                return True
    return False


def get_check_numbers(claim_status: dict) -> list[str]:
    """Extract all check or EFT trace numbers across all status details."""
    checks = set()
    for claim_result in claim_status.get("claimStatuses", []):
        for detail in claim_result.get("statusDetails", []):
            if detail.get("checkNumber"):
                checks.add(detail["checkNumber"])
    return list(checks)
```

### 12.3 Usage Example

```python
import asyncio
import os

client = AvailityClaimStatusClient(
    client_id     = os.environ["AVAILITY_CLIENT_ID"],
    client_secret = os.environ["AVAILITY_CLIENT_SECRET"],
)

async def main():
    # Full claim status workflow
    statuses = await client.get_full_claim_statuses(
        payer_id             = "BCBSF",
        provider_npi         = "1234567890",
        subscriber_member_id = "XYZ987654321",
        from_date            = "2025-01-01",
        to_date              = "2025-03-31",
        claim_number         = "20250115ABC",
    )

    for cs in statuses:
        summary = extract_claim_summary(cs)
        adj     = extract_adjudication(cs)

        print(f"Claim: {summary['claimNumber']} | {summary['status']}")
        print(f"Paid: {is_paid(cs)} | Denied: {is_denied(cs)}")
        print(f"Checks: {get_check_numbers(cs)}")

        for row in adj:
            level = row["level"].upper()
            cpt   = row.get("procedureCode") or "claim-level"
            print(f"  [{level}] {cpt}: {row['category']} — paid ${row['paymentAmount']}")

asyncio.run(main())
```

---

## 13. Key Differences from Coverages API

| Aspect | Coverages API | Claim Statuses API |
|---|---|---|
| **X12 Transaction** | 270/271 (Eligibility) | 276/277 (Claim Status) |
| **POST behavior** | Standard POST (creates new inquiry) | POST with `X-HTTP-Method-Override: GET` (search/query) |
| **POST response model** | `CoverageSummary` | `ResultSet` (array of `ClaimStatusSummary`) |
| **GET response model** | `Coverage` | `ClaimStatus` |
| **Result cardinality** | One coverage record per POST | One or more claim status records per POST |
| **Benefit data** | Deep: deductibles, co-pays, service limits | Not applicable |
| **Adjudication data** | Not present | Deep: paid amounts, check numbers, denial codes, per service line |
| **DELETE response** | 204 No Content | 200 OK |
| **Primary use** | Pre-service eligibility verification | Post-service claim follow-up, AR management |
| **Chained to** | E&B Value-Add APIs (Care Reminders, Member ID Card) | ERA/835 reconciliation, denial management |

---

## 14. PMS Integration Patterns

### Pattern 1 — Automated Claim Follow-Up (AR Aging)

Trigger nightly for claims aged 14+ days with no ERA received:

```python
async def nightly_claim_follow_up(unpaid_claims: list[dict]):
    """
    For each unpaid claim, query Availity claim status.
    Update PMS based on adjudication result.
    """
    for claim in unpaid_claims:
        statuses = await client.get_full_claim_statuses(
            payer_id             = claim["payerId"],
            provider_npi         = claim["providerNpi"],
            subscriber_member_id = claim["memberId"],
            from_date            = claim["serviceDate"],
            to_date              = claim["serviceDate"],
            claim_number         = claim.get("claimNumber"),
            claim_amount         = str(claim["chargeAmount"]),
        )

        for cs in statuses:
            if is_paid(cs):
                checks = get_check_numbers(cs)
                # → Update PMS: mark paid, store check/EFT numbers
                await pms.mark_claim_paid(claim["id"], checks)
            elif is_denied(cs):
                denial_details = [
                    r for r in extract_adjudication(cs)
                    if r["categoryCode"] == "F2"
                ]
                # → Update PMS: flag for denial management workflow
                await pms.flag_claim_denied(claim["id"], denial_details)
            else:
                # Still pending — leave in AR queue
                pass
```

### Pattern 2 — Real-Time Claim Status on Staff Request

```python
async def on_demand_claim_status(
    claim_id: str,
    payer_id: str,
    member_id: str,
    npi: str,
    service_date: str,
) -> dict:
    """
    Called when staff clicks 'Check Status' in the PMS UI.
    Returns a display-ready summary.
    """
    statuses = await client.get_full_claim_statuses(
        payer_id             = payer_id,
        provider_npi         = npi,
        subscriber_member_id = member_id,
        from_date            = service_date,
        to_date              = service_date,
    )

    if not statuses:
        return {"status": "not_found", "message": "No claims found for this date"}

    cs = statuses[0]
    return {
        "status":        cs.get("status"),
        "isPaid":        is_paid(cs),
        "isDenied":      is_denied(cs),
        "checkNumbers":  get_check_numbers(cs),
        "adjudication":  extract_adjudication(cs),
        "payerContact":  cs.get("payer", {}).get("phone"),
        "expiresAt":     cs.get("expirationDate"),
    }
```

### Pattern 3 — Batch Status Refresh (Concurrent)

```python
async def batch_status_refresh(claim_batch: list[dict]) -> list[dict]:
    """
    Fan out claim status requests concurrently across a batch.
    Respects 5 req/s Demo rate limit via semaphore.
    """
    sem = asyncio.Semaphore(5)  # max 5 concurrent requests

    async def check_one(claim):
        async with sem:
            try:
                return await client.get_full_claim_statuses(
                    payer_id             = claim["payerId"],
                    provider_npi         = claim["npi"],
                    subscriber_member_id = claim["memberId"],
                    from_date            = claim["fromDate"],
                    to_date              = claim["toDate"],
                )
            except Exception as e:
                return []

    results = await asyncio.gather(*[check_one(c) for c in claim_batch])
    return [r for batch in results for r in batch]  # flatten
```

---

*Source: Availity Claim Statuses 1.0.0 Swagger Specification (claims-statuses-document.json) · Swagger 2.0 · Host: api.availity.com · BasePath: /v1*
