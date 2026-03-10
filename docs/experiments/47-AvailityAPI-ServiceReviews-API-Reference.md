# Availity Service Reviews API 2.0.0 — Developer Reference
**Experiment 47 · PMS Integration · MPS Inc.**  
Source: Availity Service Reviews Swagger Spec (healthcare-hipaa-transactions-document.json)  
Last Updated: March 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Base URLs & Endpoints Summary](#3-base-urls--endpoints-summary)
4. [Request Lifecycle & State Machine](#4-request-lifecycle--state-machine)
5. [GET /service-reviews — Search Existing Reviews](#5-get-service-reviews--search-existing-reviews)
6. [POST /service-reviews — Submit New Authorization Request](#6-post-service-reviews--submit-new-authorization-request)
7. [PUT /service-reviews — Update an Existing Request](#7-put-service-reviews--update-an-existing-request)
8. [GET /service-reviews/{id} — Retrieve by ID](#8-get-service-reviewsid--retrieve-by-id)
9. [DELETE /service-reviews/{id} — Void a Request](#9-delete-service-reviewsid--void-a-request)
10. [ServiceReview Body Model (POST / PUT)](#10-servicereview-body-model-post--put)
11. [Supporting Models](#11-supporting-models)
    - [RequestingProvider](#111-requestingprovider)
    - [RenderingProvider](#112-renderingprovider)
    - [Subscriber](#113-subscriber)
    - [Patient](#114-patient)
    - [Payer](#115-payer)
    - [Procedures](#116-procedures)
    - [Diagnosis](#117-diagnosis)
    - [SupplementalInformation](#118-supplementalinformation)
    - [TransportLocation](#119-transportlocation)
    - [Note](#1110-note)
12. [Response Models](#12-response-models)
    - [ResultSet (GET /service-reviews)](#121-resultset-get-service-reviews-response)
    - [ServiceReview (GET /service-reviews/{id})](#122-servicereview-get-service-reviewsid-response)
    - [ErrorResponse](#123-errorresponse)
13. [HTTP Status Code Reference](#13-http-status-code-reference)
14. [Service Review Status Codes](#14-service-review-status-codes)
15. [Request Type Codes](#15-request-type-codes)
16. [Sample curl Calls](#16-sample-curl-calls)
17. [Sample Python Integration](#17-sample-python-integration)
18. [Key Differences from Coverages & Claim Statuses APIs](#18-key-differences-from-coverages--claim-statuses-apis)
19. [PMS Integration Patterns](#19-pms-integration-patterns)

---

## 1. Overview

The **Availity Service Reviews 2.0.0 API** facilitates healthcare service authorization and referral requests, implementing the **ASC X12N 278** transaction — the HIPAA standard for prior authorization (PA).

**Key behaviors:**

- `GET /service-reviews` — searches existing reviews (query parameters, not a body)
- `POST /service-reviews` — submits a **new** prior authorization or referral request (JSON body)
- `PUT /service-reviews` — updates an **existing** request (JSON body, must include `id`)
- `GET /service-reviews/{id}` — retrieves a specific review by ID; poll until status is terminal
- `DELETE /service-reviews/{id}` — voids a review; returns `202 Accepted` (async void)
- Base path is `/v2` — **different from Coverages and Claim Statuses which use `/v1`**
- POST/PUT accept and produce JSON or XML; GET produces JSON or XML
- All responses are async (`202 Accepted`) until the payer responds

---

## 2. Authentication

**Scheme:** OAuth 2.0 Client Credentials (`application` flow)  
**Token URL:** `https://api.availity.com/v1/token`

> Note: Token URL remains `/v1/token` even though the API itself is at `/v2`.

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

> Token TTL = **5 minutes**. Cache with 4.5-minute effective TTL.

---

## 3. Base URLs & Endpoints Summary

| Environment | Base URL |
|---|---|
| Production | `https://api.availity.com/v2` |
| QUA / Sandbox | `https://qua.api.availity.com/v2` |
| Test | `https://tst.api.availity.com/v2` |

| Method | Path | Operation | Description |
|---|---|---|---|
| `GET` | `/service-reviews` | `findServiceReviews` | Search existing service reviews by query parameters |
| `POST` | `/service-reviews` | `createServiceReview` | Submit a new prior authorization / referral request |
| `PUT` | `/service-reviews` | `updateServiceReview` | Update an existing service review |
| `GET` | `/service-reviews/{id}` | `getServiceReviewById` | Retrieve a specific service review by ID; used for polling |
| `DELETE` | `/service-reviews/{id}` | `voidServiceReview` | Void (cancel) an existing service review |

---

## 4. Request Lifecycle & State Machine

Service reviews follow an async lifecycle. Poll `GET /service-reviews/{id}` after submission.

```
POST /service-reviews  (new auth request)
  → 202 Accepted  → extract id from Location header or response body

PUT /service-reviews   (update existing)
  → 202 Accepted

DELETE /service-reviews/{id}  (void request)
  → 202 Accepted (async void initiated)
  → 204 No Content (void complete, synchronous path)

GET /service-reviews/{id}  (poll)
  → statusCode = "A1" / "A3"  → Approved ✓ — extract certificationNumber
  → statusCode = "A4" / "A6"  → Denied — record denial reason, alert staff
  → statusCode = "WR"         → Pended — attach docs, staff action needed
  → statusCode = "CA"         → Cancelled — log
  → statusCode = "P1"         → Pending — poll again in 2–5s
  → statusCode = "VO"         → Voided — void confirmed
```

**`updatable` and `deletable` flags** on the `ServiceReview` object indicate whether the current state allows updates or voids. Always check these before attempting `PUT` or `DELETE`.

---

## 5. GET /service-reviews — Search Existing Reviews

**`GET https://api.availity.com/v2/service-reviews`**

- **Accept:** `application/json` or `application/xml`
- **Auth:** Bearer token
- All parameters are query string parameters

### Query Parameters

#### Payer

| Parameter | Type | Description |
|---|---|---|
| `payer.id` | string | Availity payer ID |

#### Requesting Provider

| Parameter | Type | Description |
|---|---|---|
| `requestingProvider.npi` | string | Requesting provider NPI |
| `requestingProvider.taxId` | string | Requesting provider tax ID |
| `requestingProvider.lastName` | string | Provider last or business name |
| `requestingProvider.firstName` | string | Provider first name |
| `requestingProvider.middleName` | string | Provider middle name |
| `requestingProvider.suffix` | string | Provider suffix |
| `requestingProvider.specialtyCode` | string | Provider specialty code |
| `requestingProvider.payerAssignedProviderId` | string | Payer-assigned provider ID |
| `requestingProvider.submitterId` | string | Provider submitter ID |
| `requestingProvider.addressLine1` | string | Provider street address line 1 |
| `requestingProvider.addressLine2` | string | Provider street address line 2 |
| `requestingProvider.city` | string | Provider city |
| `requestingProvider.stateCode` | string | Provider two-character state code |
| `requestingProvider.zipCode` | string | Provider ZIP code |
| `requestingProvider.contactName` | string | Provider contact name |
| `requestingProvider.phone` | string | Provider phone number |
| `requestingProvider.extension` | string | Provider phone extension |
| `requestingProvider.fax` | string | Provider fax number |

#### Subscriber

| Parameter | Type | Description |
|---|---|---|
| `subscriber.memberId` | string | Subscriber health plan member ID |
| `subscriber.lastName` | string | Subscriber last name |
| `subscriber.firstName` | string | Subscriber first name |
| `subscriber.middleName` | string | Subscriber middle name |
| `subscriber.suffix` | string | Subscriber suffix |

#### Patient

| Parameter | Type | Format | Description |
|---|---|---|---|
| `patient.lastName` | string | | Patient last name |
| `patient.firstName` | string | | Patient first name |
| `patient.middleName` | string | | Patient middle name |
| `patient.suffix` | string | | Patient suffix |
| `patient.birthDate` | string | date | Patient date of birth (`YYYY-MM-DD`) |
| `patient.subscriberRelationshipCode` | string | | Patient's relationship to subscriber |

#### Review / Authorization Filters

| Parameter | Type | Format | Description |
|---|---|---|---|
| `requestTypeCode` | string | | Request type code (see Section 15) |
| `fromDate` | string | date | Service from date (`YYYY-MM-DD`) |
| `toDate` | string | date | Service to date (`YYYY-MM-DD`) |
| `certificationIssueDate` | string | date | Date the certification was issued |
| `certificationNumber` | string | | Authorization / certification number |
| `referenceNumber` | string | | Reference number |
| `statusCode` | string | | Filter by review status code |
| `sessionId` | string | | Session ID |

### Responses

| HTTP Code | Description | Schema |
|---|---|---|
| `200 OK` | Results returned | `ResultSet` |
| `202 Accepted` | In progress — poll individual IDs | `ResultSet` |
| `400 Bad Request` | Validation failure | `ErrorResponse` |
| `401 Unauthorized` | Invalid or missing token | `ErrorResponse` |
| `403 Forbidden` | Insufficient scope | `ErrorResponse` |
| `500 Internal Server Error` | Server error | `ErrorResponse` |

---

## 6. POST /service-reviews — Submit New Authorization Request

**`POST https://api.availity.com/v2/service-reviews`**

- **Content-Type:** `application/json` or `application/xml`
- **Accept:** `application/json` or `application/xml`
- **Auth:** Bearer token
- **Body:** `ServiceReview` object (see Section 10)

### Responses

| HTTP Code | Description | Notes |
|---|---|---|
| `202 Accepted` | Request submitted and queued for payer | Poll `GET /service-reviews/{id}` to get status |
| `400 Bad Request` | Validation failure | `ErrorResponse` |
| `401 Unauthorized` | Invalid or missing token | `ErrorResponse` |
| `403 Forbidden` | Insufficient scope | `ErrorResponse` |
| `500 Internal Server Error` | Server error | `ErrorResponse` |

> The `202` response does **not** include a body schema in the spec. Retrieve the review ID from the `Location` response header (e.g., `Location: /v2/service-reviews/{id}`) or by querying `GET /service-reviews` filtered by your submission parameters.

---

## 7. PUT /service-reviews — Update an Existing Request

**`PUT https://api.availity.com/v2/service-reviews`**

- **Content-Type:** `application/json` or `application/xml`
- **Accept:** `application/json` or `application/xml`
- **Auth:** Bearer token
- **Body:** `ServiceReview` object with `id` populated

### Pre-Conditions

Before calling PUT, confirm the review allows updates:
- `serviceReview.updatable == true`
- `serviceReview.updatableFields[]` — lists which specific fields may be changed

### Responses

| HTTP Code | Description | Notes |
|---|---|---|
| `202 Accepted` | Update accepted | Poll `GET /service-reviews/{id}` |
| `400 Bad Request` | Validation failure | `ErrorResponse` |
| `401 Unauthorized` | Invalid or missing token | `ErrorResponse` |
| `403 Forbidden` | Insufficient scope | `ErrorResponse` |
| `500 Internal Server Error` | Server error | `ErrorResponse` |

---

## 8. GET /service-reviews/{id} — Retrieve by ID

**`GET https://api.availity.com/v2/service-reviews/{id}`**

- **Accept:** `application/json` or `application/xml`
- **Auth:** Bearer token
- Primary polling endpoint after POST or PUT

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | ✅ Yes | Service review ID |

### Responses

| HTTP Code | Description | Schema |
|---|---|---|
| `200 OK` | Review found and returned | `ServiceReview` |
| `202 Accepted` | Still processing — keep polling | no body |
| `400 Bad Request` | Validation failure | `ErrorResponse` |
| `401 Unauthorized` | Invalid or missing token | `ErrorResponse` |
| `403 Forbidden` | Insufficient scope | `ErrorResponse` |
| `404 Not Found` | Review not found or expired | `ErrorResponse` |
| `500 Internal Server Error` | Server error | `ErrorResponse` |

---

## 9. DELETE /service-reviews/{id} — Void a Request

**`DELETE https://api.availity.com/v2/service-reviews/{id}`**

- **Auth:** Bearer token
- Voids (cancels) a service review. Only allowed when `deletable == true`.

### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | string | ✅ Yes | Service review ID to void |

### Responses

| HTTP Code | Description |
|---|---|
| `202 Accepted` | Void request accepted — async processing |
| `204 No Content` | Void complete (synchronous path) |
| `400 Bad Request` | Validation failure or review not voidable |
| `401 Unauthorized` | Invalid or missing token |
| `403 Forbidden` | Insufficient scope |
| `404 Not Found` | Review not found |
| `500 Internal Server Error` | Server error |

---

## 10. ServiceReview Body Model (POST / PUT)

The `ServiceReview` object is the primary request/response body for POST, PUT, and GET by ID.

### Core Fields

| Field | Type | Format | Description |
|---|---|---|---|
| `id` | string | | Service review ID — **required for PUT**, absent for POST |
| `requestTypeCode` | string | | Request type: `"AR"`=Auth Request, `"HS"`=Health Services Review, `"SC"`=Service Certification, `"SS"`=Specialist Referral (see Section 15) |
| `requestType` | string | | Human-readable request type |
| `serviceTypeCode` | string | | Service type code (X12 service type, e.g., `"MH"`=Mental Health, `"SU"`=Substance Abuse) |
| `serviceType` | string | | Human-readable service type |
| `serviceLevelCode` | string | | Service level code (e.g., `"E"`=Emergency, `"U"`=Urgent, `"R"`=Routine) |
| `serviceLevel` | string | | Human-readable service level |
| `placeOfServiceCode` | string | | Place of service code (e.g., `"11"`=Office, `"21"`=Inpatient, `"22"`=Outpatient) |
| `placeOfService` | string | | Human-readable place of service |
| `fromDate` | string | date | Service start date (`YYYY-MM-DD`) |
| `toDate` | string | date | Service end date (`YYYY-MM-DD`) |
| `quantity` | string | | Quantity of the service |
| `quantityTypeCode` | string | | Unit code for quantity (e.g., `"VS"`=Visits, `"DA"`=Days, `"UN"`=Units) |
| `quantityType` | string | | Human-readable quantity type |
| `referenceNumber` | string | | Reference number |
| `shortFormIndicator` | boolean | | Indicates this is a short-form request |

### Authorization / Certification Fields

| Field | Type | Format | Description |
|---|---|---|---|
| `certificationNumber` | string | | Authorization / certification number (assigned by payer) |
| `certificationIssueDate` | string | date | Date the authorization was issued |
| `certificationEffectiveDate` | string | date | Date the authorization became effective |
| `certificationExpirationDate` | string | date | Date the authorization expires |
| `controlNumber` | string | | Control number of the X12 request |
| `traceNumbers[]` | array of string | | Trace numbers added by the payer |

### Status Fields (Response — do not send in POST)

| Field | Type | Description |
|---|---|---|
| `status` | string | Current status of the review |
| `statusCode` | string | Status code (see Section 14) |
| `statusReasons[]` | array | Status reasons (payer-supplied) |
| `updatable` | boolean | Whether this review can be updated via PUT |
| `updatableFields[]` | array of string | List of field names that can be updated |
| `deletable` | boolean | Whether this review can be voided via DELETE |
| `validationMessages[]` | array of `FieldError` | Validation messages |

### Administrative Fields (Response)

| Field | Type | Description |
|---|---|---|
| `customerId` | string | Availity customer ID |
| `userId` | string | User ID that created the review |
| `createdDate` | date-time | When this record was created |
| `updatedDate` | date-time | When this record was last updated |
| `expirationDate` | date-time | When this cached result expires |

### Notes Fields

| Field | Type | Description |
|---|---|---|
| `payerNotes[]` | array of `Note` | Notes and disclaimers from the payer |
| `providerNotes[]` | array of `Note` | Notes from the provider |

### Specialty Service Fields (include only when applicable)

#### Chiropractic

| Field | Type | Description |
|---|---|---|
| `beginningSubluxationLevel` | string | Beginning subluxation level description |
| `beginningSubluxationLevelCode` | string | Beginning subluxation level code |
| `endingSubluxationLevel` | string | Ending subluxation level description |
| `endingSubluxationLevelCode` | string | Ending subluxation level code |
| `spinalCondition` | string | Spinal condition description |
| `spinalConditionCode` | string | Spinal condition code |
| `spinalConditionDescription` | string | Narrative spinal condition description |
| `chiropracticTreatmentCount` | string | Number of chiropractic treatments |

#### Institutional / Inpatient

| Field | Type | Description |
|---|---|---|
| `admissionTypeCode` | string | Admission type code (e.g., `"1"`=Emergency, `"2"`=Urgent, `"3"`=Elective) |
| `admissionType` | string | Human-readable admission type |
| `admissionSourceCode` | string | Admission source code |
| `admissionSource` | string | Human-readable admission source |

#### Home Health

| Field | Type | Description |
|---|---|---|
| `homeHealthStartDate` | string (date) | Home health service start date |
| `homeHealthCertificationPeriodStartDate` | string (date) | Certification period start |
| `homeHealthCertificationPeriodEndDate` | string (date) | Certification period end |

#### Nursing Home

| Field | Type | Description |
|---|---|---|
| `nursingHomeResidentialStatusCode` | string | Residential status code |
| `nursingHomeResidentialStatus` | string | Residential status description |

#### Oxygen / DME

| Field | Type | Description |
|---|---|---|
| `oxygenEquipmentTypeCode` | string | Equipment type code |
| `oxygenEquipmentType` | string | Equipment type description |
| `oxygenDeliverySystemTypeCode` | string | Delivery system type code |
| `oxygenDeliverySystemType` | string | Delivery system type description |
| `oxygenFlowRate` | string | Flow rate |
| `oxygenDailyUseCount` | string | Daily use count (hours per day) |
| `oxygenUsePeriodHourCount` | string | Total use period hours |
| `oxygenOrderText` | string | Oxygen order free text |

#### Transport

| Field | Type | Description |
|---|---|---|
| `transportTypeCode` | string | Transport type code |
| `transportType` | string | Transport type description |
| `transportPurpose` | string | Transport purpose |
| `transportDistance` | string | Distance of medically related transport |
| `transportLocations[]` | array of `TransportLocation` | Origin and destination locations |

#### Additional Service Types

| Field | Type | Description |
|---|---|---|
| `additionalServiceTypes[]` | array of object | Additional service types beyond primary |

### Linked Object Fields

| Field | Type | Description |
|---|---|---|
| `payer` | `Payer` | Payer information (see Section 11.5) |
| `requestingProvider` | `RequestingProvider` | Provider submitting the request (see Section 11.1) |
| `renderingProviders[]` | array of `RenderingProvider` | Providers who will perform the service (see Section 11.2) |
| `subscriber` | `Subscriber` | Policy holder (see Section 11.3) |
| `patient` | `Patient` | Patient receiving the service (see Section 11.4) |
| `diagnoses[]` | array of `Diagnosis` | Supporting diagnoses (see Section 11.7) |
| `procedures[]` | array of `Procedures` | Requested procedures (see Section 11.6) |
| `supplementalInformation` | `SupplementalInformation` | Update context for PUT requests (see Section 11.8) |

---

## 11. Supporting Models

### 11.1 RequestingProvider

The provider submitting the authorization request.

| Field | Type | Description |
|---|---|---|
| `npi` | string | Provider NPI (required by most payers) |
| `taxId` | string | Provider tax ID |
| `lastName` | string | Last name or organization name |
| `firstName` | string | First name (individual providers) |
| `middleName` | string | Middle name |
| `suffix` | string | Suffix |
| `specialtyCode` | string | Specialty taxonomy code |
| `specialty` | string | Specialty description |
| `payerAssignedProviderId` | string | Payer-assigned provider ID |
| `submitterId` | string | Payer-assigned submitter reference number |
| `addressLine1` | string | Street address line 1 |
| `addressLine2` | string | Street address line 2 |
| `city` | string | City |
| `stateCode` | string | Two-character state code |
| `zipCode` | string | ZIP code |
| `state` | string | State name |
| `contactName` | string | Contact name |
| `phone` | string | Phone number |
| `extension` | string | Phone extension |
| `fax` | string | Fax number |
| `emailAddress` | string | Email address |
| `url` | string | Website URL |

---

### 11.2 RenderingProvider

The provider(s) who will actually perform the requested service. Multiple rendering providers can be listed.

| Field | Type | Description |
|---|---|---|
| `npi` | string | Provider NPI |
| `taxId` | string | Provider tax ID |
| `lastName` | string | Last name or organization name |
| `firstName` | string | First name |
| `middleName` | string | Middle name |
| `suffix` | string | Suffix |
| `specialtyCode` | string | Specialty taxonomy code |
| `specialty` | string | Specialty description |
| `roleCode` | string | Provider role code |
| `role` | string | Provider role description |
| `payerAssignedProviderId` | string | Payer-assigned provider ID |
| `addressLine1` | string | Street address line 1 |
| `addressLine2` | string | Street address line 2 |
| `city` | string | City |
| `stateCode` | string | Two-character state code |
| `state` | string | State name |
| `zipCode` | string | ZIP code |
| `contactName` | string | Contact name |
| `phone` | string | Phone number |
| `extension` | string | Phone extension |
| `fax` | string | Fax number |
| `emailAddress` | string | Email address |
| `url` | string | Website URL |

---

### 11.3 Subscriber

The policy holder (may be the same person as the patient).

| Field | Type | Description |
|---|---|---|
| `memberId` | string | Health plan member ID ← **primary identifier** |
| `lastName` | string | Subscriber last name |
| `firstName` | string | Subscriber first name |
| `middleName` | string | Subscriber middle name |
| `suffix` | string | Subscriber suffix |
| `addressLine1` | string | Street address line 1 |
| `addressLine2` | string | Street address line 2 |
| `city` | string | City |
| `state` | string | State name |
| `stateCode` | string | Two-character state code |
| `zipCode` | string | ZIP code |

---

### 11.4 Patient

The patient receiving the service. Include when patient differs from subscriber.

| Field | Type | Format | Description |
|---|---|---|---|
| `lastName` | string | | Patient last name |
| `firstName` | string | | Patient first name |
| `middleName` | string | | Patient middle name |
| `suffix` | string | | Patient suffix |
| `birthDate` | string | date | Patient date of birth (`YYYY-MM-DD`) |
| `gender` | string | | Patient gender |
| `genderCode` | string | | Patient gender code (`M`, `F`, `U`) |
| `subscriberRelationshipCode` | string | | Relationship to subscriber (`18`=Self, `01`=Spouse, `19`=Child, `G8`=Other) |
| `subscriberRelationship` | string | | Relationship description |
| `addressLine1` | string | | Street address line 1 |
| `addressLine2` | string | | Street address line 2 |
| `city` | string | | City |
| `state` | string | | State name |
| `stateCode` | string | | Two-character state code |
| `zipCode` | string | | ZIP code |
| `conditionCode` | string | | Patient condition code |
| `condition` | string | | Patient condition description |
| `prognosisCode` | string | | Prognosis code |
| `prognosis` | string | | Prognosis description |
| `statusCode` | string | | Patient status code |
| `status` | string | | Patient status description |
| `medicareCoverage` | boolean | | Whether patient has Medicare coverage |

---

### 11.5 Payer

| Field | Type | Description |
|---|---|---|
| `id` | string | Availity payer ID ← **required** |
| `name` | string | Payer name |
| `contactName` | string | Payer contact name |
| `phone` | string | Payer phone number |
| `extension` | string | Phone extension |
| `fax` | string | Payer fax number |
| `emailAddress` | string | Payer email address |
| `url` | string | Payer website URL |

---

### 11.6 Procedures

Each procedure in the `procedures[]` array represents one service being requested.

| Field | Type | Format | Description |
|---|---|---|---|
| `code` | string | | Procedure code (CPT/HCPCS) |
| `qualifierCode` | string | | Procedure qualifier code (e.g., `"HC"`=HCPCS, `"AD"`=ADA) |
| `qualifier` | string | | Qualifier description |
| `value` | string | | Procedure value / description |
| `description` | string | | Procedure description |
| `quantity` | string | | Quantity requested |
| `quantityTypeCode` | string | | Quantity unit code (`"VS"`=Visits, `"DA"`=Days, `"UN"`=Units, `"ML"`=Milliliters) |
| `quantityType` | string | | Quantity type description |
| `modifierCode1` / `modifier1` | string | | First modifier code and description |
| `modifierCode2` / `modifier2` | string | | Second modifier code and description |
| `modifierCode3` / `modifier3` | string | | Third modifier code and description |
| `modifierCode4` / `modifier4` | string | | Fourth modifier code and description |
| `revenueCode` | string | | Revenue code (institutional claims) |
| `revenueValue` | string | | Revenue value (institutional claims) |
| `fromDate` | string | date | Procedure start date |
| `toDate` | string | date | Procedure end date |
| `statusCode` | string | | Procedure status code (payer response) |
| `status` | string | | Procedure status description |
| `statusReasons[]` | array | | Status reasons (payer response) |
| `certificationNumber` | string | | Authorization number for this procedure |
| `certificationIssueDate` | string | date | Authorization issue date |
| `certificationEffectiveDate` | string | date | Authorization effective date |
| `certificationExpirationDate` | string | date | Authorization expiration date |
| `traceNumbers[]` | array of string | | Trace numbers from payer |
| `notes[]` | array of `Note` | | Notes, disclaimers, and descriptions |

---

### 11.7 Diagnosis

| Field | Type | Format | Description |
|---|---|---|---|
| `code` | string | | Diagnosis code (ICD-10-CM) |
| `qualifierCode` | string | | Qualifier code (e.g., `"ABK"`=ICD-10-CM Principal, `"APR"`=ICD-10-CM Admitting) |
| `qualifier` | string | | Qualifier description |
| `value` | string | | Diagnosis description |
| `date` | string | date | Date diagnosis was reached |

---

### 11.8 SupplementalInformation

Used with PUT requests to provide update context. Carries the reference authorization/referral number and update sequencing.

| Field | Type | Description |
|---|---|---|
| `refAuthNumber` | string | Authorization or referral number being referenced |
| `sequence` | string | Sequence number for the update |
| `updateType` | string | Type of update being performed |
| `diagnoses[]` | array of `Diagnosis` | Updated diagnosis information |
| `procedures[]` | array of `Diagnosis` | Updated procedure information (uses Diagnosis schema) |

---

### 11.9 TransportLocation

Each entry in `transportLocations[]` defines an origin or destination for medical transport.

| Field | Type | Description |
|---|---|---|
| `name` | string | Name of the transport location |
| `addressLine1` | string | Street address line 1 |
| `addressLine2` | string | Street address line 2 |
| `city` | string | City |
| `state` | string | State name |
| `stateCode` | string | Two-character state code |
| `zipCode` | string | ZIP code |

---

### 11.10 Note

Used in `payerNotes[]` and `providerNotes[]`.

| Field | Type | Description |
|---|---|---|
| `message` | string | Note text or message |
| `typeCode` | string | Note type code |
| `type` | string | Note type description |

---

## 12. Response Models

### 12.1 ResultSet (GET /service-reviews Response)

| Field | Type | Description |
|---|---|---|
| `serviceReviews[]` | array of `ServiceReview` | Matching service review records |
| `count` | integer | Number of records in this page |
| `totalCount` | integer | Total matching records |
| `limit` | integer | Page size limit |
| `offset` | integer | Page offset |
| `links` | object | Pagination link URLs |

---

### 12.2 ServiceReview (GET /service-reviews/{id} Response)

The full `ServiceReview` object as documented in Section 10 above. After polling completes (`statusCode` is terminal), the key response fields to extract are:

| Field | Purpose |
|---|---|
| `statusCode` | Disposition — approved, denied, pended, cancelled |
| `certificationNumber` | Auth number — store in PMS; required for claim submission |
| `certificationEffectiveDate` | Auth validity start |
| `certificationExpirationDate` | Auth validity end |
| `procedures[n].statusCode` | Per-procedure disposition |
| `procedures[n].certificationNumber` | Per-procedure auth number (may differ from top-level) |
| `procedures[n].certificationExpirationDate` | Per-procedure expiration |
| `statusReasons[]` | Denial or pend reasons |
| `payerNotes[]` | Payer instructions or disclaimers |
| `updatable` / `deletable` | Whether subsequent PUT/DELETE is allowed |
| `traceNumbers[]` | Payer-assigned trace numbers for follow-up |

---

### 12.3 ErrorResponse

| Field | Type | Description |
|---|---|---|
| `userMessage` | string | High-level human-readable error message |
| `developerMessage` | string | Technical error detail |
| `statusCode` | integer | HTTP-equivalent status code |
| `reasonCode` | integer | Internal reason code |
| `errors[]` | array of `FieldError` | Per-field validation errors (`field`, `errorMessage`, `code`, `index`) |

---

## 13. HTTP Status Code Reference

| Code | Meaning | Action |
|---|---|---|
| `200` | OK — review found | Process `ServiceReview` or `ResultSet` |
| `202` | Accepted — async processing | Poll `GET /service-reviews/{id}` |
| `204` | No Content — void complete | Done (synchronous void path) |
| `400` | Bad Request | Check `ErrorResponse.errors[]` |
| `401` | Unauthorized | Refresh token |
| `403` | Forbidden — scope insufficient | Check OAuth scope |
| `404` | Not Found — expired or invalid ID | Resubmit or escalate |
| `500` | Internal Server Error | Retry with backoff |

---

## 14. Service Review Status Codes

### Top-Level statusCode (ServiceReview.statusCode)

| statusCode | status | Meaning | PMS Action |
|---|---|---|---|
| `A1` | Certified in Total | Approved — full authorization granted | Store `certificationNumber`, enable scheduling |
| `A3` | Certified — Partial | Approved — partial authorization only | Store auth, flag partial — alert staff |
| `A4` | Denied | Denied — authorization not granted | Flag for denial management, store denial reasons |
| `A6` | Modified | Modified by payer — not exactly as submitted | Review changes, store modified auth |
| `CA` | Cancel Acknowledge | Cancellation confirmed | Mark cancelled in PMS |
| `CT` | Contact Payer | Payer requests provider contact | Alert staff to call payer |
| `NA` | No Action Required | No authorization required for this service | Proceed without auth |
| `P1` | Pending | Awaiting payer decision | Keep polling or queue for manual follow-up |
| `PD` | Pend | Pended — additional info required | Alert staff; attach supporting docs; resubmit |
| `VO` | Voided | Review voided | Mark voided in PMS |
| `WR` | Waiting for Additional Information | Payer requires more info | Route to clinical staff; attach and resubmit |

### Procedure-Level statusCode (Procedures.statusCode)

Same codes apply at the individual procedure level within `procedures[n].statusCode`.

---

## 15. Request Type Codes

| requestTypeCode | Description |
|---|---|
| `AR` | Authorization Request — prior auth for services |
| `HS` | Health Services Review — concurrent or retrospective review |
| `SC` | Service Certification — certification of service |
| `SS` | Specialist Referral — referral to specialist |
| `RN` | Referral Notification — notification of referral (no approval needed) |
| `RR` | Referral for Specialty Care — referral requiring payer acknowledgement |
| `IN` | Intake |

---

## 16. Sample curl Calls

### 16.1 Get Token

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

### 16.2 Search Existing Service Reviews

```bash
curl -X GET "https://api.availity.com/v2/service-reviews\
?payer.id=BCBSF\
&requestingProvider.npi=1234567890\
&subscriber.memberId=ABC987654321\
&fromDate=2025-01-01\
&toDate=2025-03-31\
&requestTypeCode=AR\
&statusCode=A1" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 16.3 Submit New Prior Authorization Request (Professional)

```bash
curl -X POST "https://api.availity.com/v2/service-reviews" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "requestTypeCode": "AR",
    "serviceTypeCode": "MH",
    "serviceLevelCode": "R",
    "placeOfServiceCode": "11",
    "fromDate": "2025-04-01",
    "toDate": "2025-06-30",
    "quantity": "12",
    "quantityTypeCode": "VS",
    "payer": {
      "id": "BCBSF"
    },
    "requestingProvider": {
      "npi": "1234567890",
      "taxId": "123456789",
      "lastName": "Smith Medical Group",
      "city": "Jacksonville",
      "stateCode": "FL",
      "zipCode": "32201",
      "phone": "9045551234"
    },
    "renderingProviders": [
      {
        "npi": "9876543210",
        "lastName": "JONES",
        "firstName": "SARAH",
        "specialtyCode": "103T00000X"
      }
    ],
    "subscriber": {
      "memberId": "XYZ123456789",
      "lastName": "DOE",
      "firstName": "JOHN"
    },
    "patient": {
      "lastName": "DOE",
      "firstName": "JOHN",
      "birthDate": "1985-06-15",
      "genderCode": "M",
      "subscriberRelationshipCode": "18"
    },
    "diagnoses": [
      {
        "code": "F32.1",
        "qualifierCode": "ABK"
      }
    ],
    "procedures": [
      {
        "code": "90837",
        "qualifierCode": "HC",
        "quantity": "12",
        "quantityTypeCode": "VS",
        "fromDate": "2025-04-01",
        "toDate": "2025-06-30"
      }
    ]
  }'
```

---

### 16.4 Submit Inpatient / Institutional Authorization

```bash
curl -X POST "https://api.availity.com/v2/service-reviews" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "requestTypeCode": "AR",
    "serviceTypeCode": "MH",
    "serviceLevelCode": "U",
    "placeOfServiceCode": "21",
    "admissionTypeCode": "2",
    "admissionSourceCode": "7",
    "fromDate": "2025-04-10",
    "toDate": "2025-04-17",
    "quantity": "7",
    "quantityTypeCode": "DA",
    "payer": { "id": "AETNA" },
    "requestingProvider": {
      "npi": "1234567890",
      "taxId": "123456789",
      "lastName": "General Hospital",
      "stateCode": "TX"
    },
    "subscriber": {
      "memberId": "M987654321",
      "lastName": "JOHNSON",
      "firstName": "MARY"
    },
    "patient": {
      "lastName": "JOHNSON",
      "firstName": "MARY",
      "birthDate": "1962-11-03",
      "genderCode": "F",
      "subscriberRelationshipCode": "18"
    },
    "diagnoses": [
      { "code": "F20.0", "qualifierCode": "ABK" },
      { "code": "F33.2", "qualifierCode": "APR" }
    ],
    "procedures": [
      {
        "revenueCode": "0100",
        "quantity": "7",
        "quantityTypeCode": "DA"
      }
    ]
  }'
```

---

### 16.5 Poll for Authorization Decision

```bash
# Get id from Location header or by searching GET /service-reviews
REVIEW_ID="sr-20250401-abc123"

curl -X GET "https://api.availity.com/v2/service-reviews/${REVIEW_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json"
```

---

### 16.6 Update an Existing Review (Add Diagnosis)

```bash
curl -X PUT "https://api.availity.com/v2/service-reviews" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "id": "sr-20250401-abc123",
    "requestTypeCode": "AR",
    "payer": { "id": "BCBSF" },
    "requestingProvider": {
      "npi": "1234567890",
      "lastName": "Smith Medical Group",
      "stateCode": "FL"
    },
    "subscriber": {
      "memberId": "XYZ123456789"
    },
    "patient": {
      "lastName": "DOE",
      "firstName": "JOHN",
      "birthDate": "1985-06-15",
      "subscriberRelationshipCode": "18"
    },
    "diagnoses": [
      { "code": "F32.1", "qualifierCode": "ABK" },
      { "code": "F41.1", "qualifierCode": "APR" }
    ],
    "procedures": [
      {
        "code": "90837",
        "qualifierCode": "HC",
        "quantity": "12",
        "quantityTypeCode": "VS",
        "fromDate": "2025-04-01",
        "toDate": "2025-06-30"
      }
    ],
    "supplementalInformation": {
      "refAuthNumber": "AUTH-2025-00123",
      "updateType": "AR",
      "sequence": "1"
    }
  }'
```

---

### 16.7 Void a Service Review

```bash
curl -X DELETE "https://api.availity.com/v2/service-reviews/${REVIEW_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
# Returns 202 Accepted (async) or 204 No Content (sync)
```

---

### 16.8 Demo Sandbox — Simulated Scenarios

```bash
# Simulate approved authorization
curl -X POST "https://api.availity.com/v2/service-reviews" \
  -H "Authorization: Bearer ${DEMO_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "X-Api-Mock-Scenario-ID: ServiceReviews-Approved-i" \
  -H "X-Api-Mock-Response: true" \
  -d '{
    "requestTypeCode": "AR",
    "payer": { "id": "00611" },
    "requestingProvider": { "npi": "1234567893", "city": "Jacksonville", "stateCode": "FL" },
    "subscriber": { "memberId": "TEST1" },
    "patient": { "lastName": "Doe", "firstName": "John", "birthDate": "1990-01-01", "subscriberRelationshipCode": "18" }
  }'

# Simulate denied authorization
curl -X POST "https://api.availity.com/v2/service-reviews" \
  -H "Authorization: Bearer ${DEMO_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "X-Api-Mock-Scenario-ID: ServiceReviews-Denied-i" \
  -H "X-Api-Mock-Response: true" \
  -d '{ "requestTypeCode": "AR", "payer": { "id": "00611" }, "requestingProvider": { "npi": "1234567893", "city": "Jacksonville", "stateCode": "FL" }, "subscriber": { "memberId": "TEST1" }, "patient": { "lastName": "Doe", "firstName": "John", "birthDate": "1990-01-01", "subscriberRelationshipCode": "18" } }'

# Simulate pended (WR) — additional info required
curl -X POST "https://api.availity.com/v2/service-reviews" \
  -H "Authorization: Bearer ${DEMO_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "X-Api-Mock-Scenario-ID: ServiceReviews-WR-i" \
  -H "X-Api-Mock-Response: true" \
  -d '{ "requestTypeCode": "AR", "payer": { "id": "00611" }, "requestingProvider": { "npi": "1234567893", "city": "Jacksonville", "stateCode": "FL" }, "subscriber": { "memberId": "TEST1" }, "patient": { "lastName": "Doe", "firstName": "John", "birthDate": "1990-01-01", "subscriberRelationshipCode": "18" } }'
```

---

## 17. Sample Python Integration

### 17.1 Service Review Client

```python
# app/services/availity_service_review.py
import asyncio
import httpx
from typing import Optional


class AvailityServiceReviewClient:

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
                f"{self.base_url}/v1/token",   # always v1 for token
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
    # GET /service-reviews — search
    # ──────────────────────────────────────────────────────────────
    async def search_service_reviews(self, **params) -> dict:
        """Search existing service reviews by query parameters."""
        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/v2/service-reviews",
                params=params,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept":        "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    # ──────────────────────────────────────────────────────────────
    # POST /service-reviews — create
    # ──────────────────────────────────────────────────────────────
    async def create_service_review(self, service_review: dict) -> str:
        """
        Submit a new service review (prior auth / referral).
        Returns the review ID extracted from the Location header.
        Raises if no ID can be extracted.
        """
        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/v2/service-reviews",
                json=service_review,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type":  "application/json",
                    "Accept":        "application/json",
                },
            )
            resp.raise_for_status()  # 202 Accepted expected

            # Extract ID from Location header: /v2/service-reviews/{id}
            location = resp.headers.get("Location", "")
            if location:
                return location.rstrip("/").split("/")[-1]

            raise ValueError(
                "POST /service-reviews returned 202 but no Location header. "
                "Use search_service_reviews() to find the submitted review."
            )

    # ──────────────────────────────────────────────────────────────
    # PUT /service-reviews — update
    # ──────────────────────────────────────────────────────────────
    async def update_service_review(self, service_review: dict) -> None:
        """
        Update an existing service review.
        service_review must include 'id'.
        Review must have updatable=True.
        """
        if not service_review.get("id"):
            raise ValueError("service_review.id is required for PUT")

        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{self.base_url}/v2/service-reviews",
                json=service_review,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type":  "application/json",
                    "Accept":        "application/json",
                },
            )
            resp.raise_for_status()  # 202 Accepted expected

    # ──────────────────────────────────────────────────────────────
    # GET /service-reviews/{id} — retrieve / poll
    # ──────────────────────────────────────────────────────────────
    async def get_service_review(self, review_id: str) -> dict:
        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/v2/service-reviews/{review_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept":        "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    # ──────────────────────────────────────────────────────────────
    # DELETE /service-reviews/{id} — void
    # ──────────────────────────────────────────────────────────────
    async def void_service_review(self, review_id: str) -> bool:
        """
        Void a service review. Only call when deletable=True.
        Returns True if void accepted (202) or complete (204).
        """
        token = await self.get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.base_url}/v2/service-reviews/{review_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            return resp.status_code in (202, 204)

    # ──────────────────────────────────────────────────────────────
    # Poll until terminal status
    # ──────────────────────────────────────────────────────────────
    async def poll_until_terminal(
        self,
        review_id: str,
        max_polls: int = 20,
        poll_interval_s: float = 3.0,
    ) -> dict:
        """
        Poll GET /service-reviews/{id} until a terminal statusCode is reached.
        Terminal codes: A1, A3, A4, A6, CA, NA, VO
        Pending codes (keep polling): P1, PD, WR, CT
        """
        TERMINAL_CODES = {"A1", "A3", "A4", "A6", "CA", "CT", "NA", "VO"}
        # WR and PD require staff action — treat as terminal for automation
        STAFF_ACTION_CODES = {"WR", "PD"}

        for attempt in range(max_polls):
            try:
                review = await self.get_service_review(review_id)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 202:
                    # Still processing — response has no body
                    await asyncio.sleep(poll_interval_s)
                    continue
                raise

            status_code = review.get("statusCode", "")

            if status_code in TERMINAL_CODES or status_code in STAFF_ACTION_CODES:
                return review

            await asyncio.sleep(poll_interval_s)

        raise TimeoutError(
            f"Service review {review_id} did not reach terminal status "
            f"after {max_polls} polls"
        )

    # ──────────────────────────────────────────────────────────────
    # Full PA workflow: submit → poll → return result
    # ──────────────────────────────────────────────────────────────
    async def submit_and_poll(self, service_review: dict) -> dict:
        """
        Full prior authorization workflow:
          1. POST to create
          2. Poll until terminal status
          3. Return completed ServiceReview
        """
        review_id = await self.create_service_review(service_review)
        return await self.poll_until_terminal(review_id)
```

### 17.2 Authorization Extraction Utilities

```python
# app/services/service_review_parser.py

APPROVED_CODES = {"A1", "A3", "A6"}
DENIED_CODES   = {"A4"}
PEND_CODES     = {"WR", "PD", "CT"}


def is_approved(review: dict) -> bool:
    return review.get("statusCode") in APPROVED_CODES


def is_denied(review: dict) -> bool:
    return review.get("statusCode") in DENIED_CODES


def is_pended(review: dict) -> bool:
    return review.get("statusCode") in PEND_CODES


def extract_auth_numbers(review: dict) -> dict:
    """
    Extract authorization numbers from the ServiceReview response.
    Returns top-level cert number plus per-procedure numbers.
    """
    result = {
        "topLevel": {
            "certificationNumber":        review.get("certificationNumber"),
            "certificationEffectiveDate": review.get("certificationEffectiveDate"),
            "certificationExpirationDate": review.get("certificationExpirationDate"),
            "certificationIssueDate":     review.get("certificationIssueDate"),
        },
        "procedures": [],
        "traceNumbers": review.get("traceNumbers", []),
    }

    for proc in review.get("procedures", []):
        result["procedures"].append({
            "procedureCode":              proc.get("code"),
            "certificationNumber":        proc.get("certificationNumber"),
            "certificationEffectiveDate": proc.get("certificationEffectiveDate"),
            "certificationExpirationDate": proc.get("certificationExpirationDate"),
            "statusCode":                 proc.get("statusCode"),
            "status":                     proc.get("status"),
        })

    return result


def extract_denial_reasons(review: dict) -> list[dict]:
    """
    Extract denial reasons from statusReasons and payerNotes.
    """
    reasons = []

    for reason in review.get("statusReasons", []):
        reasons.append({
            "source":  "statusReason",
            "code":    reason.get("code") if isinstance(reason, dict) else str(reason),
            "message": reason.get("message", "") if isinstance(reason, dict) else "",
        })

    for note in review.get("payerNotes", []):
        reasons.append({
            "source":   "payerNote",
            "typeCode": note.get("typeCode"),
            "type":     note.get("type"),
            "message":  note.get("message"),
        })

    return reasons


def build_pms_auth_record(review: dict) -> dict:
    """
    Build a flat dict suitable for inserting into PMS authorization table.
    """
    auth = extract_auth_numbers(review)
    payer = review.get("payer", {})
    patient = review.get("patient", {})
    subscriber = review.get("subscriber", {})

    return {
        # ── Identifiers ──────────────────────────────────────
        "availityId":          review.get("id"),
        "certificationNumber": auth["topLevel"]["certificationNumber"],
        "controlNumber":       review.get("controlNumber"),
        # ── Dates ────────────────────────────────────────────
        "effectiveDate":       auth["topLevel"]["certificationEffectiveDate"],
        "expirationDate":      auth["topLevel"]["certificationExpirationDate"],
        "issueDate":           auth["topLevel"]["certificationIssueDate"],
        "serviceFromDate":     review.get("fromDate"),
        "serviceToDate":       review.get("toDate"),
        # ── Status ───────────────────────────────────────────
        "statusCode":          review.get("statusCode"),
        "status":              review.get("status"),
        "isApproved":          is_approved(review),
        "isDenied":            is_denied(review),
        "isPended":            is_pended(review),
        "updatable":           review.get("updatable", False),
        "deletable":           review.get("deletable", False),
        # ── Payer ────────────────────────────────────────────
        "payerId":             payer.get("id"),
        "payerName":           payer.get("name"),
        "payerPhone":          payer.get("phone"),
        # ── Member ───────────────────────────────────────────
        "memberId":            subscriber.get("memberId"),
        "patientLastName":     patient.get("lastName"),
        "patientFirstName":    patient.get("firstName"),
        "patientDOB":          patient.get("birthDate"),
        # ── Service ──────────────────────────────────────────
        "requestTypeCode":     review.get("requestTypeCode"),
        "serviceTypeCode":     review.get("serviceTypeCode"),
        "placeOfServiceCode":  review.get("placeOfServiceCode"),
        "quantity":            review.get("quantity"),
        "quantityTypeCode":    review.get("quantityTypeCode"),
        # ── Procedures ───────────────────────────────────────
        "procedures":          auth["procedures"],
        # ── Notes ────────────────────────────────────────────
        "denialReasons":       extract_denial_reasons(review) if is_denied(review) else [],
        "payerNotes":          [n.get("message") for n in review.get("payerNotes", [])],
    }
```

### 17.3 Usage Example

```python
import asyncio
import os

client = AvailityServiceReviewClient(
    client_id     = os.environ["AVAILITY_CLIENT_ID"],
    client_secret = os.environ["AVAILITY_CLIENT_SECRET"],
)

async def main():

    # ── Build a prior auth request ────────────────────────────────
    service_review_request = {
        "requestTypeCode":  "AR",
        "serviceTypeCode":  "MH",
        "serviceLevelCode": "R",
        "placeOfServiceCode": "11",
        "fromDate": "2025-04-01",
        "toDate":   "2025-06-30",
        "quantity": "12",
        "quantityTypeCode": "VS",
        "payer": {"id": "BCBSF"},
        "requestingProvider": {
            "npi":       "1234567890",
            "taxId":     "123456789",
            "lastName":  "Smith Medical Group",
            "stateCode": "FL",
        },
        "renderingProviders": [
            {"npi": "9876543210", "lastName": "JONES", "firstName": "SARAH"}
        ],
        "subscriber": {
            "memberId":  "XYZ123456789",
            "lastName":  "DOE",
            "firstName": "JOHN",
        },
        "patient": {
            "lastName":  "DOE",
            "firstName": "JOHN",
            "birthDate": "1985-06-15",
            "genderCode": "M",
            "subscriberRelationshipCode": "18",
        },
        "diagnoses": [{"code": "F32.1", "qualifierCode": "ABK"}],
        "procedures": [
            {
                "code": "90837",
                "qualifierCode": "HC",
                "quantity": "12",
                "quantityTypeCode": "VS",
                "fromDate": "2025-04-01",
                "toDate":   "2025-06-30",
            }
        ],
    }

    # ── Submit and poll ───────────────────────────────────────────
    review = await client.submit_and_poll(service_review_request)

    # ── Extract and log results ───────────────────────────────────
    auth_record = build_pms_auth_record(review)
    print(f"Status:      {auth_record['statusCode']} — {auth_record['status']}")
    print(f"Auth Number: {auth_record['certificationNumber']}")
    print(f"Effective:   {auth_record['effectiveDate']}")
    print(f"Expires:     {auth_record['expirationDate']}")
    print(f"Approved:    {auth_record['isApproved']}")

    if auth_record["isDenied"]:
        print("DENIAL REASONS:")
        for r in auth_record["denialReasons"]:
            print(f"  [{r['source']}] {r.get('typeCode','')} — {r['message']}")

    if auth_record["isPended"]:
        print("PENDED — staff action required:")
        for note in auth_record["payerNotes"]:
            print(f"  {note}")

asyncio.run(main())
```

---

## 18. Key Differences from Coverages & Claim Statuses APIs

| Aspect | Coverages API | Claim Statuses API | Service Reviews API |
|---|---|---|---|
| **X12 Transaction** | 270/271 (Eligibility) | 276/277 (Claim Status) | 278 (Service Authorization) |
| **API Version** | `/v1` | `/v1` | **`/v2`** |
| **Operations** | POST, GET, DELETE | POST (override GET), GET, DELETE | GET, **POST, PUT**, GET/{id}, DELETE |
| **POST body format** | `application/x-www-form-urlencoded` | `application/x-www-form-urlencoded` | **`application/json`** |
| **POST response body** | `CoverageSummary` | `ResultSet` | **No body** (ID in `Location` header) |
| **Supports UPDATE** | No | No | **Yes — PUT** |
| **Void vs Delete** | Hard delete | Hard delete | **Void (async, payer-notified)** |
| **DELETE response** | 204 No Content | 200 OK | **202 Accepted or 204** |
| **Status terminal check** | `statusCode == "4"` | `statusCode == "4"` | Named codes: `A1`, `A3`, `A4`, etc. |
| **Primary key data** | `memberId`, benefit amounts | Adj. amounts, check numbers | **certificationNumber** (auth number) |
| **Specialty fields** | None | None | Chiro, oxygen, transport, home health |
| **Pend/Appeal support** | No | No | **Yes — WR, PD status + PUT to resubmit** |
| **Workflow position** | Pre-service eligibility | Post-service AR follow-up | **Pre-service authorization** |

---

## 19. PMS Integration Patterns

### Pattern 1 — Standard Prior Authorization Workflow

```python
async def prior_auth_workflow(appointment: dict) -> dict:
    """
    Triggered when a procedure requiring auth is scheduled.
    Returns auth record for storage in PMS.
    """
    review_request = {
        "requestTypeCode":    "AR",
        "serviceTypeCode":    appointment["serviceTypeCode"],
        "serviceLevelCode":   "R",
        "placeOfServiceCode": appointment["placeOfServiceCode"],
        "fromDate":           appointment["serviceDate"],
        "toDate":             appointment["serviceDate"],
        "payer":              {"id": appointment["payerId"]},
        "requestingProvider": {
            "npi":       appointment["providerNpi"],
            "taxId":     appointment["providerTaxId"],
            "lastName":  appointment["providerName"],
            "stateCode": appointment["providerState"],
        },
        "subscriber": {"memberId": appointment["memberId"]},
        "patient": {
            "lastName":  appointment["patientLastName"],
            "firstName": appointment["patientFirstName"],
            "birthDate": appointment["patientDOB"],
            "genderCode": appointment["genderCode"],
            "subscriberRelationshipCode": appointment["relationshipCode"],
        },
        "diagnoses":  [{"code": dx, "qualifierCode": "ABK"}
                       for dx in appointment["diagnosisCodes"]],
        "procedures": [{"code": cpt, "qualifierCode": "HC",
                        "quantity": "1", "quantityTypeCode": "VS"}
                       for cpt in appointment["procedureCodes"]],
    }

    review = await client.submit_and_poll(review_request)
    auth   = build_pms_auth_record(review)

    if auth["isApproved"]:
        await pms.store_authorization(appointment["id"], auth)
        await pms.update_appointment_status(appointment["id"], "auth_approved")
    elif auth["isDenied"]:
        await pms.flag_authorization_denied(appointment["id"], auth)
        await pms.notify_staff("PA Denied", appointment, auth["denialReasons"])
    elif auth["isPended"]:
        await pms.flag_authorization_pended(appointment["id"], auth)
        await pms.notify_staff("PA Pended — Action Required", appointment, auth["payerNotes"])

    return auth
```

### Pattern 2 — Authorization Expiration Check (Nightly)

```python
async def check_expiring_authorizations(days_ahead: int = 30):
    """
    Nightly job: query Availity for status of auths expiring within N days.
    Flags any that are pended, denied, or expired in PMS.
    """
    expiring = await pms.get_authorizations_expiring_within(days_ahead)

    for auth in expiring:
        review = await client.get_service_review(auth["availityId"])
        updated = build_pms_auth_record(review)

        if updated["statusCode"] != auth["statusCode"]:
            await pms.update_authorization(auth["id"], updated)

        if updated["isDenied"] and not auth.get("denialFlagged"):
            await pms.notify_staff("Auth Denied", auth, updated["denialReasons"])
```

### Pattern 3 — Resubmit After Pend (Staff-Triggered)

```python
async def resubmit_pended_auth(
    review_id: str,
    additional_diagnosis_codes: list[str],
    clinical_notes: str,
) -> dict:
    """
    Called by staff after gathering additional clinical information.
    Fetches current review, validates it's updatable, then PUTs with new data.
    """
    # 1. Fetch current review
    review = await client.get_service_review(review_id)

    if not review.get("updatable"):
        raise ValueError(f"Review {review_id} is not updatable (status: {review['statusCode']})")

    # 2. Add new diagnoses
    existing_codes = {d["code"] for d in review.get("diagnoses", [])}
    for code in additional_diagnosis_codes:
        if code not in existing_codes:
            review["diagnoses"].append({"code": code, "qualifierCode": "ABK"})

    # 3. Add provider note
    review.setdefault("providerNotes", []).append({
        "message":  clinical_notes,
        "typeCode": "ADD",
    })

    # 4. Set supplemental info for update context
    review["supplementalInformation"] = {
        "refAuthNumber": review.get("certificationNumber", ""),
        "updateType":    "AR",
        "sequence":      "1",
    }

    # 5. Submit update and poll
    await client.update_service_review(review)
    return await client.poll_until_terminal(review_id)
```

---

*Source: Availity Service Reviews 2.0.0 Swagger Specification (healthcare-hipaa-transactions-document.json) · Swagger 2.0 · Host: api.availity.com · BasePath: /v2*
