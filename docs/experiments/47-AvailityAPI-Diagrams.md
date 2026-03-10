# Availity API — Architecture & Workflow Diagrams
**Experiment 47 · PMS Integration · MPS Inc.**  
All diagrams in Mermaid format — render in any Mermaid-compatible viewer  
Last Updated: March 2026

---

## Diagram Index

| # | Diagram | Type | Description |
|---|---|---|---|
| 1 | API Ecosystem Overview | flowchart | All 5 APIs, their roles, and relationships |
| 2 | Pre-Submission Pipeline | flowchart | Full validation gate before any transaction submission |
| 3 | OAuth Token Lifecycle | sequence | Token request, caching strategy, and refresh |
| 4 | Coverages API Lifecycle | sequence | 270/271 async polling from POST to result |
| 5 | Claim Statuses API Lifecycle | sequence | 276/277 POST-as-GET + multi-record polling |
| 6 | Service Reviews State Machine | stateDiagram | All 278 PA status codes and transitions |
| 7 | Service Reviews Full Sequence | sequence | POST → poll → pend/resubmit → approve/deny |
| 8 | Payer List Decision Flow | flowchart | Enrollment, API support, and contract checks |
| 9 | Configurations Field Validation | flowchart | Conditional logic evaluation order per Element |
| 10 | End-to-End Clinical Workflow | flowchart | Scheduling → eligibility → PA → service → AR |
| 11 | API Comparison Matrix | erDiagram | Key properties side-by-side across all 5 APIs |
| 12 | requiredFieldCombinations Logic | flowchart | OR-group member identification validation |

---

## 1 — API Ecosystem Overview

```mermaid
---
title: "Exp 47 · Availity API Ecosystem Overview"
---
flowchart TD
    PMS["🏥 PMS / EHR\nPractice Management System"]

    subgraph disco["Discovery Layer  (read-only · synchronous · cache daily)"]
        PL["Payer List API\n/epdm-payer-list-aws/v1\nscope: aws-availity-payer-list"]
        CFG["Configurations API\n/v1/configurations\nscope: healthcare-hipaa-transactions"]
    end

    subgraph tx["Transaction Layer  (async · poll for result)"]
        COV["Coverages API\n/v1/coverages\nX12 270/271 · Eligibility"]
        CS["Claim Statuses API\n/v1/claim-statuses\nX12 276/277 · AR Follow-up"]
        SR["Service Reviews API\n/v2/service-reviews\nX12 278 · Prior Auth"]
    end

    AUTH["OAuth 2.0 Token\nhttps://api.availity.com/v1/token\nClient Credentials  TTL=5 min"]

    PMS -->|"1  Which payers/transactions?"| PL
    PMS -->|"2  What fields are required?"| CFG
    PMS -->|"3a  Pre-service eligibility"| COV
    PMS -->|"3b  Post-service AR follow-up"| CS
    PMS -->|"3c  Pre-service prior auth"| SR

    PL -.->|"payerId confirmed"| CFG
    CFG -.->|"field rules applied"| COV
    CFG -.->|"field rules applied"| CS
    CFG -.->|"field rules applied"| SR

    AUTH -.->|"Bearer token"| PL
    AUTH -.->|"Bearer token"| CFG
    AUTH -.->|"Bearer token"| COV
    AUTH -.->|"Bearer token"| CS
    AUTH -.->|"Bearer token"| SR

    style disco fill:#e3f2fd,stroke:#1976D2,color:#000
    style tx fill:#e8f5e9,stroke:#388E3C,color:#000
    style AUTH fill:#fff8e1,stroke:#F57F17,color:#000
    style PMS fill:#f3e5f5,stroke:#7B1FA2,color:#000
```

---

## 2 — Pre-Submission Validation Pipeline

