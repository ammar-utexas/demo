# v0 Developer Tutorial for PMS Frontend

**Document ID:** PMS-EXP-V0-002
**Version:** 1.0
**Date:** 2026-02-16
**Applies To:** `pms-frontend` (Next.js 15 / React 19 / TypeScript / Tailwind CSS 3)
**Prerequisite:** [v0 Getting Started Guide](02-v0-Getting-Started.md)

---

## Overview

This tutorial provides ready-to-use v0 prompts for generating every major UI component and page in the PMS frontend. Each section includes the prompt, expected output, and instructions for adapting the generated code to your project.

---

## Part 1: Generating UI Components

### 1.1 Patient Registration Form

**Prompt:**
```
Create a patient registration form for a healthcare application using React,
TypeScript, and Tailwind CSS. Include these fields:
- First Name (text, required)
- Last Name (text, required)
- Date of Birth (date picker, required)
- Gender (select: Male, Female, Other)
- Email (email, required, must be unique)
- Phone (tel)
- SSN (password-masked input, labeled "SSN — encrypted at rest")

Include form validation with inline error messages below each field.
Add "Save Patient" (primary) and "Cancel" (secondary) buttons at the bottom.
Use a clean, minimal healthcare design with a white card on a gray background.
```

**After generating, adapt:**
1. Replace `<Button variant="default">` → `<Button variant="primary">`
2. Replace `<Button variant="outline">` → `<Button variant="secondary">`
3. Use your `<Input label="..." error="..." />` component instead of raw inputs
4. Replace generic blue with `primary-600` / `primary-700`
5. Add `"use client";` at top (form uses state)
6. Save to `src/app/patients/new/page.tsx`

---

### 1.2 Patient Detail View

**Prompt:**
```
Create a patient detail page for a HIPAA-compliant healthcare app.
Layout: sidebar navigation on the left (already exists), main content area.

The main content should have:
1. Header with patient name, status badge (Active/Inactive), and action buttons
   (Edit, Deactivate)
2. Demographics card: name, DOB, gender, email, phone (no SSN displayed)
3. Encounters tab: table with columns Date, Type (office visit, telehealth,
   emergency, follow-up), Provider, Status (scheduled/in_progress/completed/cancelled
   as colored badges), Actions (View button)
4. Medications tab: table with columns Medication, Dosage, Prescriber, Status
   (active/completed/cancelled badges), Refills Remaining
5. Audit Log tab: table with columns Timestamp, User, Action, Details

Use React, TypeScript, Tailwind CSS. Use tabs to switch between sections.
```

**After generating, adapt:**
1. Import your existing `Badge`, `Button`, `Card`, `Input` components
2. Wire up API calls to `src/lib/api.ts`
3. Add `"use client";` directive
4. Save to `src/app/patients/[id]/page.tsx`

---

### 1.3 Encounter Management Page

**Prompt:**
```
Create an encounter management page for a healthcare patient management system.
React + TypeScript + Tailwind CSS.

Include:
1. Page header: "Encounters" title + "New Encounter" button
2. Filter bar: date range picker, encounter type dropdown (All, Office Visit,
   Telehealth, Emergency, Follow Up), status dropdown (All, Scheduled,
   In Progress, Completed, Cancelled)
3. Data table with columns:
   - Patient Name
   - Encounter Type
   - Provider
   - Date/Time
   - Status (colored badges: blue=scheduled, yellow=in_progress,
     green=completed, red=cancelled)
   - Actions (View, Edit buttons)
4. Pagination controls at the bottom (Previous, Page 1 2 3, Next)

Show 10 rows of realistic mock data with mixed statuses.
```

**After generating, adapt:**
1. Map badge colors to your variants: `info`=scheduled, `warning`=in_progress, `success`=completed, `danger`=cancelled
2. Connect filter dropdowns to API query parameters
3. Replace pagination with your API's cursor/offset pattern
4. Save to `src/app/encounters/page.tsx`

---

### 1.4 Medication Prescriptions Page

**Prompt:**
```
Create a medication management page for a HIPAA-compliant healthcare app.
React + TypeScript + Tailwind CSS.

Include:
1. Header: "Medications" title + "New Prescription" button
2. Active Prescriptions table:
   - Drug Name, Dosage, Frequency, Patient, Prescriber, Start Date,
     Status (active/completed/cancelled badges), Refills Remaining
3. Drug Interaction Alert banner at the top (dismissible):
   - Show a yellow warning card: "3 potential drug interactions detected"
   - List interactions with severity badges (contraindicated=red, major=red,
     moderate=yellow, minor=blue)
   - Each interaction shows the two drugs involved and a brief description
4. Prescription detail modal when clicking a row:
   - Full prescription info, interaction warnings, refill history

Use realistic medication names (Amoxicillin, Lisinopril, Metformin, etc.).
```

