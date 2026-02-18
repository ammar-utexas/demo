# Banani Developer Tutorial for PMS

**Document ID:** PMS-EXP-BANANI-002
**Version:** 1.0
**Date:** 2026-02-16
**Applies To:** PMS project (web frontend + Android app)
**Prerequisite:** [Banani Getting Started Guide](03-Banani-Getting-Started.md)

---

## Overview

This tutorial provides ready-to-use Banani prompts for designing every major screen in the PMS application — both web and Android. Each section includes the prompt, what to look for in the output, and how to use the design downstream.

---

## Part 1: Web Frontend Designs (pms-frontend)

### 1.1 Login Page

**Prompt:**
```
Design a login page for a Patient Management System (PMS).
HIPAA-compliant healthcare application.

Layout:
- Centered card on a light gray (#f9fafb) background
- App title "Patient Management System" in bold, dark text
- Subtitle "Sign in to access patient records" in gray
- Username input field with label
- Password input field with label and visibility toggle icon
- Full-width "Sign In" button in primary blue (#2563eb)
- Error message area in red below the button
- Footer: "Protected by HIPAA Security Standards" in small gray text

Style: Clean, professional, modern healthcare. White card with subtle shadow.
No decorative elements — focus on trust and clarity.
```

**What to look for:** Clean form layout, proper label alignment, clear error state placement, professional healthcare feel.

---

### 1.2 Dashboard

**Prompt:**
```
Design a dashboard page for a HIPAA-compliant Patient Management System.

Layout:
- Fixed left sidebar (256px wide) with navigation:
  Logo "PMS" at top, links: Dashboard (active, blue highlight),
  Patients, Encounters, Medications, Reports
- Top header bar with "Patient Management System" text and "Sign out" button
- Main content area with light gray background

Content:
- Row of 4 stats cards:
  1. "Total Patients" = 1,247 (+12% this month, green)
  2. "Today's Encounters" = 38 (5 in progress, blue)
  3. "Active Prescriptions" = 892 (3 interaction alerts, yellow)
  4. "Pending Reports" = 7 (2 overdue, gray)
- Below: two cards side by side
  Left: "Recent Patients" — list of 3 patients with name, registration date,
        and Active badge (green)
  Right: "Today's Encounters" — list of 3 encounters with patient name, type,
         and status badges (green=completed, yellow=in progress, blue=scheduled)

Colors: Primary #2563eb, Success #16a34a, Warning #ca8a04, Danger #dc2626
```

**What to look for:** Balanced layout, readable stats, clear badge colors, proper sidebar highlighting.

---

### 1.3 Patient List Page

**Prompt:**
```
Design a patient records list page for a healthcare management system.

Layout: Same sidebar + header as dashboard. Patients link active in sidebar.

Content:
- Header row: "Patients" title (large, bold) + "Add Patient" blue button (right)
- Search bar below header: full width, placeholder "Search by name, email,
  or patient ID..."
- White card containing a data table:
  Columns: Name, Date of Birth, Email, Gender, Status, Actions
  Status column: green "Active" or red "Inactive" badge
  Actions column: "View" (secondary button) and "Edit" (ghost button)
  Show 6 rows of realistic patient data (mix of genders, ages, statuses)
- Pagination at bottom: "Showing 1-6 of 1,247 patients" with Previous/Next buttons

Style: Clean table with subtle row borders. Hover state on rows.
```

---

### 1.4 Patient Detail Page

**Prompt:**
```
Design a patient detail page for a healthcare management system.

Layout: Same sidebar + header. Patients link active in sidebar.

Content:
- Breadcrumb: Patients > John Doe
- Header: Patient name "John Doe", green "Active" badge, and buttons:
  "Edit" (secondary), "Deactivate" (danger/red)
- Demographics card:
  Two-column grid: First Name, Last Name, Date of Birth, Gender, Email,
  Phone. No SSN displayed — show "SSN: ••••••••• (encrypted)" in gray italic.
- Three tabs below:
  Tab 1 "Encounters": table with Date, Type, Provider, Status badge, View button
  Tab 2 "Medications": table with Drug, Dosage, Prescriber, Status badge, Refills
  Tab 3 "Audit Log": table with Timestamp, User, Action, Details

Show Tab 1 as active with 3 encounter rows.
```

---

### 1.5 Patient Registration Form