```mermaid
---
title: "Exp 47 · Pre-Submission Validation Pipeline"
---
flowchart TD
    START(["Start: PMS has data\nto submit for a patient"])

    step1["Step 1 — Payer List API\nGET /epdm-payer-list-aws/v1/availity-payer-list\n?payerId={id}&transactionType={tx}&submissionMode=API"]
    chk1{Payer supports\ntransaction via API?}
    enrolled{Enrollment\nrequired?}
    enrollcheck{Enrollment\non file?}

    step2["Step 2 — Configurations API\nGET /v1/configurations\n?type={coverages|service-reviews|claim-statuses}\n&payerId={id}"]
    validate["Step 3 — Local Validation\n• Element required / allowed rules\n• Conditional rules requiredWhen / notAllowedWhen\n• minLength / maxLength / pattern\n• requiredFieldCombinations OR-groups"]
    chk2{Validation\npassed?}

    step3a["Step 4a — Coverages API\nPOST /v1/coverages"]
    step3b["Step 4b — Claim Statuses API\nPOST /v1/claim-statuses"]
    step3c["Step 4c — Service Reviews API\nPOST /v2/service-reviews"]

    poll["Poll GET /{api}/{id}\nuntil terminal status"]

    err_payer["Block submission\nLog: payer not API-capable\nFallback: portal / batch"]
    err_enroll["Block submission\nAlert staff:\ncomplete enrollment first"]
    err_val["Return field-level\nerror messages to UI\nCorrect and retry"]

    done(["Result stored in PMS\ncertificationNumber / statusCode\nadjudication / benefit data"])

    START --> step1
    step1 --> chk1
    chk1 -->|"No"| err_payer
    chk1 -->|"Yes"| enrolled
    enrolled -->|"Yes"| enrollcheck
    enrolled -->|"No"| step2
    enrollcheck -->|"Not enrolled"| err_enroll
    enrollcheck -->|"Enrolled"| step2
    step2 --> validate
    validate --> chk2
    chk2 -->|"Errors found"| err_val
    chk2 -->|"Pass"| step3a
    chk2 -->|"Pass"| step3b
    chk2 -->|"Pass"| step3c
    step3a --> poll
    step3b --> poll
    step3c --> poll
    poll --> done

    style err_payer fill:#ffebee,stroke:#c62828,color:#000
    style err_enroll fill:#ffebee,stroke:#c62828,color:#000
    style err_val fill:#fff3e0,stroke:#e65100,color:#000
    style done fill:#e8f5e9,stroke:#2e7d32,color:#000
    style START fill:#e8eaf6,stroke:#3949ab,color:#000
```

---

## 3 — OAuth 2.0 Token Lifecycle

```mermaid
---
title: "Exp 47 · OAuth 2.0 Token Lifecycle"
---
sequenceDiagram
    participant PMS as PMS / Client App
    participant Cache as Token Cache
    participant Auth as Availity Token Endpoint<br/>/v1/token
    participant API as Availity API

    PMS->>Cache: Check for valid token
    alt Token exists and age < 4.5 min
        Cache-->>PMS: Return cached token
    else No token or expiring
        PMS->>Auth: POST /v1/token<br/>grant_type=client_credentials<br/>client_id + client_secret + scope
        Auth-->>PMS: access_token (TTL=300s)
        PMS->>Cache: Store token with timestamp
        Cache-->>PMS: Cached (effective TTL=270s)
    end

    PMS->>API: Request with Authorization: Bearer {token}
    alt Token valid
        API-->>PMS: 200/202 Response
    else Token expired
        API-->>PMS: 401 Unauthorized
        PMS->>Cache: Evict expired token
        PMS->>Auth: POST /v1/token (refresh)
        Auth-->>PMS: New access_token
        PMS->>Cache: Store new token
        PMS->>API: Retry request with new token
        API-->>PMS: 200/202 Response
    end

    Note over Cache: Effective cache TTL = 270s (4.5 min)<br/>Hard TTL from Availity = 300s (5 min)<br/>30s buffer prevents mid-request expiry
    Note over Auth: Scopes vary by API:<br/>aws-availity-payer-list (Payer List)<br/>healthcare-hipaa-transactions (all others)
```

---

