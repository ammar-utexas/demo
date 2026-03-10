# Availity API — Test Data & Sandbox Access Guide
**Experiment 47 · PMS Integration · MPS Inc.**  
Last Updated: March 2026 · Source: developer.availity.com

---

## Table of Contents

1. [Overview — What Is Available for Testing](#1-overview)
2. [Step-by-Step: Getting Demo Sandbox Access](#2-getting-access)
3. [Authentication in the Demo Environment](#3-authentication)
4. [How Demo Scenarios Work](#4-how-demo-scenarios-work)
5. [Test Credentials & Member IDs](#5-test-credentials--member-ids)
6. [Coverages API — Demo Scenarios (Eligibility 270/271)](#6-coverages-api-demo-scenarios)
7. [Service Reviews API — Demo Scenarios (PA 278)](#7-service-reviews-api-demo-scenarios)
8. [E&B Value-Add APIs — Test Payloads](#8-eb-value-add-apis-test-payloads)
   - [Care Reminders](#81-care-reminders)
   - [Member ID Card](#82-member-id-card)
9. [Payer-Specific Requirements Reference](#9-payer-specific-requirements-reference)
   - [Care Reminders — Supported Payers](#91-care-reminders--supported-payers)
   - [Member ID Card — Supported Payers](#92-member-id-card--supported-payers)
10. [Rate Limits](#10-rate-limits)
11. [Key URLs Reference](#11-key-urls-reference)
12. [Known Limitations of the Demo Environment](#12-known-limitations-of-the-demo-environment)

---

## 1. Overview

Availity does **not** publish downloadable test data files. Instead, testing is done through:

| Method | What It Gives You |
|---|---|
| **Demo Sandbox (auto-approved)** | Canned JSON responses triggered by scenario header — no PHI, no real payer connectivity |
| **Published test member IDs** | Specific `memberId` / `payerId` values documented for E&B Value-Add APIs |
| **"Try" button in portal** | Live API calls against the sandbox from within the developer portal UI |
| **Standard Plan (contract required)** | Full API access + real payer data — requires Trading Partner agreement |

> **Bottom line for Exp 47:** Sign up for the Demo plan to validate request/response shapes and polling logic. Upgrade to Standard plan when ready for real payer data in QA/prod.

---

## 2. Getting Access

### Step 1 — Create a Developer Portal Account

1. Go to **https://developer.availity.com**
2. Click **Create Account** (top right)
3. On the Sign In page, click **Create an account** again
4. Fill in: Email, First Name, Last Name, Password (must meet password policy)
5. Confirm password and click **Sign Up**
6. Enter the **security code** sent to your email and click **Confirm Account**
   - Code is valid for **24 hours**; click Resend if needed
7. Set up the **Authenticator App** (MFA required):
   - Install any TOTP authenticator app on your phone
   - Scan the QR code displayed on screen
   - Your account will appear in the app

### Step 2 — Create or Join an Organization

> You must be linked to an organization before creating an application.

**To create a new organization:**
1. Log in to the portal
2. Navigate to **My Apps → My Org/Users → Create New Organization**
3. Fill in organization details including Tax ID if available

**To join an existing organization:**
- Open a support ticket with case reason **"API"**
- Include: your User ID, email, organization name, Organization Admin contact, and Tax ID if available
- Approval is manual and may take 24–48 hours

### Step 3 — Create an Application

1. Log in to the portal
2. Click **My Apps** in the menu bar
3. Click **Create a New App**
4. Enter application name and details, click **Create App**
5. **Save your Client ID and Client Secret immediately** — the secret is shown only once

### Step 4 — Subscribe to the Demo Plan (Healthcare HIPAA Transactions)

1. Click **API Products** in the menu bar
2. Find **Healthcare HIPAA Transactions** and click **More Info**
3. Click **Access this Product**
4. Select the **Demo Plan** and click **Access with this Plan**
5. Add to cart and complete subscription
6. **Demo subscriptions are automatically approved** — no wait time

> To also subscribe to the **E&B Value-Add APIs** (Care Reminders, Member ID Card), repeat steps 2–5 for that product separately.

### Step 5 — Retrieve Your API Credentials

1. Go to **My Apps → Approved Access**
2. Find the Healthcare HIPAA Transactions product
3. Expand **Client Info** to see your **API Key** (Client ID) and **Client Secret**
4. Store these in your `.env` file:

```env
AVAILITY_CLIENT_ID=your_api_key_here
AVAILITY_CLIENT_SECRET=your_client_secret_here
AVAILITY_BASE_URL=https://api.availity.com
AVAILITY_TOKEN_URL=https://api.availity.com/v1/token
AVAILITY_SCOPE=healthcare-hipaa-transactions healthcare-hipaa-transactions-demo
```

### Step 6 (Optional) — Upgrade to Standard Plan for Real Data

When ready for real payer connectivity:

1. In the portal, subscribe to the **Standard Plan** for the desired API product
2. Email **partnermanagement@availity.com** to begin contracting
3. The Trading Partner Management team will reach out to complete the agreement
4. Subscription is activated upon contract verification
5. Standard plan rate limits: **100 req/s, 100,000 req/day**

---

## 3. Authentication

All environments (Demo and Standard) use OAuth 2.0 Client Credentials flow.

### Token Request

```bash
curl -i -X POST "https://api.availity.com/v1/token" \
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

> **Token TTL = 5 minutes (300 seconds).** Cache with a 4.5-minute effective TTL and refresh proactively. Every token call counts against your rate limit quota.

### Using the Token

```bash
-H "Authorization: Bearer ${ACCESS_TOKEN}"
```

---

## 4. How Demo Scenarios Work

The Demo environment returns **canned (fixed) responses** regardless of the request body content. You choose which response to receive by passing a special header.

### Request Headers for Demo Mode

| Header | Value | Purpose |
|---|---|---|
| `X-Api-Mock-Scenario-ID` | e.g. `Coverages-Complete-i` | Selects which canned scenario to return |
| `X-Api-Mock-Response` | `true` | Confirms you want a mock response |

### Confirming a Mock Response

Check the response header:
```
X-Api-Mock-Response: true
```
If this header is present, the response is a canned demo response.

### Important Behavioral Notes

- The Demo environment **ignores all request body content** — it returns the same canned response for any valid request
- For POST methods in demo mode, you can send an **empty JSON body `{}`** and still get a valid scenario response
- Not all Availity APIs support demo scenario IDs — check each API's reference section in the portal
- The full list of scenario IDs per API is only visible after logging into the portal and navigating to each API's reference section

---

## 5. Test Credentials & Member IDs

These are the only test identifiers explicitly published in Availity's public documentation. Use them for E&B Value-Add API calls in the QUA (quality/sandbox) environment.

### Primary Test Member

| Field | Value |
|---|---|
| `memberId` | `SUCC123456789` |
| `payerId` | `00611` (Regence BlueShield of Idaho) |
| `firstName` | `PATIENTONE` |
| `lastName` | `TEST` |
| `dateOfBirth` | `1900-01-01` |
| `stateCode` | `FL` |
| `planId` | `1111111111` |
| `policyNumber` | `1111111111` |
| `responsePayerId` | `00611` |
| `planType` | `Medical` |

### Mock Payer IDs (from Payer List API sample responses)

| Payer ID | Display Name | Use |
|---|---|---|
| `100000001` | Mock Payer A | Demo payer list responses |
| `100000002` | Mock Payer B | Demo payer list responses |
| `00611` | Regence BlueShield of Idaho | E&B Value-Add test calls |
| `BCBSF` | Florida Blue | Configurations API sample |

### Provider Test Values

| Field | Value | Notes |
|---|---|---|
| `providerNPI` | `1234567890` | Must start with 1–4, 10 digits |
| `providerTax` | `11111` | Tax ID for care reminders |
| `providerPAPI` | `ABC00000XXXXXXX` | Payer-assigned provider ID |
| `submitterId` | `123456789` | Submitter identifier |
| `controlNumber` | `123456789` | Reference number |
| `groupNumber` | `1111111111` | Group number |

---

## 6. Coverages API — Demo Scenarios (Eligibility 270/271)

**Endpoint:** `POST /v1/coverages`  
**Polling:** `GET /v1/coverages/{id}`

Use these scenario IDs in the `X-Api-Mock-Scenario-ID` header.

| Scenario ID | HTTP Status | Description |
|---|---|---|
| `Coverages-Complete-i` | 200 | Successfully retrieved coverage — `statusCode: 4` (Complete) |
| `Coverages-PayerError1-i` | 200 | Payer indicates provider is ineligible for inquiries |
| `Coverages-PayerError2-i` | 200 | Payer indicates subscriber name is invalid |
| `Coverages-InProgress-i` | 202 | Availity is retrieving coverage — `statusCode: 0` (In Progress) |
| `Coverages-Retrying-i` | 202 | Payer did not respond — Availity is retrying |
| `Coverages-RequestError1-i` | 400 | Request failed Availity input validation |
| `Coverages-RequestError2-i` | 400 | Request failed Availity input validation (alternate) |

### Status Code Reference

| statusCode | status | Meaning |
|---|---|---|
| `0` | In Progress | Request processing — poll again in ~2 seconds |
| `1` | Retrying | Payer timeout — Availity retrying |
| `4` | Complete | Final response received from payer |

### Sample Demo Request — Eligibility (Complete Scenario)

```bash
curl -X POST "https://api.availity.com/availity/v1/coverages" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-Api-Mock-Scenario-ID: Coverages-Complete-i" \
  -H "X-Api-Mock-Response: true" \
  -d "payerId=00611&memberId=SUCC123456789&patientLastName=TEST&patientFirstName=PATIENTONE&patientBirthDate=1900-01-01&serviceType=30&providerNpi=1234567890"
```

### Sample Poll Request

```bash
# Use the id returned in the POST Location header
curl -X GET "https://api.availity.com/availity/v1/coverages/{id}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "X-Api-Mock-Scenario-ID: Coverages-Complete-i" \
  -H "X-Api-Mock-Response: true"
```

### Sample Error Response (400)

```json
{
  "userMessage": "This client system has made an invalid request.",
  "developerMessage": "Your request is not formed properly.",
  "documentation": "https://api.availity.com/availity/v1/documentation/coverages",
  "reasonCode": 0,
  "statusCode": 400,
  "errors": [
    { "field": "serviceType", "errorMessage": "This field is required." },
    { "field": "memberId", "errorMessage": "Enter a patient ID containing letters, numbers, spaces, and special characters." }
  ]
}
```

> **Note:** The full scenario ID table for Coverages (and all other APIs) is visible in each API's reference section inside the developer portal after login.

---

## 7. Service Reviews API — Demo Scenarios (PA 278)

**Endpoint:** `POST /v2/service-reviews`  
**Polling:** `GET /v2/service-reviews?sessionId={sessionId}`

### Request Subtypes (`requestTypeCode`)

| Code | Type |
|---|---|
| `HS` | Outpatient authorization (Health Services Review) |
| `AR` | Inpatient authorization / Admission Review |
| `SC` | Specialty Care / Referral |

### Sample Demo Request — PA Submission

```bash
curl -X POST "https://api.availity.com/availity/v2/service-reviews" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Api-Mock-Scenario-ID: {SCENARIO_ID_FROM_PORTAL}" \
  -H "X-Api-Mock-Response: true" \
  -d '{}'
```

> For POST methods in demo mode, an **empty JSON body `{}`** is valid — the canned response is returned regardless.

### Known Test Values (from public docs)

```bash
# GET (inquiry) — these parameters are shown in Availity's published sample
requestTypeCode=AR
requestingProviderLastName=SLICE N DICE DISCOUNT SURGERY
requestingProviderAddressLine1=123Street
requestingProviderCity=Jacksonville
requestingProviderState=FL
requestingProviderZipCode=123451234
requestingProviderContactName=John
requestingProviderPhone=1112223333
memberId=TEST1
patientLastName=Doe
patientFirstName=John
patientBirthDate=1990-01-01
fromDate=2015-01-01
requestingProviderNpi=1234567893
```

### X12 278 Status Codes (PA Result Handling)

| Status Code | Description | Action |
|---|---|---|
| `A1` | Approved as Requested | Store auth number → proceed to scheduling |
| `A3` | Approved — Modified | Store auth number + note modifications |
| `A4` | Denied | Store denial reason → alert staff for appeal |
| `A6` | Modified — Denied | Store denial + modifications → alert staff |
| `WR` | Pended / Waiting for Information | Queue for staff review → attach clinical docs → resubmit |
| `CA` | Cancelled | Log cancellation |

### Configurations API — Get Payer-Specific Rules Before Submitting

```bash
# Get validation rules for outpatient auth (HS) for a specific payer
curl -X GET "https://api.availity.com/availity/v1/configurations\
?type=service-reviews&subtypeId=HS&payerId=00611" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

| `type` value | `subtypeId` value | Use |
|---|---|---|
| `service-reviews` | `HS`, `AR`, `SC` | POST /v2/service-reviews validation rules |
| `service-reviews-inquiry` | `HS`, `AR`, `SC` | GET /v2/service-reviews validation rules |
| `270` | *(none)* | Coverages (eligibility) validation rules |

---

## 8. E&B Value-Add APIs — Test Payloads

**Base URL (QUA/sandbox):** `https://qua.api.availity.com`  
**Base URL (production):** `https://api.availity.com`

> The E&B Value-Add APIs do **not** use `X-Api-Mock-Scenario-ID`. Instead, the test member ID `SUCC123456789` with payer `00611` returns a real-shaped success response from the QUA environment.

---

### 8.1 Care Reminders

**Endpoint:** `POST /pre-claim/eb-value-adds/care-reminders`

#### Full Test Request

```bash
curl -L -X POST 'https://qua.api.availity.com/pre-claim/eb-value-adds/care-reminders' \
  -H 'accept: application/json' \
  -H 'content-type: application/json' \
  -H 'Authorization: Bearer ADDTOKENHERE' \
  --data-raw '{
    "payerId": "00611",
    "memberId": "SUCC123456789",
    "stateId": "FL",
    "lineOfBusiness": "COMMERCIAL",
    "providerTax": "11111",
    "controlNumber": "123456789",
    "providerNPI": "1234567890",
    "submitterId": "123456789",
    "subscriberRelationship": "18",
    "lastName": "TEST",
    "firstName": "PATIENTONE",
    "groupNumber": "1111111111",
    "dateOfBirth": "1990-01-01",
    "genderCode": "F",
    "providerPAPI": "ABC00000XXXXXXX",
    "middleName": "MIDDLE",
    "suffix": "Sr."
  }'
```

#### Expected Success Response

```json
{
  "status": "Success",
  "statusCode": 4,
  "data": {
    "disclaimer": "Care reminders are based on clinical and administrative information submitted to participating insurance companies...",
    "title": "Care Reminders",
    "careReminderDetails": [
      {
        "order": ["Date", "Care Gap", "Gap Instructions", "Data Source"],
        "headers": {
          "Date": "Date",
          "Care Gap": "Care Gap",
          "Gap Instructions": "Gap Instructions",
          "Data Source": "Data Source"
        },
        "rows": [
          {
            "Date": "10/30/2023",
            "Care Gap": "Advance Care Planning",
            "Gap Instructions": "Gap closure is based on provider submitting a successfully adjudicated claim for having an Advance Care Planning discussion...",
            "Data Source": "Sample Health Plan 1"
          },
          {
            "Date": "10/30/2023",
            "Care Gap": "Annual Flu Vaccine",
            "Gap Instructions": "Gap closure is based on provider administering a flu vaccine and submitting successfully adjudicated claim...",
            "Data Source": "Sample Health Plan 1"
          },
          {
            "Date": "10/30/2023",
            "Care Gap": "Fall Risk Management",
            "Gap Instructions": "Gap closure is based on provider submitting documentation from an encounter reporting that Fall Risk was assessed...",
            "Data Source": "Sample Health Plan 1"
          },
          {
            "Date": "10/30/2023",
            "Care Gap": "Palliative Care Encounter",
            "Gap Instructions": "Gap closure is based on provider referring appropriate members to a Palliative Care Specialist...",
            "Data Source": "Sample Health Plan 1"
          },
          {
            "Date": "10/30/2023",
            "Care Gap": "Preventive Care Visit",
            "Gap Instructions": "Gap closure is based on successfully adjudicated claim for a 2023 Preventive Care visit, Welcome to Medicare Visit (IPPE) or Annual Wellness Visit...",
            "Data Source": "Sample Health Plan 1"
          }
        ]
      }
    ]
  },
  "createdDate": "2023-12-13T18:27:45.537Z"
}
```

#### Response Field Reference

| Field | Type | Description |
|---|---|---|
| `status` | String | `"Success"` or error string |
| `statusCode` | Integer | `4` = complete/success |
| `data.disclaimer` | String | Legal disclaimer text — render to user |
| `data.title` | String | Payer-assigned section title (e.g. "Care Reminders", "Care Gap") |
| `data.careReminderDetails[].order` | Array | Column display order — use to sort table headers |
| `data.careReminderDetails[].headers` | Object | Key-value pairs for column headings |
| `data.careReminderDetails[].rows` | Array | Each object is one table row; keys match `order` values |

> **Empty rows array is valid** — it means no care gaps exist for this member, not an error.

---

### 8.2 Member ID Card

**Step 1 — POST to initiate, get GTID:**  
**Endpoint:** `POST /pre-claim/eb-value-adds/member-card`

**Step 2 — GET the card document using the GTID:**  
**Endpoint:** `GET /pre-claim/eb-value-adds/member-card/{GTID}`

#### Step 1 — Full Test Request (POST)

```bash
curl -L -X POST 'https://qua.api.availity.com/pre-claim/eb-value-adds/member-card' \
  -H 'accept: application/json' \
  -H 'content-type: application/json' \
  -H 'Authorization: Bearer ADDTOKENHERE' \
  --data-raw '{
    "memberId": "SUCC123456789",
    "payerId": "00611",
    "firstName": "PATIENTONE",
    "lastName": "TEST",
    "dateOfBirth": "1900-01-01",
    "asOfDate": "2024-01-01",
    "effectiveDate": "2024-01-01",
    "stateCode": "FL",
    "planId": "1111111111",
    "policyNumber": "1111111111",
    "responsePayerId": "00611",
    "planType": "Medical"
  }'
```

#### Step 1 — Expected Response (POST)

```json
{
  "status": "Success",
  "statusCode": 4,
  "data": {
    "memberCards": {
      "type": "application/pdf",
      "uris": ["{{GTID}}"]
    }
  },
  "createdDate": "2024-01-01T12:30:00.000Z"
}
```

> Extract `data.memberCards.uris[0]` — this is the GTID for the GET step.

#### Step 2 — Full Test Request (GET)

```bash
curl --request GET \
  --url 'https://qua.api.availity.com/pre-claim/eb-value-adds/member-card/{{GTID}}' \
  --header 'Authorization: Bearer ADDTOKENHERE' \
  --header 'Content-Type: application/x-www-form-urlencoded'
```

> Response is raw **PDF or PNG bytes**. Save to file or stream to client. The `type` field in the POST response (`application/pdf` or `image/png`) tells you the format.

#### Supported Document Types

| `type` value | Format | Notes |
|---|---|---|
| `application/pdf` | PDF bytes | Most common — render in PDF viewer |
| `image/png` | PNG bytes | Some payers return PNG instead |

---

## 9. Payer-Specific Requirements Reference

### 9.1 Care Reminders — Supported Payers

| Payer | Payer ID | Required Fields Beyond payerId + memberId |
|---|---|---|
| Asuris Northwest Health | 93221 | *(none additional)* |
| Blue Cross Blue Shield of Michigan | 00710 | `lineOfBusiness` (BCN \| COMMERCIAL \| MAPPO) |
| Florida Blue | BCBSF | *(none additional)* |
| Florida Blue Medicare | FBM01 | *(none additional)* |
| BCBS Florida Other Blue Plans | OTHER BLUE PLANS | *(none additional)* |
| Humana | HUMANA | *(none additional)* |
| Molina Healthcare Arizona | A4353 | `stateId` |
| Molina Healthcare California | 38333 | `stateId` |
| Molina Healthcare Florida | 51062 | `stateId` |
| Molina Healthcare Idaho | 61799 | `stateId` |
| Molina Healthcare Illinois | 20934 | *(none additional)* |
| Molina Healthcare Iowa | A3144 | `stateId` |
| Molina Healthcare Michigan | 38334 | `stateId` |
| Molina Healthcare Mississippi | 77010 | `stateId` |
| Molina Healthcare Nebraska | A8822 | `stateId` |
| Molina Healthcare Nevada | A6106 | `stateId` |
| Molina Healthcare New Mexico | 09824 | `stateId` |
| Molina Healthcare Ohio | 20149 | `stateId` |
| Molina Healthcare South Carolina | 46299 | `stateId` |
| Molina Healthcare Texas | 20554 | `stateId` |
| Molina Healthcare Utah | SX109 | `stateId` |
| Molina Healthcare Virginia | A6848 | `stateId` |
| Molina Healthcare Washington | 38336 | `stateId` |
| Molina Healthcare Wisconsin | ABRI1 | `stateId` |
| Molina Healthcare – Affinity | 16146 | `stateId` |
| Passport by Molina Healthcare | A6863 | `stateId` |
| Regence BlueCross BlueShield of Oregon | 00851 | *(none additional)* |
| Regence BlueCross BlueShield of Utah | 00910 | *(none additional)* |
| Regence BlueShield of Idaho | 00611 | *(none additional)* ← **use for testing** |
| Regence BlueShield | 00932 | *(none additional)* |
| Senior Whole Health of Massachusetts | A6567 | `stateId` |
| Senior Whole Health of New York | A0281 | `stateId` |
| Truli for Health | TRULI | *(none additional)* |

---

### 9.2 Member ID Card — Supported Payers

| Payer | Payer ID | Required Fields Beyond payerId + memberId |
|---|---|---|
| Aetna | AETNA | *(none additional)* |
| Aetna Better Health | ABH01 | `responsePayerId` (see values below) |
| Mercy Care – Arizona | AZM01 | `responsePayerId` (AZMERCY \| AEMED \| MMICR) |
| Anthem (all plans) | 040, 050, 060, 130, etc. | *(none additional; `thirdPartySystemId` + `routingCode` optional)* |
| Arkansas BCBS | 00520 | *(none additional)* |
| BCBS of Arizona | 53589 | *(none additional)* |
| Florida Blue | BCBSF | *(none additional)* |
| BCBS of Michigan | 00710 | `firstName`, `lastName`, `dateOfBirth`, `groupNumber` |
| BCBS New Jersey | 100046 | `firstName`, `lastName`; optional: `dateOfBirth`, `planId`, `groupNumber` |
| Capital Blue Cross | 361 | *(none additional; `effectiveDate` optional)* |
| HCSC plans (BCBS IL, MT, NM, OK, TX) | BCBSIL, G00751, BCBSNM, BCBSOK, BCBSTX | `firstName`, `lastName` |
| Medical Mutual | 29076 | `groupNumber` |
| Molina Healthcare (all plans) | 51062, 38334, etc. | `stateCode`, `planId`, `policyNumber` |
| Premera (all plans) | 00430, 00934, 93095 | *(none additional)* |
| Regence BlueShield of Idaho | 00611 | *(none additional)* ← **use for testing** |
| TMG Health Insurance | 10688 | *(none additional)* |

#### Aetna Better Health — `responsePayerId` Values

| responsePayerId | Region |
|---|---|
| ABHCA | California |
| ABHFL | Florida |
| ILMSA | Illinois |
| ABHKS | Kansas |
| ABHKY | Kentucky |
| ABHLA | Louisiana |
| ABHMD | Maryland |
| ABHMI | Michigan |
| ABHNJ | New Jersey |
| ABHNY | New York |
| ABHOH | Ohio |
| PENNS | Pennsylvania |
| TMDSA | Texas |
| ABHVA | Virginia |
| AVHWV | West Virginia |
| ABHOK | Oklahoma |

---

## 10. Rate Limits

| Plan | Max Requests/Second | Max Requests/Day | Notes |
|---|---|---|---|
| **Demo** | 5 | 500 | Every API call counts — including token requests and polling |
| **Standard** | 100 | 100,000 | May vary by product (E&B Value-Adds have separate limits) |

> **429 Response** = rate limit exceeded. If per-second limit is hit, wait 1 second and retry. If daily limit is hit, resume the following day.

> **Token call tip:** Cache your access token for up to 4.5 minutes to avoid burning quota on repeated auth calls.

---

## 11. Key URLs Reference

| Resource | URL |
|---|---|
| Developer Portal | https://developer.availity.com |
| Get Started Guide | https://developer.availity.com/partner/gettingstarted |
| API Products Catalog | https://developer.availity.com/portal/catalogue-products |
| HIPAA Transactions Docs | https://developer.availity.com/blog/2025/3/25/hipaa-transactions |
| E&B Value-Add Docs | https://developer.availity.com/blog/2025/3/4/ebvalue-add-api |
| Service Reviews Add-On Docs | https://developer.availity.com/blog/2025/3/4/service-reviews |
| API Guide (auth + workflows) | https://developer.availity.com/blog/2025/3/25/availity-api-guide |
| FAQ | https://developer.availity.com/partner/faq |
| Support | https://developer.availity.com/partner/contact-us |
| Trading Partner email | partnermanagement@availity.com |
| **Token Endpoint (Demo/Prod)** | https://api.availity.com/v1/token |
| **Token Endpoint (Test/QUA)** | https://tst.api.availity.com/v1/token |
| **API Base URL (Prod)** | https://api.availity.com |
| **API Base URL (QUA/Sandbox)** | https://qua.api.availity.com |
| GitHub Mock Data (deprecated) | https://github.com/Availity/availity-mock-data |

---

## 12. Known Limitations of the Demo Environment

| Limitation | Detail |
|---|---|
| **No end-to-end testing** | Demo returns canned responses — payer connectivity is not real |
| **Request body is ignored** | The same scenario response is returned regardless of request payload |
| **No PHI** | All demo data is synthetic — never send real patient data in demo |
| **Not all APIs support scenarios** | Check each API's reference section in the portal for scenario availability |
| **Polling simulation** | Use `Coverages-InProgress-i` then `Coverages-Complete-i` to simulate the async polling flow |
| **E&B Value-Adds use QUA env** | Use `qua.api.availity.com` (not `api.availity.com`) for Care Reminders and Member ID Card sandbox calls |
| **Rate limits apply to demo** | 5 req/s and 500 req/day — token calls count |
| **Secret shown once** | Client Secret is displayed only at app creation — save it immediately |
| **Scenario IDs gated** | Full scenario ID tables require portal login + active subscription to view |