**Prompt:**
```
Design a new patient registration form for a HIPAA-compliant healthcare system.

Layout: Same sidebar + header. Patients link active in sidebar.

Content:
- Breadcrumb: Patients > New Patient
- Title: "Register New Patient"
- White card with form fields in two-column grid:
  Row 1: First Name (required*), Last Name (required*)
  Row 2: Date of Birth (date picker, required*), Gender (dropdown: Male/Female/Other)
  Row 3: Email (required*, unique), Phone
  Row 4: SSN (masked input, note below: "Encrypted at rest per HIPAA §164.312")
- Validation: show one field with a red border and error message:
  "Email already exists in the system"
- Footer buttons: "Save Patient" (primary blue), "Cancel" (secondary gray)

Include a note at the top: "Fields marked with * are required"
```

---

### 1.6 Encounter List Page

**Prompt:**
```
Design an encounters list page for a healthcare management system.

Layout: Same sidebar + header. Encounters link active in sidebar.

Content:
- Header: "Encounters" title + "New Encounter" blue button
- Filter bar: Date range picker, Type dropdown (All/Office Visit/Telehealth/
  Emergency/Follow Up), Status dropdown (All/Scheduled/In Progress/Completed/
  Cancelled)
- Data table in white card:
  Columns: Patient, Type, Provider, Date/Time, Status, Actions
  Status badges: blue=Scheduled, yellow=In Progress, green=Completed,
  red=Cancelled
  Show 8 rows with mixed statuses and types
- Pagination at bottom

Show the filter bar with "All" selected for both dropdowns.
```

---

### 1.7 Medication Management Page

**Prompt:**
```
Design a medications page for a healthcare prescription management system.

Layout: Same sidebar + header. Medications link active in sidebar.

Content:
- Warning banner at top (yellow background, orange border):
  "⚠ 3 potential drug interactions detected — Review required"
  With a "Review Interactions" button
- Header: "Medications" title + "New Prescription" blue button
- Data table in white card:
  Columns: Medication, Dosage, Frequency, Patient, Prescriber, Status, Refills
  Status badges: green=Active, gray=Completed, red=Cancelled
  Show 6 rows with realistic medication names (Amoxicillin 500mg, Lisinopril
  10mg, Metformin 850mg, Warfarin 5mg, Omeprazole 20mg, Ibuprofen 400mg)
- Drug Interaction Detail card below the table:
  Show 3 interactions:
  1. Warfarin + Ibuprofen — Severity: "Major" (red badge) — "Increased bleeding risk"
  2. Lisinopril + Metformin — Severity: "Moderate" (yellow badge) — "Monitor renal function"
  3. Amoxicillin + Omeprazole — Severity: "Minor" (blue badge) — "Reduced absorption possible"
```

---

### 1.8 Reports Dashboard

**Prompt:**
```
Design a reports and analytics dashboard for a healthcare management system.

Layout: Same sidebar + header. Reports link active in sidebar.

Content:
- Header: "Reports & Analytics" title + "Export CSV" button (secondary)
- Date range selector: tabs for "Last 7 Days", "Last 30 Days", "Last 90 Days",
  "Custom Range"
- Stats cards row (4 cards):
  1. Total Patients: 1,247 (+12% vs previous period)
  2. Encounters: 342 (breakdown: 180 office, 95 telehealth, 42 follow-up, 25 emergency)
  3. Prescriptions: 892 (3 interaction alerts)
  4. Audit Events: 15,847 (logged actions this period)
- Two chart placeholder areas side by side:
  Left: "Patient Registrations Over Time" with a simple line chart sketch
  Right: "Encounters by Type" with a donut chart sketch
- Bottom section: "Recent Audit Log" table:
  Columns: Timestamp, User, Action (Created/Read/Updated/Deleted), Resource Type,
  Resource ID
  Show 5 rows of audit data
```

---

## Part 2: Android App Designs (pms-android)

### 2.1 Android Login Screen

**Prompt:**
```
Design a native Android login screen for a Patient Management System.
Material Design 3 style.

Layout:
- Centered content on white background
- App icon placeholder (blue medical cross) at top
- "Patient Management System" title
- "Sign in to continue" subtitle in gray
- Username text field (Material outlined style)
- Password text field with visibility toggle
- Full-width "Sign In" filled button in blue (#2563eb)
- Error message in red below button
- Bottom text: "HIPAA Compliant" in small gray

Style: Material Design 3, clean, professional. Android system font.
Show as a phone frame (360x800).
```

---

### 2.2 Android Patient List