## 4 — Coverages API (270/271) Async Polling Lifecycle

```mermaid
---
title: "Exp 47 · Coverages API (270/271) — Async Polling Lifecycle"
---
sequenceDiagram
    participant PMS as PMS
    participant COV as Coverages API<br/>/v1/coverages
    participant PAY as Payer Clearinghouse

    PMS->>COV: POST /v1/coverages<br/>Content-Type: application/x-www-form-urlencoded<br/>payerId + memberId + providerNpi + serviceType...

    alt Cached result exists
        COV-->>PMS: 200 OK — CoverageSummary<br/>statusCode="4" (Complete)
        Note over PMS: Skip polling — result ready
    else New request submitted
        COV-->>PMS: 202 Accepted — CoverageSummary<br/>id={coverageId}  statusCode="0" (In Progress)
    end

    loop Poll until terminal
        PMS->>COV: GET /v1/coverages/{id}
        alt statusCode = "0" In Progress
            COV-->>PMS: 202 — CoverageSummary  statusCode="0"
            Note over PMS: Wait 2-3s, retry
        else statusCode = "1" Retrying
            COV-->>PAY: Re-attempting payer connection
            COV-->>PMS: 202 — CoverageSummary  statusCode="1"
            Note over PMS: Wait 3-5s, retry
        else statusCode = "4" Complete
            COV-->>PMS: 200 OK — Full Coverage object<br/>benefits[], deductibles, copays, coInsurance
            Note over PMS: Terminal — extract benefit data
        else statusCode = "R" Request Error
            COV-->>PMS: 200 — Coverage  statusCode="R"<br/>errors[] with field-level detail
            Note over PMS: Terminal — fix and resubmit
        else statusCode = "E" Comm Error
            COV-->>PMS: 200 — Coverage  statusCode="E"
            Note over PMS: Terminal — retry later
        end
    end

    PMS->>PMS: Store eligibility result<br/>memberId, planGroupNumber,\ndeductible amounts, benefit details
    PMS->>COV: DELETE /v1/coverages/{id}
    COV-->>PMS: 204 No Content

    Note over COV: Demo scenarios:<br/>Coverages-Complete-i → 200, statusCode=4<br/>Coverages-InProgress-i → 202, statusCode=0<br/>Coverages-RequestError1-i → 400
```

---

## 5 — Claim Statuses API (276/277) Lifecycle

```mermaid
---
title: "Exp 47 · Claim Statuses API (276/277) — Async Polling Lifecycle"
---
sequenceDiagram
    participant PMS as PMS
    participant CS as Claim Statuses API<br/>/v1/claim-statuses
    participant PAY as Payer

    Note over PMS,CS: POST masquerades as search due to HIPAA query-string length limits
    PMS->>CS: POST /v1/claim-statuses<br/>Header: X-HTTP-Method-Override: GET  ← REQUIRED<br/>Content-Type: application/x-www-form-urlencoded<br/>payer.id + subscriber.memberId + fromDate + toDate<br/>(or claimNumber + claimAmount)

    CS-->>PMS: ResultSet<br/>claimStatuses[] — array of ClaimStatusSummary<br/>Each has its own id for polling

    Note over PMS: May return 1..N summaries<br/>Poll each id independently

    loop For each claimStatus.id
        PMS->>CS: GET /v1/claim-statuses/{id}
        alt statusCode = "4" (Pending/In Progress)
            CS-->>PMS: 202 or summary  statusCode="4"
            Note over PMS: Wait 2-3s, retry
        else Terminal status reached
            CS-->>PMS: 200 OK — Full ClaimStatus<br/>claimStatusResults[].statusDetails[]<br/>categoryCode, checkNumber, paymentAmount<br/>remittanceDate, serviceLines[]
        end
    end

    PMS->>PMS: For each result — extract adjudication
    Note over PMS: categoryCode F1 = Finalized/Paid<br/>categoryCode F2 = Finalized/Denied<br/>categoryCode F3 = Revised<br/>P1-P4 = Pending variants<br/>A1-A8 = Acknowledgements

    PMS->>CS: DELETE /v1/claim-statuses/{id}
    CS-->>PMS: 200 OK  ← returns 200 not 204

    Note over CS: Key difference vs Coverages API:<br/>Returns array not single record<br/>DELETE returns 200 not 204<br/>Contains adjudication/payment data<br/>No benefit/deductible data
```