**After generating, adapt:**
1. Map severity badges to your `Badge` variants
2. Connect to interaction checker API (`/api/medications/interactions`)
3. Save to `src/app/medications/page.tsx`

---

### 1.5 Reports Dashboard

**Prompt:**
```
Create a reports dashboard for a healthcare management system.
React + TypeScript + Tailwind CSS.

Include:
1. Header: "Reports & Analytics" title + "Export CSV" button
2. Date range selector at the top (Last 7 Days, Last 30 Days, Last 90 Days,
   Custom Range)
3. Stats cards row:
   - Total Patients (with % change)
   - Total Encounters (with breakdown by type)
   - Active Prescriptions (with interaction alert count)
   - Audit Events (total logged actions)
4. Two charts side by side (use placeholder chart areas with descriptive labels):
   - "Patient Registrations Over Time" (line chart placeholder)
   - "Encounters by Type" (pie/donut chart placeholder)
5. Bottom section: "Recent Audit Log" table:
   - Timestamp, User, Action (Created/Read/Updated/Deleted), Resource Type
     (Patient/Encounter/Medication), Resource ID

Use a clean analytics dashboard design.
```

**After generating, adapt:**
1. Replace chart placeholders with a charting library (e.g., Recharts)
2. Wire stats to report API endpoints
3. Connect audit log to `/api/reports/audit`
4. Save to `src/app/reports/page.tsx`

---

### 1.6 Login Page

**Prompt:**
```
Create a login page for a HIPAA-compliant Patient Management System.
React + TypeScript + Tailwind CSS.

Include:
1. Centered card on a light gray background
2. App logo/title: "Patient Management System" with a healthcare icon
3. Subtitle: "Sign in to access patient records"
4. Username input with label
5. Password input with label and show/hide toggle
6. "Sign In" primary button (full width)
7. Error message area (red text below button): "Invalid credentials"
8. Footer text: "Protected by HIPAA Security Standards"

Make it professional and clean, suitable for a healthcare institution.
```

---

## Part 2: Generating Layout Components

### 2.1 Application Shell

**Prompt:**
```
Create an application shell layout for a healthcare management system.
React + TypeScript + Tailwind CSS.

Layout:
- Fixed left sidebar (w-64) with:
  - App name "PMS" at top in bold blue
  - Navigation links: Dashboard, Patients, Encounters, Medications, Reports
  - Active link has blue background, inactive is gray
  - User info at bottom: avatar circle, name, role badge
- Top header bar with:
  - Breadcrumb trail (e.g., Patients > John Doe)
  - Right side: notification bell with count badge, "Sign out" button
- Main content area with gray background and padding

Show the Dashboard as the active page.
```

---

## Part 3: Generating Complex Workflows

### 3.1 New Encounter Wizard

**Prompt:**
```
Create a multi-step encounter creation wizard for a healthcare app.
React + TypeScript + Tailwind CSS.

Steps:
1. Select Patient: searchable patient dropdown with recent patients shown
2. Encounter Details: type (office visit, telehealth, emergency, follow-up),
   date/time picker, provider dropdown
3. Clinical Notes: large textarea with character count, optional chief complaint field
4. Review & Submit: summary card showing all entered data with Edit buttons per section

Include:
- Step indicator bar at the top (1-2-3-4 with labels)
- Back / Next buttons at the bottom
- Active step highlighted in blue, completed steps with green checkmark
- Form validation before allowing next step
```

---

### 3.2 Patient Search with Results

**Prompt:**
```
Create a patient search component for a healthcare app.
React + TypeScript + Tailwind CSS.

Include:
1. Search bar with icon, placeholder "Search by name, DOB, or patient ID"
2. Advanced filters collapsible panel:
   - Gender dropdown, Age range, Status (Active/Inactive), Date range
3. Results table that updates as you type:
   - Columns: Name, DOB, Gender, Email, Status badge, Last Visit date
   - Clickable rows that would navigate to patient detail
4. Result count: "Showing 5 of 1,247 patients"
5. Empty state when no results: "No patients match your search"
6. Loading state: skeleton rows while searching

Show realistic mock data with 5 patients.
```

---

### 3.3 Drug Interaction Checker