**Prompt:**
```
Design a native Android patient list screen for a healthcare app.
Material Design 3 style. Phone frame (360x800).

Layout:
- Top app bar: "Patients" title, search icon, floating action button (blue +)
  for adding patients
- Search bar (expandable from icon)
- Scrollable list of patient cards:
  Each card shows: Patient name (bold), email (gray), DOB (gray)
  Right side: green "Active" or red "Inactive" chip/badge
  Chevron icon indicating tap to view detail
- Show 5 patient entries
- Bottom navigation bar: Dashboard, Patients (active/blue), Encounters,
  Medications, Reports

Style: Material Design 3 with proper elevation and spacing.
```

---

### 2.3 Android Patient Detail

**Prompt:**
```
Design a native Android patient detail screen for a healthcare app.
Material Design 3 style. Phone frame (360x800).

Layout:
- Top app bar: back arrow, "John Doe" title, overflow menu (Edit, Deactivate)
- Status chip: green "Active"
- Demographics section (Material card):
  Two-column grid: First Name, Last Name, DOB, Gender, Email, Phone
  SSN: "••••••••• (encrypted)" in gray italic
- Tab bar: Encounters | Medications | Audit Log
- Encounters tab active: list of 3 encounter cards
  Each shows: Type, Provider, Date, Status chip (color-coded)
- Bottom navigation bar (same as patient list)

Style: Material Design 3, clean layout, proper card elevation.
```

---

### 2.4 Android Encounter List

**Prompt:**
```
Design a native Android encounters screen for a healthcare app.
Material Design 3 style. Phone frame (360x800).

Layout:
- Top app bar: "Encounters" title, filter icon, FAB (blue +) for new encounter
- Filter chips row (horizontally scrollable):
  "All" (selected/filled), "Scheduled", "In Progress", "Completed", "Cancelled"
- Scrollable list of encounter cards:
  Each card: Patient name (bold), encounter type (subtitle), date/time (gray)
  Right side: status chip (blue=Scheduled, yellow=In Progress, green=Completed,
  red=Cancelled)
- Show 5 encounter entries with mixed statuses
- Bottom navigation bar

Style: Material Design 3 with filter chips and proper card layout.
```

---

### 2.5 Android Medications Screen

**Prompt:**
```
Design a native Android medications screen for a healthcare app.
Material Design 3 style. Phone frame (360x800).

Layout:
- Top app bar: "Medications" title, FAB (blue +) for new prescription
- Warning banner (yellow/amber card at top):
  "⚠ 3 drug interactions detected" with "Review" text button
- Scrollable list of medication cards:
  Each card: Drug name + dosage (bold), patient name (subtitle),
  prescriber (gray), refills remaining
  Right side: status chip (green=Active, gray=Completed, red=Cancelled)
- Show 4 medication entries
- Bottom navigation bar

Style: Material Design 3, warning banner should be prominent but not alarming.
```

---

## Part 3: Design System Screens

### 3.1 Component Reference Sheet

**Prompt:**
```
Design a UI component reference sheet for a healthcare design system.
Web layout, full width.

Show all components used in the system:

1. Buttons row: Primary (blue), Secondary (gray), Danger (red), Ghost (text only)
   In three sizes: Small, Medium, Large. Also show Disabled state.

2. Badges row: Default (gray), Success (green), Warning (yellow),
   Danger (red), Info (blue). Label each with its use case.

3. Input fields: Default, With Label, With Error (red border + message),
   Disabled, Date picker, Password with toggle

4. Cards: Basic card, Card with header and title, Patient summary card,
   Stats card with number and trend

5. Color palette: Primary blue shades (50-950), Success green, Warning yellow,
   Danger red, Neutral grays

Title: "PMS Design System — Component Reference"
```

---

### 3.2 Full App Flow Prototype

**Prompt:**
```
Design a complete user flow for a Patient Management System (web).
Show 6 connected screens as a storyboard:

1. Login page → user enters credentials
2. Dashboard → shows stats and recent activity
3. Patient List → user clicks "View" on a patient
4. Patient Detail → user sees demographics and encounters
5. New Encounter → user fills out encounter form for this patient
6. Encounter Confirmation → success message with encounter details

Show arrows connecting the screens to indicate navigation flow.
Use consistent sidebar + header layout across screens 2-6.
Primary blue (#2563eb), clean healthcare style.
```

---

## Part 4: Working with Banani Output

### Exporting to Figma