---

## 6 — Service Reviews API (278) State Machine

```mermaid
---
title: "Exp 47 · Service Reviews API (278) — State Machine"
---
stateDiagram-v2
    [*] --> Submitted : POST /v2/service-reviews\n202 Accepted

    Submitted --> InProgress : Payer processing\nstatusCode = P1

    InProgress --> Approved : statusCode = A1\nCertified in Total
    InProgress --> PartialApproval : statusCode = A3\nCertified Partial
    InProgress --> Denied : statusCode = A4\nDenied
    InProgress --> Modified : statusCode = A6\nModified by Payer
    InProgress --> Pended : statusCode = PD or WR\nAdditional Info Required
    InProgress --> ContactPayer : statusCode = CT\nContact Payer
    InProgress --> NoAuthRequired : statusCode = NA\nNo Auth Needed

    Pended --> Updated : PUT /v2/service-reviews\nupdatable = true\nAdd diagnoses / notes
    Updated --> InProgress : Payer re-evaluates

    Approved --> Voided : DELETE /v2/service-reviews/{id}\ndeletable = true\n202 Accepted or 204
    PartialApproval --> Voided : DELETE /v2/service-reviews/{id}
    Voided --> [*] : statusCode = VO

    Approved --> [*] : Store certificationNumber\neffectiveDate / expirationDate\nEnable scheduling
    PartialApproval --> [*] : Store partial auth\nAlert staff re: limitations
    Denied --> [*] : Denial management workflow\nStore denial reasons
    Modified --> [*] : Review payer changes\nStore modified auth
    NoAuthRequired --> [*] : Proceed without auth
    ContactPayer --> [*] : Alert staff to call payer

    note right of Pended
        WR = Waiting for Additional Info
        PD = Pend
        Staff must attach clinical docs
        and PUT to resubmit
    end note

    note right of Approved
        Extract from response:
        certificationNumber
        certificationEffectiveDate
        certificationExpirationDate
        procedures[n].certificationNumber
    end note
```

---

## 7 — Service Reviews API — Full PA Workflow with Pend-Resubmit

```mermaid
---
title: "Exp 47 · Service Reviews API — Full PA Workflow with Pend-Resubmit"
---
sequenceDiagram
    participant Staff as Clinical Staff
    participant PMS as PMS
    participant SR as Service Reviews API<br/>/v2/service-reviews
    participant PAY as Payer

    PMS->>SR: POST /v2/service-reviews<br/>Content-Type: application/json<br/>requestTypeCode=AR + procedures[] + diagnoses[]<br/>requestingProvider + subscriber + patient

    SR-->>PMS: 202 Accepted<br/>Location: /v2/service-reviews/{id}

    loop Poll until terminal
        PMS->>SR: GET /v2/service-reviews/{id}
        SR->>PAY: Forward to payer
        PAY-->>SR: Payer response

        alt statusCode = P1 (Pending)
            SR-->>PMS: 202 — still processing
            Note over PMS: Wait 3s, retry
        else statusCode = WR or PD (Pended)
            SR-->>PMS: 200 — ServiceReview<br/>statusCode=WR  updatable=true<br/>payerNotes[] with instructions
            Note over PMS: Alert clinical staff
            Staff->>PMS: Attach additional diagnoses\nclinical notes / documentation
            PMS->>SR: PUT /v2/service-reviews<br/>id={id} + updated diagnoses[]\n+ supplementalInformation.refAuthNumber
            SR-->>PMS: 202 Accepted — re-queued
        else statusCode = A1 (Approved)
            SR-->>PMS: 200 — ServiceReview<br/>certificationNumber\ncertificationEffectiveDate\ncertificationExpirationDate
            Note over PMS: Store auth, enable scheduling
        else statusCode = A3 (Partial)
            SR-->>PMS: 200 — ServiceReview<br/>certificationNumber — partial only\nprocedures[n].statusCode per procedure
            Note over PMS: Flag partial, alert staff
        else statusCode = A4 (Denied)
            SR-->>PMS: 200 — ServiceReview<br/>statusCode=A4\nstatusReasons[] + payerNotes[]
            Note over PMS: Denial mgmt workflow
        end
    end

    opt Void if no longer needed
        PMS->>SR: DELETE /v2/service-reviews/{id}
        SR-->>PAY: Void notification (X12 278 void)
        SR-->>PMS: 202 Accepted or 204 No Content
    end

    Note over SR: Base path: /v2 not /v1<br/>POST body: JSON not form-encoded<br/>ID from Location header not response body<br/>Supports PUT for updates (unique to this API)
```