**Prompt:**
```
Create a drug interaction checker component for a healthcare prescription system.
React + TypeScript + Tailwind CSS.

Include:
1. Two medication selector dropdowns (searchable)
2. "Check Interactions" button
3. Results panel showing:
   - Severity badge (Contraindicated=red, Major=red, Moderate=yellow, Minor=blue)
   - Drug pair (e.g., "Warfarin + Aspirin")
   - Description of the interaction
   - Clinical recommendation
4. "Override with Justification" section:
   - Textarea for clinical justification
   - Prescriber signature (name + role display)
   - "Confirm Override" danger button
5. Warning banner if contraindicated: "This combination is contraindicated.
   Override requires documented clinical justification."

Show 3 mock interactions with different severities.
```

---

## Part 4: Workflow — From Prompt to Production

### Step-by-Step Process

```
1. Write prompt          → Describe the UI you need
2. Generate on v0.dev    → Get React + Tailwind code
3. Copy to project       → Paste into appropriate file
4. Adapt imports         → Use your existing Button, Card, Badge, Input
5. Fix color palette     → Replace generic blue with primary-*
6. Add "use client"      → If component uses hooks/events
7. Wire API calls        → Connect to src/lib/api.ts
8. Add TypeScript types  → Import from src/types/
9. Write tests           → Add test in __tests__/
10. Add Storybook story  → Document in .stories.tsx
```

### Example: Patient List Page End-to-End

```bash
# 1. Generate on v0.dev with the Patient List prompt from 1.1

# 2. Create the file
touch src/app/patients/page.tsx

# 3. Paste and adapt the generated code

# 4. Add TypeScript types
```

```typescript
// src/app/patients/page.tsx
"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import type { Patient } from "@/types/patient";

// ... paste adapted v0 code here, using your types and components
```

```bash
# 5. Write a test
touch __tests__/patients-page.test.tsx

# 6. Add a Storybook story
touch src/stories/pages/patient-list.stories.tsx
```

---

## Part 5: Prompt Templates

### Generic Page Template

```
Create a [PAGE_NAME] page for a HIPAA-compliant Patient Management System.
React + TypeScript + Tailwind CSS.

Include:
1. Page header with title "[PAGE_TITLE]" and [ACTION_BUTTON] button
2. [FILTER/SEARCH description]
3. Data table with columns: [COLUMN_LIST]
4. [STATUS_BADGES description]
5. Pagination controls
6. Empty state when no data

Use realistic mock healthcare data.
Color palette: primary blue (#2563eb), success green, warning yellow, danger red.
```

### Generic Form Template

```
Create a [FORM_NAME] form for a healthcare application.
React + TypeScript + Tailwind CSS.

Fields:
[LIST_ALL_FIELDS with types and validation rules]

Include:
- Form validation with inline error messages
- Required field indicators
- Submit button (primary) and Cancel button (secondary)
- Loading state on submit
- Success/error toast notification

Wrap in a Card component with a clean healthcare design.
```

### Generic Detail Page Template

```
Create a [ENTITY] detail page for a healthcare management system.
React + TypeScript + Tailwind CSS.

Include:
1. Header with [ENTITY] name, status badge, and action buttons (Edit, Delete)
2. Details card with [FIELD_LIST]
3. Related data tabs: [TAB_LIST with table descriptions]
4. Loading skeleton state
5. Back button to return to list

Use realistic mock data.
```

---

## Part 6: Best Practices

### Prompt Quality

| Do | Don't |
|---|---|
| Be specific about fields and columns | Use vague descriptions like "a nice table" |
| Mention "React + TypeScript + Tailwind CSS" | Assume v0 knows your stack |
| Describe states (loading, empty, error) | Only describe the happy path |
| Reference healthcare domain context | Use generic business terms |
| Specify badge colors for statuses | Leave status styling ambiguous |

### Integration Quality

| Do | Don't |
|---|---|
| Replace v0 components with your existing ones | Keep duplicate component implementations |
| Use your `primary-*` color palette | Leave generic Tailwind blues |
| Add proper TypeScript types from `src/types/` | Leave `any` types in generated code |
| Wire to your API client (`src/lib/api.ts`) | Hardcode mock data in production code |
| Add `"use client"` when needed | Forget client directive for interactive components |

### Security

- **Never include real PHI** in prompts — v0 is a cloud service
- **Review generated code** for XSS vulnerabilities (e.g., `dangerouslySetInnerHTML`)
- **Validate all inputs** — don't trust v0 to add proper validation
- **Check for hardcoded secrets** — ensure no API keys or tokens in generated code

---

## Next Steps

1. Try generating the Patient Registration Form (Section 1.1) at [v0.dev](https://v0.dev)
2. Adapt the output to use your existing PMS components
3. Compare the result with your current `src/app/patients/page.tsx`
4. If the approach works well, generate remaining pages from the prompts above
5. Document generated components in Storybook (see [Storybook Tutorial](01-Storybook-Developer-Tutorial.md))
