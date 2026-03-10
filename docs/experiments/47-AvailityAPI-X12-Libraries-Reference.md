# X12 / EDI Python Libraries & Tools Reference
**Experiment 47 · PMS Integration · MPS Inc.**  
Last Updated: March 2026

---

## Table of Contents

1. [Critical Context for Exp 47](#1-critical-context-for-exp-47)
2. [Library Comparison Matrix](#2-library-comparison-matrix)
3. [Recommended: linuxforhealth-x12](#3-recommended-linuxforhealth-x12)
4. [Alternative: TigerShark3](#4-alternative-tigershark3)
5. [Simple/Generic: badX12](#5-simplegeneric-badx12)
6. [High-Level Wrapper: x12-edi-tools](#6-high-level-wrapper-x12-edi-tools)
7. [Avoid: pyx12](#7-avoid-pyx12)
8. [Avoid: python-x12 (not found)](#8-avoid-python-x12-not-found)
9. [Developer Tooling (Non-Library)](#9-developer-tooling-non-library)
10. [When You Actually Need an X12 Parser in Exp 47](#10-when-you-actually-need-an-x12-parser-in-exp-47)
11. [memberId Extraction — Availity REST JSON Path](#11-memberid-extraction--availity-rest-json-path)

---

## 1. Critical Context for Exp 47

> **You may not need an X12 parser at all.**

Availity's Coverages API (270/271) returns a **structured JSON response** — not raw X12 EDI text. The `memberId` needed to call the E&B Value-Add APIs (Care Reminders, Member ID Card) is available directly from the JSON polling response.

An X12 parser is only necessary if **one or more** of the following is true:

| Trigger | Description |
|---|---|
| Raw 271 batch files | Receiving raw X12 text from a payer directly (not via Availity REST) |
| Second clearinghouse | Integrating a non-Availity path alongside the Availity REST path |
| Raw payload inspection | Validating or auditing the underlying EDI that Availity wraps |
| Offline/HIPAA compliance testing | Parsing locally captured X12 files for test fixtures |

**For the current Exp 47 scope (Availity REST only), skip the X12 parser dependency and extract `memberId` from the JSON response directly.** See [Section 11](#11-memberid-extraction--availity-rest-json-path) for the JSON path.

---

## 2. Library Comparison Matrix

| Library | PyPI Package | Status | Python | 271 Support | Pydantic | Last Release |
|---|---|---|---|---|---|---|
| **linuxforhealth-x12** | `linuxforhealth-x12` | ✅ Active | 3.8+ | ✅ Full 5010 | ✅ Yes | 2024 |
| **TigerShark3** | `TigerShark3` | ✅ Active | 3.x | ✅ Yes | ❌ No | 2024 |
| **x12-edi-tools** | `x12-edi-tools` | ⚠️ Thin | 3.x | ✅ 270/271 | ❌ No | 2024 |
| **badX12** | `badX12` | ⚠️ Generic | 3.x | ⚠️ Generic only | ❌ No | 2024 |
| **spaceavocado-x12** | `spaceavocado-x12` | ⚠️ Minimal | 3.7+ | ⚠️ Generic only | ❌ No | ~2022 |
| **pyx12** | `pyx12` | ❌ Dead | 2.7/3.4/3.5 | ✅ (but abandoned) | ❌ No | Aug 2017 |
| **python-x12** | *(not on PyPI)* | ❌ Not found | — | — | — | — |

---

## 3. Recommended: `linuxforhealth-x12`

**→ Use this if you need an X12 parser in Exp 47.**

### Overview

LinuxForHealth x12 is the most modern, production-grade Python X12 library available. It was built specifically for ASC X12 5010 healthcare transactions — the standard Availity uses — and integrates cleanly into FastAPI-based Python stacks via Pydantic models.

- **GitHub:** https://github.com/LinuxForHealth/x12
- **PyPI:** https://pypi.org/project/linuxforhealth-x12/
- **License:** Apache 2.0
- **Maintainer:** LinuxForHealth (IBM open source health project)
- **Status:** Actively maintained as of 2024

### Supported Transaction Types

| Transaction | Description |
|---|---|
| 270 | Eligibility Benefit Inquiry |
| 271 | Eligibility Benefit Response ← **key for Exp 47** |
| 834 | Benefit Enrollment |
| 835 | Claim Payment / Remittance |
| 837P | Professional Claim |
| 837I | Institutional Claim |

### Installation

```bash
pip install linuxforhealth-x12

# Optional: FastAPI endpoint
pip install "linuxforhealth-x12[api]"
```

### Segment Streaming (Low-level)

Parses each segment into a list of fields — useful for custom extraction logic.

```python
from linuxforhealth.x12.io import X12SegmentReader

with X12SegmentReader("271_response.x12") as r:
    for segment_name, segment_fields in r.segments():
        print(segment_name)    # e.g. "NM1", "REF", "EB"
        print(segment_fields)  # list of field values
```

### Model Streaming (Recommended — Typed Pydantic Models)

Validates and deserializes the X12 payload into structured Pydantic models with typed fields.

```python
from linuxforhealth.x12.io import X12ModelReader

with X12ModelReader("271_response.x12") as r:
    for model in r.models():
        print(model.header)   # ISA/GS envelope
        print(model.footer)   # IEA/GE envelope
        # Convert back to raw X12 string
        raw = model.x12()
```

### Extract memberId from Raw 271 (X12 Segment Path)

In a raw X12 271 response, the member ID appears in the `NM1` segment of the subscriber loop (`2100C`) or patient loop (`2100D`), specifically in element `NM109`.

```python
from linuxforhealth.x12.io import X12SegmentReader

def extract_member_id_from_271(x12_text: str) -> str | None:
    """
    Extract the subscriber/member ID from a raw X12 271 response.
    The member ID is in the NM1 segment, element NM109 (index 9),
    within Loop 2100C (Subscriber Name) or 2100D (Patient Name).
    """
    import io
    reader = X12SegmentReader(io.StringIO(x12_text))
    in_subscriber_loop = False

    for segment_name, fields in reader.segments():
        # Loop 2100C starts with NM1 where NM101 = "IL" (Insured or Subscriber)
        if segment_name == "NM1":
            entity_code = fields[1] if len(fields) > 1 else ""
            if entity_code in ("IL", "1"):  # IL = subscriber, 1 = insured
                in_subscriber_loop = True
                member_id = fields[9] if len(fields) > 9 else None
                if member_id:
                    return member_id
        elif segment_name in ("SE", "GE", "IEA"):
            in_subscriber_loop = False

    return None
```

### CLI Usage

```bash
# Parse to segments
lfhx12 -s 271_response.x12

# Parse to models (validates against 5010 schema)
lfhx12 -m 271_response.x12

# Pretty print
lfhx12 -m -p 271_response.x12
```

### Optional FastAPI Endpoint

```bash
# Install with API extra
pip install "linuxforhealth-x12[api]"

# Start server
lfhx12-api

# POST raw X12 text to: http://localhost:5000/x12
# Swagger UI at: http://localhost:5000/docs
```

### Pros & Cons

| ✅ Pros | ⚠️ Cons |
|---|---|
| ASC X12 5010 compliant (Availity's standard) | Heavier dependency than simple parsers |
| Pydantic models → clean FastAPI integration | Optional API endpoint is "experimental" |
| Streaming I/O → handles large batch files | Documentation is sparse on 271-specific field extraction |
| Apache 2.0 license — safe for commercial use | Schema definitions inherited from pyx12 project |
| CLI included for dev/debugging | |

---

## 4. Alternative: `TigerShark3`

### Overview

TigerShark3 is a Python X12 EDI parser that transforms X12 schema definitions into Python class definitions. It has 270/271 support and is actively maintained. Uses schema definitions sourced from the pyx12 project.

- **GitHub:** https://github.com/jdavisp3/TigerShark
- **PyPI:** https://pypi.org/project/TigerShark3/
- **License:** Apache 2.0
- **Status:** Active, production-used (2024)

### Installation

```bash
pip install TigerShark3
```

### Basic Usage — Parse 271

```python
from tigershark.facade.f271 import F271

with open("271_response.x12") as f:
    raw = f.read()

parsed = F271(raw)

for subscriber in parsed.subscribers:
    print(subscriber.member_id)       # NM109
    print(subscriber.last_name)       # NM103
    print(subscriber.first_name)      # NM104
    print(subscriber.date_of_birth)   # DMG02
```

### Pros & Cons

| ✅ Pros | ⚠️ Cons |
|---|---|
| Actively maintained | No Pydantic — plain Python classes |
| 271-specific facade (typed access) | Less aligned to FastAPI ecosystem |
| Lighter than linuxforhealth-x12 | Complex 271 loop structures noted as tricky |
| Good for 835 remittance too | |

---

## 5. Simple/Generic: `badX12`

### Overview

A lightweight Python library for parsing any ANSI ASC X12 file to a generic document object. No transaction-specific typed models. Useful for inspecting raw segment structures or converting to JSON/XML for debugging.

- **GitHub:** https://github.com/git-albertomarin/badX12
- **PyPI:** https://pypi.org/project/badX12/
- **License:** MIT
- **Status:** Maintained (2024)

### Installation

```bash
pip install badX12
```

### Basic Usage

```python
from badx12 import Parser

parser = Parser()
document = parser.parse_document("271_response.edi")

for interchange in document.interchanges:
    for group in interchange.groups:
        for transaction in group.transaction_sets:
            for segment in transaction.segments:
                print(segment.segment_id, segment.elements)
```

### CLI — Convert to JSON or XML

```bash
# Parse to JSON (default output: ~/Documents/badX12/)
badx12 parse "271_response.edi"

# Parse to XML
badx12 parse "271_response.edi" -e XML -o "./output/"
```

### Pros & Cons

| ✅ Pros | ⚠️ Cons |
|---|---|
| Dead-simple API | No 271-specific typed models |
| CLI JSON/XML export for debugging | Must manually navigate segment structure |
| MIT license | Not ideal for production extraction logic |
| No heavy dependencies | |

---

## 6. High-Level Wrapper: `x12-edi-tools`

### Overview

A newer library with a clean, opinionated API specifically for common healthcare EDI transactions. Provides high-level classes for eligibility (270/271), remittance (835), and JSON/CSV conversion.

- **GitHub:** https://github.com/copyleftdev/x12-edi-tools
- **PyPI:** https://pypi.org/project/x12-edi-tools/
- **License:** MIT
- **Status:** Single contributor — vet before adopting

### Installation

```bash
pip install x12-edi-tools
```

### 270/271 Usage

```python
from x12_edi_tools.eligibility_checker import EligibilityChecker

checker = EligibilityChecker()

# Build a 270 request
request = checker.create_270_request(patient_data)

# Parse a 271 response
response = checker.process_271_response(response_data)
print(f"Patient eligible: {response.is_eligible}")
print(f"Member ID: {response.member_id}")
```

### JSON/CSV Conversion

```python
from x12_edi_tools.x_12_converter import X12Converter

converter = X12Converter()
json_data = converter.to_json("271_response.edi")
csv_data  = converter.to_csv("271_response.edi")
```

### Pros & Cons

| ✅ Pros | ⚠️ Cons |
|---|---|
| Cleanest 270/271 high-level API | Single-contributor — bus factor = 1 |
| `is_eligible` and `member_id` directly | Internals not well documented |
| MIT license | Vet test coverage before relying on it |
| Includes 270 request building | |

---

## 7. Avoid: `pyx12`

> ❌ **Do not use for new development.**

### Why It's Listed

`pyx12` was the most widely referenced Python X12 library for years and still appears in tutorials, Stack Overflow answers, and older GitHub projects. It also serves as the schema source for both linuxforhealth-x12 and TigerShark3. You will encounter it — this entry is here to explain why to avoid adopting it directly.

- **PyPI:** https://pypi.org/project/pyx12/
- **GitHub:** https://github.com/azoner/pyx12
- **Last Release:** August 17, 2017 (v2.3.3)
- **Python Support:** 2.7, 3.4, 3.5 only
- **Status:** ❌ Abandoned / Inactive

### Why Abandoned

The maintainer (John Holland / azoner) stopped active development after 2017. No Python 3.6+ wheel exists. Snyk and Socket both flag it as inactive with no recent PyPI releases or PR activity.

### What To Do Instead

If you find code using `pyx12` in existing integrations:

| pyx12 usage | Replace with |
|---|---|
| Validation / schema checking | `linuxforhealth-x12` (Pydantic validation) |
| X12 → XML conversion | `badX12` CLI or `linuxforhealth-x12` |
| 271 parsing | `linuxforhealth-x12` or `TigerShark3` |
| Schema files (`.se` files) | Already bundled in linuxforhealth-x12 |

---

## 8. Avoid: `python-x12` (Not Found)

> ❌ **This package does not exist on PyPI or GitHub as a standalone library.**

The name `python-x12` and `pyx12` are sometimes used interchangeably in articles and blog posts, but there is no PyPI package named `python-x12`. Searches return no matching repository or distribution.

If you encounter a reference to `python-x12` in documentation or tutorials:
- It is almost certainly referring to `pyx12` (see Section 7)
- Or it may be a private/internal package at the organization that wrote the docs
- Use `linuxforhealth-x12` instead

---

## 9. Developer Tooling (Non-Library)

These are tools useful during development and debugging — not Python libraries to import.

### `edicat` — CLI Prettifier for Raw X12

Adds newlines to raw X12 files (which have no line breaks by default) so they are readable in a terminal or editor.

```bash
pip install edicat

# Prettify a raw X12 file
edicat 271_response.x12

# Number lines
edicat -n 271_response.x12

# Works with stdin
cat 271_response.x12 | edicat
```

**PyPI:** https://pypi.org/project/edicat/ | Last release: 2024

---

### EDI Lens — Browser-Based X12 Inspector

A web-based tool for viewing and parsing X12 EDI files visually. No install required.

- **URL:** https://edilen.s (search "EDI Lens")
- **Use:** Paste raw X12 text, get a structured tree view — useful for understanding 271 loop/segment layout before writing parser logic

---

### VS Code Extension — EDI Support

`hellooops.edi-support` — VS Code extension providing syntax highlighting and language support for X12/HIPAA and EDIFACT files.

- **Install:** VS Code Extensions → search "EDI Support"
- **Use:** Syntax highlight raw `.x12` / `.edi` files during development

---

### `pyedi` — JSONata-Based X12 → JSON Transformer

For teams that want to map X12 to a custom schema using JSONata expressions rather than writing Python field extraction code.

```bash
pip install pyedi
```

```python
from pyedi import X12Pipeline

pipeline = X12Pipeline()
result = pipeline.transform(
    edi_file="271_response.edi",
    mapping="mapping_271_to_pms.json"  # JSONata mapping file
)
```

**PyPI:** https://pypi.org/project/pyedi/ | Wraps linuxforhealth-x12 internally.

---

## 10. When You Actually Need an X12 Parser in Exp 47

For most of Exp 47's current scope, **the Availity REST API returns JSON and no X12 parser is needed**. Here is the decision table:

| Scenario | Need X12 Parser? | Recommended Library |
|---|---|---|
| Parsing Availity `/v1/coverages` JSON response for `memberId` | ❌ No | Plain JSON (`response.json()`) |
| Availity returns raw X12 271 in response body (rare) | ✅ Yes | `linuxforhealth-x12` |
| Receiving 271 batch files from payer directly | ✅ Yes | `linuxforhealth-x12` |
| Integrating a second non-Availity clearinghouse | ✅ Yes | `linuxforhealth-x12` |
| Inspecting raw X12 payload for debugging | ✅ Dev only | `edicat` (CLI) + `badX12` |
| Writing test fixtures from real 271 samples | ✅ One-time | `badX12` CLI → JSON |
| Validating 270 requests before sending | ⚠️ Optional | `linuxforhealth-x12` |

---

## 11. memberId Extraction — Availity REST JSON Path

When using the Availity Coverages REST API, `memberId` is in the polling (`GET`) response JSON. **No X12 parser required.**

### JSON Response Structure (statusCode 4 = Complete)

```json
{
  "id": "7276849100383928590",
  "status": "Complete",
  "statusCode": "4",
  "coverages": [
    {
      "subscriber": {
        "memberId": "XYZ123456789",
        "lastName": "DOE",
        "firstName": "JOHN",
        "dateOfBirth": "1990-01-01",
        "groupNumber": "GRP001"
      },
      "payer": {
        "id": "00611",
        "name": "Regence BlueShield of Idaho"
      },
      "planStatus": "Active"
    }
  ]
}
```

### Python Extraction Utility

```python
# app/services/availity_api.py

def extract_member_id(coverage_response: dict) -> str | None:
    """
    Extract memberId from the Availity GET /v1/coverages/{id} JSON response.
    Returns None if response is not complete or memberId is not present.
    """
    if coverage_response.get("statusCode") != "4":
        return None  # Not complete yet — keep polling

    coverages = coverage_response.get("coverages", [])
    if not coverages:
        return None

    subscriber = coverages[0].get("subscriber", {})
    return subscriber.get("memberId")


def extract_member_details(coverage_response: dict) -> dict:
    """
    Extract all relevant member fields needed for E&B Value-Add API calls.
    """
    if coverage_response.get("statusCode") != "4":
        return {}

    coverages = coverage_response.get("coverages", [])
    if not coverages:
        return {}

    coverage = coverages[0]
    subscriber = coverage.get("subscriber", {})
    payer = coverage.get("payer", {})

    return {
        "memberId":    subscriber.get("memberId"),
        "firstName":   subscriber.get("firstName"),
        "lastName":    subscriber.get("lastName"),
        "dateOfBirth": subscriber.get("dateOfBirth"),
        "groupNumber": subscriber.get("groupNumber"),
        "payerId":     payer.get("id"),
        "planStatus":  coverage.get("planStatus"),
    }
```

### Integration Flow

```python
# After polling coverages to statusCode=4, pass directly to value-add APIs

coverage = await poll_coverages_until_complete(coverage_id)
member   = extract_member_details(coverage)

if member.get("memberId") and member.get("payerId"):
    care_reminders = await get_care_reminders(
        payer_id  = member["payerId"],
        member_id = member["memberId"],
        first_name = member.get("firstName"),
        last_name  = member.get("lastName"),
    )
    member_card = await initiate_member_id_card(
        payer_id  = member["payerId"],
        member_id = member["memberId"],
        dob       = member.get("dateOfBirth"),
    )
```

---

## Quick Reference

| Task | Tool |
|---|---|
| Parse 271 in production code | `pip install linuxforhealth-x12` |
| Parse 271 with typed facade | `pip install TigerShark3` |
| Convert X12 file → JSON (one-shot) | `pip install badX12` + CLI |
| Prettify raw X12 in terminal | `pip install edicat` |
| Inspect X12 visually (browser) | EDI Lens (web tool) |
| Map X12 → custom schema via JSONata | `pip install pyedi` |
| High-level 270/271 (vet first) | `pip install x12-edi-tools` |
| Extract memberId from Availity JSON | No library — use `response["coverages"][0]["subscriber"]["memberId"]` |

---

*Sources: PyPI, GitHub, Snyk Advisor, Socket.dev — verified March 2026*