---

## 8 — Payer List API — Payer Validation Decision Flow

```mermaid
---
title: "Exp 47 · Payer List API — Payer Validation Decision Flow"
---
flowchart TD
    START(["PMS needs to submit\na transaction for a payer"])

    lookup["GET /epdm-payer-list-aws/v1/availity-payer-list\n?payerId={id}"]

    found{Payer found\nin Availity list?}

    api_check{processingRoutes has\nsubmissionMode = API\nfor this transactionType?}

    avail_check{availability = true\nno additional contract\nneeded?}

    enroll_check{enrollmentRequired\n= true?}

    enrolled{Provider enrollment\non file in PMS?}

    notes_check{additionalInfo\nfield populated?}

    log_notes["Log payer-specific notes\nCheck for required GS02 values\nor special submission instructions"]

    err_notfound["Cannot submit via Availity\nLog unknown payer ID\nUse alternate clearinghouse"]

    err_noapisupport["Transaction not API-capable\nFallback: Portal or Batch submission\nLog for manual processing"]

    err_needcontract["Additional Availity contract required\nAlert admin to upgrade contract\nBlock submission"]

    err_notenrolled["Enrollment required but not on file\nAlert staff: complete payer enrollment\nBlock until enrolled"]

    proceed["Proceed to Configurations API\nfor field-level validation\nthen submit to transaction API"]

    START --> lookup
    lookup --> found
    found -->|"No"| err_notfound
    found -->|"Yes"| api_check
    api_check -->|"No"| err_noapisupport
    api_check -->|"Yes"| avail_check
    avail_check -->|"No  contract required"| err_needcontract
    avail_check -->|"Yes  available"| enroll_check
    enroll_check -->|"No  no enrollment needed"| notes_check
    enroll_check -->|"Yes"| enrolled
    enrolled -->|"Not enrolled"| err_notenrolled
    enrolled -->|"Enrolled"| notes_check
    notes_check -->|"Yes"| log_notes
    notes_check -->|"No"| proceed
    log_notes --> proceed

    style err_notfound fill:#ffebee,stroke:#b71c1c,color:#000
    style err_noapisupport fill:#ffebee,stroke:#b71c1c,color:#000
    style err_needcontract fill:#ffebee,stroke:#b71c1c,color:#000
    style err_notenrolled fill:#fff3e0,stroke:#e65100,color:#000
    style proceed fill:#e8f5e9,stroke:#1b5e20,color:#000
    style START fill:#e8eaf6,stroke:#283593,color:#000
```

---

## 9 — Configurations API — Field Validation Decision Tree

