# Availity Coverages API 1.0.0 — Developer Reference
**Experiment 47 · PMS Integration · MPS Inc.**  
Source: Availity Coverages Swagger Spec (document.json)  
Last Updated: March 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Base URLs & Endpoints Summary](#3-base-urls--endpoints-summary)
4. [Async Polling Pattern](#4-async-polling-pattern)
5. [POST /coverages — Initiate Eligibility Request](#5-post-coverages--initiate-eligibility-request)
6. [GET /coverages/{id} — Poll for Full Coverage](#6-get-coveragesid--poll-for-full-coverage)
7. [DELETE /coverages/{id} — Delete a Coverage](#7-delete-coveragesid--delete-a-coverage)
8. [Response Models](#8-response-models)
   - [CoverageSummary](#81-coveragesummary-post-202-response)
   - [Coverage (Full)](#82-coverage-full-get-200-response)
   - [Benefit & BenefitDetail](#83-benefit--benefitdetail)
   - [NetworkBenefit](#84-networkbenefit)
   - [Payer](#85-payer)
   - [HealthCareContact](#86-healthcarecontact)
   - [ErrorResponse](#87-errorresponse)
9. [HTTP Status Code Reference](#9-http-status-code-reference)
10. [Coverage Status Codes](#10-coverage-status-codes)
11. [Sample curl Calls](#11-sample-curl-calls)
12. [Sample Python Integration](#12-sample-python-integration)
13. [Key Fields for E&B Value-Add Chaining](#13-key-fields-for-eb-value-add-chaining)
14. [Demo Sandbox Scenarios](#14-demo-sandbox-scenarios)

---

## 1. Overview

The **Availity Coverages 1.0.0 API** supports real-time eligibility and benefits inquiries in compliance with HIPAA standards, implementing the X12 270/271 transaction pair.

**Key behaviors:**
- `POST /coverages` initiates the request and may return a `202 Accepted` (async) or `200 OK` (cached)
- Poll `GET /coverages/{id}` until `statusCode` reaches `"4"` (Complete)
- The full benefit detail (deductibles, co-pays, plan info, etc.) is returned only from `GET /coverages/{id}` — the POST response is a lightweight `CoverageSummary`
- Availity caches coverage results until `expirationDate`; repeat requests for the same member may return a cached `200 OK` immediately

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
| `rcm-coverages` | RCM add-on |
| `rcm-coverages-standard` | RCM Standard |

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

> Token TTL = **5 minutes**. Cache with 4.5-minute effective TTL. Every token call counts against your rate limit (500/day on Demo plan).

---

## 3. Base URLs & Endpoints Summary

| Environment | Base URL |
|---|---|
| Production | `https://api.availity.com/v1` |
| QUA / Sandbox | `https://qua.api.availity.com/v1` |
| Test | `https://tst.api.availity.com/v1` |

| Method | Path | Operation | Description |
|---|---|---|---|
| `POST` | `/coverages` | `createCoverage` | Initiate eligibility request or retrieve cached result |
| `GET` | `/coverages/{id}` | `getCoverageById` | Poll for full coverage detail by coverage ID |
| `DELETE` | `/coverages/{id}` | `deleteCoverageById` | Delete a coverage record by ID |

---

## 4. Async Polling Pattern

The Coverages API is asynchronous. Follow this pattern in all integrations:

```
POST /coverages
  → 202 Accepted  (in progress)  ─┐
  → 200 OK        (cached hit)    │ extract id from response
                                  │
  GET /coverages/{id}  ←──────────┘
  → statusCode = "0"  → wait 2s, poll again
  → statusCode = "1"  → payer timeout, Availity retrying, poll again
  → statusCode = "4"  → Complete ✓ — extract member/benefit data
  → statusCode = "R"  → Request Error — stop, inspect validationMessages
  → statusCode = "E"  → Communication Error — stop
```

> **Polling interval:** 2 seconds between polls. Do not hammer — Demo plan is limited to 5 req/s / 500 req/day.

---

## 5. POST /coverages — Initiate Eligibility Request

**`POST https://api.availity.com/v1/coverages`**

- **Content-Type:** `application/x-www-form-urlencoded`
- **Accept:** `application/json` or `application/xml`
- **Auth:** Bearer token with `healthcare-hipaa-transactions` scope

### Request Parameters

All parameters are form-data (URL-encoded). All are optional per the spec, but payer-specific required fields are enforced at submission — use the Configurations API to look them up first.

#### Provider / Submitter Parameters

| Parameter | Type | Description |
|---|---|---|
| `payerId` | string | Availity payer ID of the member's health plan |
| `providerLastName` | string | Requesting provider's last or business name |
| `providerFirstName` | string | Requesting provider's first name |
| `providerType` | string | Provider type (e.g., professional, institutional) |
| `providerNpi` | string | Requesting provider's NPI (10 digits, starts with 1–4) |
| `providerTaxId` | string | Requesting provider's tax ID (9 digits, no dashes) |
| `payerAssignedProviderId` | string | Payer-assigned provider ID |
| `providerSSN` | string | Provider's Social Security Number |
| `providerPIN` | string | Provider's personal identification number |
| `medicaidProviderNumber` | string | Medicaid-assigned provider ID |
| `providerOfficeId` | string | Provider's internal system provider ID |
| `providerUserId` | string | Provider's internal system user ID |
| `contractNumber` | string | Provider contract number (CMS NPI mandate use only) |
| `providerCity` | string | Requesting provider's city |
| `providerState` | string | Requesting provider's two-character state code |
| `providerZipCode` | string | Requesting provider's ZIP code |
| `providerSpecialty` | string | Provider specialty taxonomy code |
| `placeOfService` | string | Place of service code |
| `submitterId` | string | Payer-assigned submitter ID |

#### Coverage / Request Parameters

| Parameter | Type | Format | Description |
|---|---|---|---|
| `asOfDate` | string | date-time | Date of service for coverage check |
| `toDate` | string | date-time | End date for coverage search period |
| `cardIssueDate` | string | date-time | Issue date of the member's health plan card |
| `serviceType` | string | | Service type code(s) being checked (e.g., `30` = Health Benefit Plan Coverage) |
| `procedureCode` | string | | Procedure code(s) being checked |

#### Patient / Member Identification Parameters

| Parameter | Type | Format | Description |
|---|---|---|---|
| `memberId` | string | | Member ID of the patient or subscriber ← **primary identifier** |
| `patientSSN` | string | | Patient or subscriber Social Security Number |
| `medicaidId` | string | | Patient or subscriber Medicaid ID |
| `medicalRecordIdentificationNumber` | string | | Patient's medical record ID number |
| `patientAccountNumber` | string | | Patient's account number |
| `identificationCardSerialNumber` | string | | Card serial number (when multiple cards issued to a member) |
| `identityCardNumber` | string | | Identity card number (when different from member ID) |
| `insurancePolicyNumber` | string | | Patient's insurance policy number |
| `planNetworkIdentificationNumber` | string | | Patient's plan network ID |
| `agencyClaimNumber` | string | | Property & Casualty claim number (P&C payers only) |
| `patientLastName` | string | | Patient's last name |
| `patientFirstName` | string | | Patient's first name |
| `patientMiddleName` | string | | Patient's middle name |
| `patientSuffix` | string | | Patient's suffix |
| `patientBirthDate` | string | date-time | Patient's date of birth |
| `patientGender` | string | | Patient's gender |
| `patientState` | string | | Patient's state of residence (two-character code) |
| `patientZipCode` | string | | Patient's ZIP code |
| `groupNumber` | string | | Patient's group number |
| `groupOrPolicyNumber` | string | | Use when group vs. policy number cannot be determined |
| `planNumber` | string | | Patient's plan number |
| `healthInsuranceClaimNumber` | string | | Patient's HIC (Medicare) number |
| `subscriberRelationship` | string | | Patient's relationship to subscriber (`18`=Self, `01`=Spouse, `19`=Child, `G8`=Other) |
| `caseNumber` | string | | Case number assigned by the information source |

### Responses

| HTTP Code | Description | Schema |
|---|---|---|
| `200 OK` | Cached result returned immediately | `CoverageSummary` |
| `202 Accepted` | Request in progress — poll `GET /coverages/{id}` | `CoverageSummary` |
| `400 Bad Request` | Validation failure | `ErrorResponse` |
| `401 Unauthorized` | Invalid or missing token | `ErrorResponse` |
| `403 Forbidden` | Insufficient scope | `ErrorResponse` |
| `500 Internal Server Error` | Server error | `ErrorResponse` |

---

## 6. GET /coverages/{id} — Poll for Full Coverage

**`GET https://api.availity.com/v1/coverages/{id}`**

- **Accept:** `application/json` or `application/xml`
- **Auth:** Bearer token

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | ✅ Yes | Coverage ID from the POST response (`CoverageSummary.id`) |

### Responses

| HTTP Code | Description | Schema |
|---|---|---|
| `200 OK` | Full coverage detail | `Coverage` |
| `401 Unauthorized` | Invalid or missing token | `ErrorResponse` |
| `403 Forbidden` | Insufficient scope | `ErrorResponse` |
| `404 Not Found` | Coverage ID not found or expired | `ErrorResponse` |
| `500 Internal Server Error` | Server error | `ErrorResponse` |

> Returns the **full `Coverage` model** (not the summary) — includes complete benefit details, plan info, deductibles, co-pays, supplemental information, and care reminders.

---

## 7. DELETE /coverages/{id} — Delete a Coverage

**`DELETE https://api.availity.com/v1/coverages/{id}`**

Deletes a locally cached coverage record. Used for cleanup or when patient data should not persist.

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | ✅ Yes | Coverage ID from the POST response |

### Responses

| HTTP Code | Description |
|---|---|
| `204 No Content` | Deleted successfully — no body returned |
| `401 Unauthorized` | Invalid or missing token |
| `403 Forbidden` | Insufficient scope |
| `404 Not Found` | Coverage ID not found |
| `500 Internal Server Error` | Server error |

---

## 8. Response Models

### 8.1 CoverageSummary (POST 200/202 Response)

Lightweight summary returned from `POST /coverages`. Use `id` to poll `GET /coverages/{id}`.

| Field | Type | Description |
|---|---|---|
| `id` | string | **Coverage ID — use this for GET/DELETE polling** |
| `status` | string | Current status: `"In Progress"`, `"Complete"`, `"Request Error"`, `"Communication Error"` |
| `statusCode` | string | Status code: `"0"` (In Progress), `"1"` (Retrying), `"4"` (Complete), `"R"` (Request Error), `"E"` (Comm Error) |
| `customerId` | string | Customer ID that owns this coverage |
| `controlNumber` | string | Tracking number assigned to the transaction |
| `createdDate` | date-time | When this coverage was added to the system |
| `updatedDate` | date-time | When this coverage was last updated |
| `expirationDate` | date-time | When this cached result expires |
| `asOfDate` | date-time | The as-of date for the coverage check |
| `toDate` | date-time | The to date |
| `cardIssueDate` | date-time | Card issue date |
| `submitterStatecode` | string | Submitter's configured state code |
| `subscriber` | object | Subscriber (see below) |
| `patient` | object | Patient (see below) |
| `payer` | object | Payer info (name, payerId, responseName, responsePayerId) |
| `plans[]` | array | Array of plan summaries |
| `requestingProvider` | object | Requesting provider |
| `requestedServiceType[]` | array | Requested service types (`code`, `value`) |
| `procedureCode[]` | array | Requested procedure codes |
| `validationMessages[]` | array | Validation errors from payer (`FieldError`) |

#### CoverageSummary.subscriber

| Field | Type | Description |
|---|---|---|
| `memberId` | string | **Subscriber member ID ← key for E&B Value-Add APIs** |
| `firstName` | string | Subscriber's first name |
| `lastName` | string | Subscriber's last name |
| `middleName` | string | Subscriber's middle name |
| `suffix` | string | Subscriber's suffix |
| `birthDate` | date-time | Subscriber's date of birth |
| `gender` | string | Subscriber's gender |
| `genderCode` | string | Subscriber's gender code |
| `medicaidId` | string | Subscriber's Medicaid ID |
| `ssn` | string | Subscriber's SSN |
| `caseNumber` | string | Subscriber's case number |

#### CoverageSummary.patient

| Field | Type | Description |
|---|---|---|
| `memberId` | string | Patient's member ID (if different from subscriber) |
| `firstName` | string | Patient's first name |
| `lastName` | string | Patient's last name |
| `middleName` | string | Patient's middle name |
| `suffix` | string | Patient's suffix |
| `birthDate` | date-time | Patient's date of birth |
| `gender` | string | Patient's gender |
| `genderCode` | string | Patient's gender code |
| `ssn` | string | Patient's SSN |
| `subscriberRelationship` | string | Relationship to subscriber |
| `subscriberRelationshipCode` | string | Relationship code |
| `address.state` | string | Patient's state |
| `address.stateCode` | string | Patient's state code |

#### CoverageSummary.payer

| Field | Type | Description |
|---|---|---|
| `name` | string | Requested payer name |
| `payerId` | string | Requested payer ID (what you sent) |
| `responseName` | string | Name the payer responded with |
| `responsePayerId` | string | Payer ID the payer responded with (may differ — use this for value-add APIs) |

#### CoverageSummary.plans[] (summary)

| Field | Type | Description |
|---|---|---|
| `status` | string | Plan status: `"Active"`, `"Inactive"` |
| `statusCode` | string | Plan status code |
| `groupName` | string | Plan group name |
| `groupNumber` | string | Plan group number |
| `coverageStartDate` | date-time | Coverage start date |
| `coverageEndDate` | date-time | Coverage end date |
| `eligibilityStartDate` | date-time | Eligibility start date |
| `eligibilityEndDate` | date-time | Eligibility end date |
| `insuranceType` | string | Type of insurance |
| `insuranceTypeCode` | string | Insurance type code |
| `identityCardNumber` | string | Identity card number |
| `description` | string | Plan description |
| `primaryCareProvider` | object | PCP name, category, categoryCode |
| `coverageSummaryAdditionalPayers[]` | array | COB payers (primary/secondary/tertiary flags) |

---

### 8.2 Coverage (Full — GET /coverages/{id} Response)

The full `Coverage` model returned from the polling GET. Contains everything in `CoverageSummary` plus full benefit detail.

**Additional fields beyond CoverageSummary:**

| Field | Type | Description |
|---|---|---|
| `plans[].benefits[]` | array | Array of `Benefit` objects — full benefit detail per service type |
| `plans[].amounts` | object | `Amounts` — deductible, co-pay, co-insurance, out-of-pocket |
| `plans[].payerNotes[]` | array | General payer notes and disclaimers |
| `plans[].contacts[]` | array | Contacts associated with this plan |
| `plans[].primaryCareProvider` | object | `HealthCareContact` — full PCP detail |
| `plans[].coverageBasis` | object | `BenefitDetail` |
| `plans[].costContainment` | object | `BenefitDetail` |
| `plans[].limitations` | object | `BenefitDetail` |
| `plans[].preexistingConditions` | object | `BenefitDetail` |
| `plans[].reserve` | object | `BenefitDetail` |
| `plans[].policyNumber` | string | Policy number |
| `plans[].contractNumber` | string | Contract number |
| `plans[].planName` | string | Plan name |
| `plans[].planNumber` | string | Plan number |
| `plans[].planNetworkId` | string | Network ID |
| `plans[].planNetworkName` | string | Network name |
| `plans[].planEnrollmentDate` | date-time | Enrollment date |
| `plans[].planStartDate` / `planEndDate` | date-time | Plan start/end dates |
| `plans[].policyEffectiveDate` / `policyExpirationDate` | date-time | Policy effective/expiration dates |
| `plans[].premiumPaidToBeginDate` / `premiumPaidToEndDate` | date-time | Premium paid date range |
| `plans[].cobraStartDate` / `cobraEndDate` | date-time | COBRA dates |
| `plans[].medicalRecordNumber` | string | Medical record number |
| `plans[].healthInsuranceClaimNumber` | string | HIC (Medicare) number |
| `patient.memberId` | string | Patient's member ID |
| `patient.updateYourRecords` | boolean | Payer signals you should update demographic info |
| `patient.familyUnitNumber` | string | Family unit number |
| `reminders` | object | Care reminders (inference, messages, titles) |
| `supplementalInformation` | object | Extended flags (PCP cost estimator, C-SNP, maternity, referral, etc.) |

---

### 8.3 Benefit & BenefitDetail

Each entry in `plans[].benefits[]` represents coverage for a specific service type.

#### Benefit

| Field | Type | Description |
|---|---|---|
| `name` | string | Benefit name (e.g., "Professional (Physician) Visit - Office") |
| `type` | string | Benefit type |
| `status` | string | Coverage status for this benefit |
| `statusCode` | string | Coverage status code |
| `source` | string | Source of the procedure benefit |
| `amounts` | object | `Amounts` — co-pay, deductible, co-insurance, out-of-pocket for this benefit |
| `benefitDescriptions` | object | `BenefitDetail` |
| `costContainment` | object | `BenefitDetail` |
| `coverageBasis` | object | `BenefitDetail` |
| `exclusions` | object | `BenefitDetail` |
| `limitations` | object | `BenefitDetail` |
| `nonCovered` | object | `BenefitDetail` |
| `preexistingConditions` | object | `BenefitDetail` |
| `reserve` | object | `BenefitDetail` |
| `statusDetails` | object | `BenefitDetail` |
| `additionalPayers[]` | array | Additional `Payer` objects |
| `contacts[]` | array | `HealthCareContact` objects |
| `payerNotes[]` | array | `PayerNote` objects |

#### BenefitDetail

Each `BenefitDetail` object segments benefit data by network tier. All four fields hold arrays of `NetworkBenefit`.

| Field | Description |
|---|---|
| `inNetwork[]` | Benefits applying to in-network providers |
| `outOfNetwork[]` | Benefits applying to out-of-network providers |
| `notApplicableNetwork[]` | Benefits applying regardless of network |
| `noNetwork[]` | Benefits not specific to a network |

#### Amounts

| Field | Type | Description |
|---|---|---|
| `deductibles` | BenefitDetail | Deductible amounts by network tier |
| `coPayment` | BenefitDetail | Co-payment amounts by network tier |
| `coInsurance` | BenefitDetail | Co-insurance amounts by network tier |
| `outOfPocket` | BenefitDetail | Out-of-pocket maximum by network tier |

---

### 8.4 NetworkBenefit

The atomic unit of benefit data. Found in all `BenefitDetail` arrays.

| Field | Type | Description |
|---|---|---|
| `amount` | string | Dollar amount |
| `total` | string | Total benefit amount |
| `remaining` | string | Remaining benefit amount |
| `quantity` | string | Quantity covered |
| `quantityQualifier` | string | Type of service (e.g., visits, days) |
| `quantityQualifierCode` | string | Qualifier code |
| `level` | string | Coverage level (e.g., Individual, Family) |
| `levelCode` | string | Level code |
| `status` | string | Benefit status |
| `statusCode` | string | Benefit status code |
| `description` | string | Human-readable benefit description |
| `amountTimePeriod` | string | Time period (e.g., Calendar Year) |
| `amountTimePeriodCode` | string | Time period code |
| `remainingTimePeriod` | string | Time period for remaining amount |
| `totalTimePeriod` | string | Time period for total amount |
| `units` | string | Units (e.g., dollar, percent) |
| `authorizationRequired` | boolean | Whether auth is required for this service |
| `authorizationRequiredUnknown` | boolean | Whether auth requirement is unknown |
| `coverageStartDate` / `coverageEndDate` | date-time | Benefit coverage dates |
| `eligibilityStartDate` / `eligibilityEndDate` | date-time | Eligibility dates |
| `benefitBeginDate` / `benefitEndDate` | date-time | Benefit period dates |
| `planName` | string | Plan name |
| `planNumber` | string | Plan number |
| `planNetworkId` | string | Network ID |
| `planNetworkName` | string | Network name |
| `groupName` / `groupNumber` | string | Group name/number |
| `policyNumber` | string | Policy number |
| `priorAuthorizationNumber` | string | Prior auth number |
| `referralNumber` | string | Referral number |
| `healthInsuranceClaimNumber` | string | HIC number |
| `memberIdentificationNumber` | string | Member ID |
| `insuranceType` / `insuranceTypeCode` | string | Insurance type |
| `placeOfService` / `placeOfServiceCode` | string | Place of service |
| `serviceDate` | date-time | Service date |
| `deliveryInformation[]` | array | `HealthCareServiceDelivery` — frequency/delivery details |
| `contacts[]` | array | `ContactInformation` |
| `payerNotes[]` | array | Free-form notes from payer |

---

### 8.5 Payer

Used within `Coverage` for both the primary payer and `additionalPayers` (COB).

| Field | Type | Description |
|---|---|---|
| `name` | string | Payer name |
| `payerId` | string | Payer ID |
| `responseName` | string | Name payer responded with |
| `responsePayerId` | string | ID payer responded with |
| `primary` | boolean | Is this the primary payer? |
| `secondary` | boolean | Is this the secondary payer? |
| `tertiary` | boolean | Is this the tertiary payer? |
| `thirdPartyAdministrator` | string | TPA indicator |
| `type` / `typeCode` | string | Payer type / code |
| `groupName` / `groupNumber` | string | Group name/number |
| `planName` / `planNumber` | string | Plan name/number |
| `planNetworkId` / `planNetworkName` | string | Network ID/name |
| `policyNumber` | string | Policy number |
| `insuredMemberId` | string | Insured person's member ID |
| `insuredFirstName` / `insuredLastName` | string | Insured person's name |
| `serviceTypeCode` | string | Service type associated with this payer |
| `coordinationOfBenefitsBeginDate` | date-time | COB begin date |
| `coordinationOfBenefitsEndDate` | date-time | COB end date |
| `coverageStartDate` / `coverageEndDate` | date-time | Coverage dates |
| `eligibilityStartDate` / `eligibilityEndDate` | date-time | Eligibility dates |
| `address` | object | `Address` |
| `contactInformation[]` | array | `ContactInformation` |

---

### 8.6 HealthCareContact

Rich contact model used for requesting provider, PCP, and other plan contacts.

Key fields:

| Field | Type | Description |
|---|---|---|
| `name` | string | Contact name |
| `firstName` / `lastName` | string | Contact first/last name |
| `npi` | string | Provider NPI |
| `taxId` | string | Tax ID |
| `memberId` | string | Member ID |
| `category` / `categoryCode` | string | Contact category |
| `type` / `typeCode` | string | Contact type |
| `role` / `roleCode` | string | Contact role |
| `specialty` / `specialtyCode` | string | Specialty |
| `authorizationRequired` | boolean | Whether auth is required |
| `priorAuthorizationNumber` | string | Prior auth number |
| `referralNumber` | string | Referral number |
| `planId` | string | CMMS plan ID |
| `planNetworkId` / `planNetworkName` | string | Network info |
| `address` | object | `Address` |
| `contactInformation[]` | array | `ContactInformation` (phone, fax, email, URL) |
| `deliveryInformation[]` | array | `HealthCareServiceDelivery` |

---

### 8.7 ErrorResponse

Returned for all 4xx / 5xx responses.

| Field | Type | Description |
|---|---|---|
| `userMessage` | string | High-level human-readable error message |
| `developerMessage` | string | Technical error detail |
| `statusCode` | integer | HTTP-equivalent status code |
| `reasonCode` | integer | Internal reason code |
| `errors[]` | array | Array of `FieldError` objects |

#### FieldError

| Field | Type | Description |
|---|---|---|
| `field` | string | The parameter or field that failed validation |
| `errorMessage` | string | Validation error message |
| `code` | string | Error code |
| `index` | integer | Array index (for repeated fields) |

---

## 9. HTTP Status Code Reference

| Code | Meaning | Action |
|---|---|---|
| `200` | OK — immediate result (cached) | Process `CoverageSummary` or `Coverage` |
| `202` | Accepted — async in progress | Poll `GET /coverages/{id}` |
| `204` | No Content — DELETE successful | Done |
| `400` | Bad Request — validation failure | Check `ErrorResponse.errors[]` for field details |
| `401` | Unauthorized | Refresh token |
| `403` | Forbidden — scope insufficient | Check OAuth scope |
| `404` | Not Found — coverage ID expired or invalid | Coverage has expired; submit new POST |
| `429` | Too Many Requests — rate limit hit | Wait 1s (per-second) or resume next day (daily) |
| `500` | Internal Server Error | Retry with backoff; contact Availity support |

---

## 10. Coverage Status Codes

| statusCode | status | Meaning | Action |
|---|---|---|---|
| `"0"` | In Progress | Payer response pending | Poll again in 2s |
| `"1"` | Retrying | Payer timed out; Availity retrying | Poll again in 2–5s |
| `"4"` | Complete | Final response received | Extract data ✓ |
| `"R"` | Request Error | Payer rejected the request | Check `validationMessages[]` |
| `"E"` | Communication Error | Network/payer connectivity failure | Alert staff; retry or escalate |

---

## 11. Sample curl Calls

### 11.1 Minimal Eligibility Request — Member ID Lookup

```bash
# Step 1: Get token
TOKEN=$(curl -s -X POST "https://api.availity.com/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials\
      &client_id=${AVAILITY_CLIENT_ID}\
      &client_secret=${AVAILITY_CLIENT_SECRET}\
      &scope=healthcare-hipaa-transactions" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Step 2: Submit eligibility request
curl -i -X POST "https://api.availity.com/v1/coverages" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -d "payerId=00611\
      &memberId=SUCC123456789\
      &patientLastName=TEST\
      &patientFirstName=PATIENTONE\
      &patientBirthDate=1900-01-01\
      &serviceType=30\
      &providerNpi=1234567890\
      &asOfDate=2025-01-01"
```

### 11.2 Full Request — With Provider Details and Service Type

```bash
curl -X POST "https://api.availity.com/v1/coverages" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -d "payerId=BCBSF\
      &providerNpi=1234567890\
      &providerTaxId=123456789\
      &providerLastName=SMITH\
      &providerFirstName=JOHN\
      &providerState=FL\
      &submitterId=123456789\
      &memberId=ABC987654321\
      &patientLastName=DOE\
      &patientFirstName=JANE\
      &patientBirthDate=1985-06-15\
      &patientGender=F\
      &subscriberRelationship=18\
      &serviceType=30\
      &asOfDate=2025-03-01"
```

### 11.3 Poll for Full Coverage Detail

```bash
# id comes from the POST response body or Location header
COVERAGE_ID="7276849100383928590"

curl -X GET "https://api.availity.com/v1/coverages/${COVERAGE_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

### 11.4 Demo Sandbox — Force a Specific Scenario

```bash
# Force "Complete" response (statusCode 4)
curl -X POST "https://api.availity.com/v1/coverages" \
  -H "Authorization: Bearer ${DEMO_TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "X-Api-Mock-Scenario-ID: Coverages-Complete-i" \
  -H "X-Api-Mock-Response: true" \
  -d "payerId=00611\
      &memberId=SUCC123456789\
      &patientLastName=TEST\
      &patientFirstName=PATIENTONE\
      &patientBirthDate=1900-01-01\
      &serviceType=30\
      &providerNpi=1234567890"

# Force "Payer Error" response
curl -X POST "https://api.availity.com/v1/coverages" \
  -H "Authorization: Bearer ${DEMO_TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -H "X-Api-Mock-Scenario-ID: Coverages-PayerError1-i" \
  -H "X-Api-Mock-Response: true" \
  -d "{}"
```

### 11.5 Delete a Coverage Record

```bash
curl -X DELETE "https://api.availity.com/v1/coverages/${COVERAGE_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
# Returns HTTP 204 No Content on success
```

### 11.6 Search Existing Coverages (POST with q parameter)

```bash
curl -X POST "https://api.availity.com/v1/coverages" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Accept: application/json" \
  -d "q=DOE\
      &status=Complete\
      &sortBy=lastUpdateDate\
      &sortDirection=desc"
```

---

## 12. Sample Python Integration

### 12.1 Complete Polling Flow

```python
# app/services/availity_api.py
import asyncio
import httpx
from typing import Optional


class AvailityClient:

    def __init__(self, client_id: str, client_secret: str,
                 base_url: str = "https://api.availity.com",
                 scope: str = "healthcare-hipaa-transactions"):
        self.client_id     = client_id
        self.client_secret = client_secret
        self.base_url      = base_url
        self.scope         = scope
        self._token: Optional[str] = None

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
    # POST /coverages — initiate
    # ──────────────────────────────────────────────────────────────
    async def create_coverage(self, **params) -> dict:
        """
        Initiate an eligibility request.
        Returns CoverageSummary (202 in-progress or 200 cached).
        """
        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v1/coverages",
                data=params,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type":  "application/x-www-form-urlencoded",
                    "Accept":        "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    # ──────────────────────────────────────────────────────────────
    # GET /coverages/{id} — poll
    # ──────────────────────────────────────────────────────────────
    async def get_coverage(self, coverage_id: str) -> dict:
        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/v1/coverages/{coverage_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept":        "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    # ──────────────────────────────────────────────────────────────
    # DELETE /coverages/{id}
    # ──────────────────────────────────────────────────────────────
    async def delete_coverage(self, coverage_id: str) -> bool:
        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.base_url}/v1/coverages/{coverage_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            return resp.status_code == 204

    # ──────────────────────────────────────────────────────────────
    # Poll until complete
    # ──────────────────────────────────────────────────────────────
    async def poll_coverage_until_complete(
        self,
        coverage_id: str,
        max_polls: int = 15,
        poll_interval_s: float = 2.0,
    ) -> dict:
        """
        Poll GET /coverages/{id} until statusCode == "4" (Complete)
        or a terminal error state is reached.
        Raises TimeoutError if max_polls is exceeded.
        """
        TERMINAL_CODES = {"4", "R", "E"}

        for attempt in range(max_polls):
            result = await self.get_coverage(coverage_id)
            status_code = result.get("statusCode", "")

            if status_code in TERMINAL_CODES:
                return result

            await asyncio.sleep(poll_interval_s)

        raise TimeoutError(
            f"Coverage {coverage_id} did not complete after {max_polls} polls"
        )

    # ──────────────────────────────────────────────────────────────
    # Full eligibility workflow
    # ──────────────────────────────────────────────────────────────
    async def check_eligibility(
        self,
        payer_id: str,
        member_id: str,
        patient_last_name: str,
        patient_first_name: str,
        patient_birth_date: str,   # YYYY-MM-DD
        provider_npi: str,
        service_type: str = "30",  # 30 = Health Benefit Plan Coverage
        as_of_date: Optional[str] = None,
    ) -> dict:
        """
        Full eligibility workflow: POST → poll → return complete Coverage.
        """
        # 1. Submit
        summary = await self.create_coverage(
            payerId           = payer_id,
            memberId          = member_id,
            patientLastName   = patient_last_name,
            patientFirstName  = patient_first_name,
            patientBirthDate  = patient_birth_date,
            providerNpi       = provider_npi,
            serviceType       = service_type,
            **({"asOfDate": as_of_date} if as_of_date else {}),
        )

        coverage_id  = summary["id"]
        status_code  = summary.get("statusCode", "0")

        # 2. If already complete (cached hit), fetch full detail
        if status_code == "4":
            return await self.get_coverage(coverage_id)

        # 3. Poll until complete
        return await self.poll_coverage_until_complete(coverage_id)
```

### 12.2 Extract Member Details for E&B Value-Add Chaining

```python
def extract_member_details(coverage: dict) -> dict:
    """
    Extract fields needed to call Care Reminders and Member ID Card APIs.
    Works on both CoverageSummary and full Coverage responses.
    """
    if coverage.get("statusCode") != "4":
        return {}  # not complete

    subscriber = coverage.get("subscriber", {})
    patient    = coverage.get("patient", {})
    payer      = coverage.get("payer", {})
    plans      = coverage.get("plans", [{}])
    plan       = plans[0] if plans else {}

    # Use responsePayerId from payer response — may differ from requested payerId
    effective_payer_id = (
        payer.get("responsePayerId") or payer.get("payerId")
    )

    return {
        # ── Identifiers ───────────────────────────────────
        "memberId":        subscriber.get("memberId") or patient.get("memberId"),
        "payerId":         effective_payer_id,
        # ── Subscriber demographics ───────────────────────
        "firstName":       subscriber.get("firstName"),
        "lastName":        subscriber.get("lastName"),
        "dateOfBirth":     subscriber.get("birthDate", "")[:10],  # strip time
        "groupNumber":     plan.get("groupNumber"),
        # ── Patient (if different from subscriber) ────────
        "patientMemberId": patient.get("memberId"),
        # ── Plan status ───────────────────────────────────
        "planStatus":      plan.get("status"),
        "planStatusCode":  plan.get("statusCode"),
        "coverageStart":   plan.get("coverageStartDate"),
        "coverageEnd":     plan.get("coverageEndDate"),
        # ── Payer metadata ────────────────────────────────
        "payerName":       payer.get("name"),
        "responsePayerId": payer.get("responsePayerId"),
    }


def extract_benefit_amounts(coverage: dict, benefit_name: str = None) -> list:
    """
    Extract deductible, co-pay, co-insurance and out-of-pocket amounts
    from the full Coverage response. Optionally filter by benefit name.
    """
    results = []
    for plan in coverage.get("plans", []):
        for benefit in plan.get("benefits", []):
            if benefit_name and benefit_name.lower() not in benefit.get("name", "").lower():
                continue

            amounts = benefit.get("amounts", {})
            for amount_type, detail in amounts.items():
                if not detail:
                    continue
                for network_tier, items in detail.items():
                    for item in (items or []):
                        results.append({
                            "benefitName":  benefit.get("name"),
                            "amountType":   amount_type,        # deductibles, coPayment, etc.
                            "networkTier":  network_tier,       # inNetwork, outOfNetwork, etc.
                            "amount":       item.get("amount"),
                            "total":        item.get("total"),
                            "remaining":    item.get("remaining"),
                            "timePeriod":   item.get("amountTimePeriod"),
                            "level":        item.get("level"),  # Individual, Family
                            "authRequired": item.get("authorizationRequired"),
                        })
    return results
```

### 12.3 Usage Example

```python
import asyncio
import os

client = AvailityClient(
    client_id     = os.environ["AVAILITY_CLIENT_ID"],
    client_secret = os.environ["AVAILITY_CLIENT_SECRET"],
)

async def main():
    # Full eligibility check
    coverage = await client.check_eligibility(
        payer_id          = "BCBSF",
        member_id         = "ABC987654321",
        patient_last_name = "DOE",
        patient_first_name= "JANE",
        patient_birth_date= "1985-06-15",
        provider_npi      = "1234567890",
        service_type      = "30",
        as_of_date        = "2025-03-01",
    )

    # Extract for value-add chaining
    member = extract_member_details(coverage)
    print(f"Member ID: {member['memberId']}")
    print(f"Payer ID:  {member['payerId']}")
    print(f"Status:    {member['planStatus']}")

    # Extract benefit amounts
    amounts = extract_benefit_amounts(coverage)
    for a in amounts[:5]:
        print(f"{a['benefitName']} | {a['amountType']} | {a['networkTier']}: ${a['amount']}")

asyncio.run(main())
```

---

## 13. Key Fields for E&B Value-Add Chaining

After a successful eligibility check (`statusCode == "4"`), these fields from the Coverage response feed directly into Care Reminders and Member ID Card API calls:

| Coverage Field | JSON Path | Maps To (Value-Add API param) |
|---|---|---|
| Subscriber member ID | `subscriber.memberId` | `memberId` |
| Patient member ID (if dep.) | `patient.memberId` | `memberId` |
| Response payer ID | `payer.responsePayerId` | `payerId` (use response, not request) |
| Subscriber first name | `subscriber.firstName` | `firstName` |
| Subscriber last name | `subscriber.lastName` | `lastName` |
| Subscriber DOB | `subscriber.birthDate` | `dateOfBirth` |
| Group number | `plans[0].groupNumber` | `groupNumber` |
| Plan network ID | `plans[0].planNetworkId` | *(contextual)* |
| Control number | `controlNumber` | `controlNumber` (Care Reminders optional) |

> **Always prefer `payer.responsePayerId` over `payer.payerId`** — the payer sometimes responds with a different ID, and the value-add APIs require the payer's own identifier.

---

## 14. Demo Sandbox Scenarios

Use the `X-Api-Mock-Scenario-ID` header to select a canned response in the Demo environment. Pass any valid request body (or `{}` for POST).

| Scenario ID | HTTP Status | statusCode | Description |
|---|---|---|---|
| `Coverages-Complete-i` | 200 | `"4"` | Success — full coverage returned immediately |
| `Coverages-InProgress-i` | 202 | `"0"` | Simulate async in-progress (use to test polling) |
| `Coverages-Retrying-i` | 202 | `"1"` | Simulate payer timeout / retry |
| `Coverages-PayerError1-i` | 200 | varies | Payer says provider ineligible for inquiries |
| `Coverages-PayerError2-i` | 200 | varies | Payer says subscriber name is invalid |
| `Coverages-RequestError1-i` | 400 | — | Availity input validation failure |
| `Coverages-RequestError2-i` | 400 | — | Availity input validation failure (alternate) |

### Simulate Full Async Polling Flow in Demo

```bash
# 1. Submit — force in-progress (202)
curl -X POST "https://api.availity.com/v1/coverages" \
  -H "Authorization: Bearer ${DEMO_TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-Api-Mock-Scenario-ID: Coverages-InProgress-i" \
  -H "X-Api-Mock-Response: true" \
  -d "payerId=00611&memberId=SUCC123456789&serviceType=30&providerNpi=1234567890"

# 2. Poll — force complete (200, statusCode=4)
curl -X GET "https://api.availity.com/v1/coverages/{id}" \
  -H "Authorization: Bearer ${DEMO_TOKEN}" \
  -H "X-Api-Mock-Scenario-ID: Coverages-Complete-i" \
  -H "X-Api-Mock-Response: true"
```

> **Note:** The full scenario ID list for `GET /coverages/{id}` is only visible inside the developer portal after login. The table above reflects all publicly documented POST scenarios.

---

*Source: Availity Coverages 1.0.0 Swagger Specification (document.json) · Swagger 2.0 · Host: api.availity.com · BasePath: /v1*