1. Select the design you want to export
2. Click "Export" → "Figma"
3. The design will be importable as a Figma file
4. In Figma, you can:
   - Refine spacing and alignment
   - Add interaction prototyping (click flows)
   - Generate a shareable prototype link
   - Use as developer handoff with inspect mode

### Using Designs as v0 Reference

Combine Banani + v0 for the best workflow:

1. Generate the visual design in Banani
2. Export as an image (PNG)
3. In v0, use the image as reference:
   ```
   "Create a React + TypeScript + Tailwind component that matches this design:
   [paste image or describe what Banani generated]
   Use these existing components: Button (variants: primary/secondary/danger/ghost),
   Badge (variants: default/success/warning/danger/info), Card, Input."
   ```
4. v0 generates code that matches the Banani design
5. Adapt and integrate into `pms-frontend`

### Using Designs for Stakeholder Reviews

1. Generate all key screens in Banani
2. Create a clickable prototype linking screens together
3. Share the prototype URL with stakeholders
4. Collect feedback before writing any code
5. Iterate on designs based on feedback
6. Once approved, proceed to code generation

---

## Part 5: Screen Inventory for PMS

Complete list of screens to design, organized by priority:

### Priority 1 — Core Screens (Design First)

| # | Screen | Platform | Subsystem |
|---|---|---|---|
| 1 | Login | Web + Android | Auth |
| 2 | Dashboard | Web + Android | All |
| 3 | Patient List | Web + Android | SUB-PR |
| 4 | Patient Detail | Web + Android | SUB-PR |
| 5 | Patient Registration Form | Web + Android | SUB-PR |

### Priority 2 — Clinical Workflow

| # | Screen | Platform | Subsystem |
|---|---|---|---|
| 6 | Encounter List | Web + Android | SUB-CW |
| 7 | Encounter Detail | Web + Android | SUB-CW |
| 8 | New Encounter Form | Web + Android | SUB-CW |

### Priority 3 — Medication Management

| # | Screen | Platform | Subsystem |
|---|---|---|---|
| 9 | Medication List | Web + Android | SUB-MM |
| 10 | Prescription Form | Web + Android | SUB-MM |
| 11 | Drug Interaction Checker | Web | SUB-MM |

### Priority 4 — Reporting & Analytics

| # | Screen | Platform | Subsystem |
|---|---|---|---|
| 12 | Reports Dashboard | Web + Android | SUB-RA |
| 13 | Audit Log Viewer | Web | SUB-RA |

### Priority 5 — Design System

| # | Screen | Platform | Subsystem |
|---|---|---|---|
| 14 | Component Reference Sheet | Web | All |
| 15 | Full App Flow Storyboard | Web + Android | All |

---

## Part 6: Best Practices

### Design Quality

| Do | Don't |
|---|---|
| Use consistent colors across all screens | Mix different blue shades |
| Include status badges on every list view | Leave status ambiguous |
| Show both populated and empty states | Only design the happy path |
| Design for both web and Android | Assume one design fits both |
| Include error states (validation, 404, network) | Skip edge cases |

### Healthcare-Specific

| Do | Don't |
|---|---|
| Mask SSN fields in all designs | Show SSN in plain text |
| Include HIPAA compliance notes | Ignore regulatory context |
| Use professional, subdued colors | Use bright/playful design |
| Show role-based differences (what a nurse sees vs admin) | Design one view for all roles |
| Include audit trail visibility | Hide data access history |

### Workflow

| Do | Don't |
|---|---|
| Design before coding | Code without visual reference |
| Get stakeholder approval on designs | Skip review step |
| Use Banani for exploration, Figma for refinement | Over-invest in Banani polish |
| Export designs for developer handoff | Keep designs only in Banani |

---

## Next Steps

1. Create a Banani account at [banani.co](https://www.banani.co/)
2. Start with the Login and Dashboard prompts (Part 1)
3. Generate Android versions of the same screens (Part 2)
4. Export approved designs to Figma
5. Use designs as reference for v0 code generation (Part 4)
6. Compare Banani workflow vs v0-only workflow to decide which to adopt

---

## Sources

- [Banani — Generate UI from Text](https://www.banani.co/)
- [Banani AI UI Generator](https://www.banani.co/product/ai-ui-generator)
- [Banani AI App Design Generator](https://www.banani.co/product/ai-app-design-generator)
- [Banani Review — AI Chief](https://aichief.com/ai-text-tools/banani/)