```mermaid
---
title: "Exp 47 · Configurations API — Field Validation Decision Tree"
---
flowchart TD
    START(["For each Element\nin Configuration.elements"])

    type_check{Element type?}
    skip["Skip — do not render\nor submit"]
    info_only["Display only —\ndo not submit"]

    not_allowed_when{notAllowedWhen\ncondition matches?}
    err_not_allowed["ERROR: Field must\nnot be submitted\nunder current conditions"]

    allowed_when_exists{allowedWhen\ncondition defined?}
    allowed_when_match{allowedWhen\ncondition matches?}
    err_not_allowed2["ERROR: Field only allowed\nunder specific conditions\nnot currently met"]

    unconditional_allowed{allowed\n= false?}
    err_unconditional["ERROR: Field not\nallowed for this payer"]

    determine_required["Determine if required:"]
    not_req_when{notRequiredWhen\ncondition matches?}
    req_when{requiredWhen\ncondition matches?}
    base_required{required\n= true?}

    has_value{Value\nsubmitted?}
    err_required["ERROR: Required field\nmissing"]

    len_check{minLength or\nmaxLength defined?}
    err_length["ERROR: Length\nviolation"]

    pattern_check{pattern or\npatternWhen defined?}
    err_pattern["ERROR: Value does\nnot match pattern"]

    enum_check{type = Enumeration\nwith values list?}
    err_enum["ERROR: Value not\nin allowed list"]

    VALID(["Field VALID ✓\nNext field"])

    START --> type_check
    type_check -->|"Unsupported"| skip
    type_check -->|"Information"| info_only
    type_check -->|"Text/Number/Date\nBoolean/Enum/Collection\nObject/ObjectArray/Section"| not_allowed_when

    not_allowed_when -->|"Yes"| err_not_allowed
    not_allowed_when -->|"No"| allowed_when_exists

    allowed_when_exists -->|"Yes"| allowed_when_match
    allowed_when_exists -->|"No"| unconditional_allowed
    allowed_when_match -->|"No match"| err_not_allowed2
    allowed_when_match -->|"Matches"| unconditional_allowed

    unconditional_allowed -->|"Yes"| err_unconditional
    unconditional_allowed -->|"No"| determine_required

    determine_required --> not_req_when
    not_req_when -->|"Matches  not required"| has_value
    not_req_when -->|"No match"| req_when
    req_when -->|"Matches  required=true"| has_value
    req_when -->|"No match"| base_required
    base_required -->|"true"| has_value
    base_required -->|"false"| has_value

    has_value -->|"No + required=true"| err_required
    has_value -->|"No + not required"| VALID
    has_value -->|"Yes"| len_check

    len_check -->|"Violation"| err_length
    len_check -->|"OK"| pattern_check

    pattern_check -->|"Violation"| err_pattern
    pattern_check -->|"OK"| enum_check

    enum_check -->|"Value not in list"| err_enum
    enum_check -->|"OK or N/A"| VALID

    style err_not_allowed fill:#ffebee,stroke:#c62828,color:#000
    style err_not_allowed2 fill:#ffebee,stroke:#c62828,color:#000
    style err_unconditional fill:#ffebee,stroke:#c62828,color:#000
    style err_required fill:#fff3e0,stroke:#e65100,color:#000
    style err_length fill:#fff3e0,stroke:#e65100,color:#000
    style err_pattern fill:#fff3e0,stroke:#e65100,color:#000
    style err_enum fill:#fff3e0,stroke:#e65100,color:#000
    style VALID fill:#e8f5e9,stroke:#2e7d32,color:#000
    style skip fill:#f5f5f5,stroke:#9e9e9e,color:#000
    style info_only fill:#f5f5f5,stroke:#9e9e9e,color:#000
    style START fill:#e8eaf6,stroke:#283593,color:#000
```

---

## 10 — End-to-End PMS Clinical Workflow

```mermaid
---
title: "Exp 47 · End-to-End PMS Clinical Workflow"
---
flowchart TD
    SCHED(["Patient Scheduled\nAppointment created in PMS"])

    subgraph preservice["Pre-Service (Day of Scheduling)"]
        E1["Payer List API\nValidate payer supports 270 via API"]
        E2["Configurations API\nFetch coverages field rules for payer"]
        E3["Coverages API — POST /v1/coverages\nCheck eligibility + benefits\nX12 270/271"]
        E3R{Eligible?}
        E3A["Store member benefits\ndeductible, copay, coInsurance\nplanGroupNumber → use for PA"]
        E3B["Alert front desk:\nPatient not eligible\nVerify coverage manually"]

        PA1["Configurations API\nFetch service-reviews rules for payer"]
        PA2["Service Reviews API — POST /v2/service-reviews\nRequest prior authorization\nX12 278"]
        PA3{Auth status?}
        PA3A["Store certificationNumber\neffectiveDate + expirationDate\nEnable visit"]
        PA3B["Alert clinical staff:\nDenied — denial mgmt\nor Pended — attach docs + resubmit"]
    end

    subgraph service["Day of Service"]
        SVC["Render service\nDocument encounter\nCode diagnosis + procedures"]
    end

    subgraph postservice["Post-Service (Claims & AR)"]
        C1["Submit claim\n837P/837I to clearinghouse\nInclude certificationNumber"]
        C2["Configurations API\nFetch claim-statuses field rules"]
        C3["Claim Statuses API — POST /v1/claim-statuses\nAR follow-up\nX12 276/277"]
        C3R{Claim status?}
        C3A["Paid: Post ERA\ncheckNumber + paymentAmount\nremittanceDate"]
        C3B["Denied: Open denial task\nstatusCode + categoryCode F2\nAppeal or write-off"]
        C3C["Pending: Reschedule\ncheck in 3-5 business days\ncategoryCode P1-P4"]
    end

    SCHED --> E1 --> E2 --> E3 --> E3R
    E3R -->|"Eligible"| E3A
    E3R -->|"Not eligible"| E3B
    E3A --> PA1 --> PA2 --> PA3
    PA3 -->|"A1 Approved"| PA3A
    PA3 -->|"A4 Denied\nor WR Pended"| PA3B
    PA3A --> SVC
    E3B -.->|"Manual override\nby front desk"| SVC

    SVC --> C1 --> C2 --> C3 --> C3R
    C3R -->|"F1 Paid"| C3A
    C3R -->|"F2 Denied"| C3B
    C3R -->|"P1-P4 Pending"| C3C
    C3C -.->|"Re-check in\n3-5 days"| C3

    style preservice fill:#e3f2fd,stroke:#1565c0,color:#000
    style service fill:#f3e5f5,stroke:#6a1b9a,color:#000
    style postservice fill:#e8f5e9,stroke:#1b5e20,color:#000
    style SCHED fill:#e8eaf6,stroke:#283593,color:#000
    style E3B fill:#ffebee,stroke:#b71c1c,color:#000
    style PA3B fill:#fff3e0,stroke:#e65100,color:#000
    style C3B fill:#ffebee,stroke:#b71c1c,color:#000
```

---

## 11 — API Comparison Matrix

```mermaid
---
title: "Exp 47 · API Comparison — Key Properties"
---
erDiagram
    PAYER_LIST_API {
        string basePath "/epdm-payer-list-aws/v1"
        string scope "aws-availity-payer-list"
        string methods "GET only"
        string x12 "None — metadata only"
        string async "No — synchronous"
        string responseType "JSON array (no envelope)"
        string cacheStrategy "Daily refresh"
        string primaryKey "payerId"
    }

    CONFIGURATIONS_API {
        string basePath "/v1"
        string scope "healthcare-hipaa-transactions"
        string methods "GET only"
        string x12 "None — validation metadata"
        string async "No — synchronous"
        string responseType "ResultSet with configurations[]"
        string cacheStrategy "Daily refresh"
        string primaryKey "type + payerId"
    }

    COVERAGES_API {
        string basePath "/v1"
        string scope "healthcare-hipaa-transactions"
        string methods "POST GET DELETE"
        string x12 "270/271 Eligibility"
        string async "Yes — poll until statusCode=4"
        string postFormat "application/x-www-form-urlencoded"
        string terminalStatus "statusCode = 4"
        string primaryOutput "benefits[] deductibles copays"
        string deleteReturns "204 No Content"
    }

    CLAIM_STATUSES_API {
        string basePath "/v1"
        string scope "healthcare-hipaa-transactions"
        string methods "POST GET DELETE"
        string x12 "276/277 Claim Status"
        string async "Yes — poll each id"
        string postHeader "X-HTTP-Method-Override: GET required"
        string postFormat "application/x-www-form-urlencoded"
        string terminalStatus "statusCode = 4"
        string responseType "ResultSet — array of summaries"
        string primaryOutput "categoryCode checkNumber paymentAmount"
        string deleteReturns "200 OK"
    }

    SERVICE_REVIEWS_API {
        string basePath "/v2"
        string scope "healthcare-hipaa-transactions"
        string methods "GET POST PUT DELETE GET-by-id"
        string x12 "278 Prior Authorization"
        string async "Yes — poll until named code"
        string postFormat "application/json"
        string idLocation "Location response header"
        string terminalStatus "A1 A3 A4 A6 CA NA VO"
        string primaryOutput "certificationNumber effectiveDate"
        string supportsUpdate "Yes — PUT"
        string deleteReturns "202 or 204"
    }

    PAYER_LIST_API ||--o{ CONFIGURATIONS_API : "payerId feeds into"
    CONFIGURATIONS_API ||--o{ COVERAGES_API : "validates fields for"
    CONFIGURATIONS_API ||--o{ CLAIM_STATUSES_API : "validates fields for"
    CONFIGURATIONS_API ||--o{ SERVICE_REVIEWS_API : "validates fields for"
```

---

## 12 — requiredFieldCombinations Logic

```mermaid
---
title: "Exp 47 · Configurations API — requiredFieldCombinations Logic"
---
flowchart TD
    START(["Evaluate\nrequiredFieldCombinations\nfor all rule groups"])

    subgraph grp["For each named rule group (e.g. memberIdentification)"]
        COMBO["Rule group has N combinations\nAt least ONE must be fully satisfied"]

        subgraph c1["Combination 1 (AND)"]
            F1A["memberId\nprovided?"]
        end
        subgraph c2["Combination 2 (AND)"]
            F2A["patientLastName\nprovided?"]
            F2B["patientFirstName\nprovided?"]
            F2C["patientBirthDate\nprovided?"]
        end
        subgraph c3["Combination 3 (AND)"]
            F3A["patientSSN\nprovided?"]
        end

        OR{"OR — at least\none combo satisfied?"}
    end

    PASS["Rule group PASSES ✓\nContinue to next group"]
    FAIL["Rule group FAILS ✗\nError: must provide one of:\n(memberId)\nOR (lastName + firstName + DOB)\nOR (SSN)"]

    MORE{More rule\ngroups?}
    ALL_PASS(["All combination\nrules satisfied ✓"])

    START --> COMBO
    F1A --> OR
    F2A & F2B & F2C --> OR
    F3A --> OR

    OR -->|"Yes"| PASS
    OR -->|"No"| FAIL

    PASS --> MORE
    MORE -->|"Yes"| COMBO
    MORE -->|"No"| ALL_PASS

    style FAIL fill:#ffebee,stroke:#c62828,color:#000
    style PASS fill:#e8f5e9,stroke:#2e7d32,color:#000
    style ALL_PASS fill:#e8f5e9,stroke:#1b5e20,color:#000
    style START fill:#e8eaf6,stroke:#283593,color:#000
    style c1 fill:#fff9c4,stroke:#f9a825,color:#000
    style c2 fill:#fff9c4,stroke:#f9a825,color:#000
    style c3 fill:#fff9c4,stroke:#f9a825,color:#000
```

---

*Source: Availity Swagger Specifications — Coverages 1.0.0, Claim Statuses 1.0.0, Service Reviews 2.0.0, AWS Payer List 2.0.0, Configurations 1.0.0*  
*Render with: VS Code Mermaid Preview, Mermaid Live Editor (mermaid.live), GitHub markdown, or any Mermaid-compatible tool*
