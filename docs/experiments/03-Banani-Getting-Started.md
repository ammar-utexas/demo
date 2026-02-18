# Banani.co — Getting Started Guide

**Document ID:** PMS-EXP-BANANI-001
**Version:** 1.0
**Date:** 2026-02-16
**Applies To:** PMS project (all platforms — web, Android, system design)

---

## What is Banani?

[Banani](https://www.banani.co/) is an AI-powered UI design platform that generates interactive UI designs, wireframes, and clickable prototypes from text descriptions. Unlike v0 (which generates code), Banani focuses on the **visual design layer** — producing editable mockups and prototypes that can be exported to Figma for further refinement.

### Why Consider Banani for PMS?

| Benefit | Description |
|---|---|
| **Text-to-UI generation** | Describe a screen in plain English, get a polished UI design in seconds |
| **No design skills required** | Product managers, developers, and stakeholders can create professional mockups |
| **Figma integration** | Export directly to Figma for pixel-perfect refinement and handoff |
| **Clickable prototypes** | Generate interactive prototypes for stakeholder demos and usability testing |
| **Web + mobile designs** | Generate designs for both the web frontend and Android app |
| **Real-time collaboration** | Multiple team members can work on designs simultaneously |
| **Style customization** | Apply consistent brand colors, typography, and design tokens |

### Banani vs v0 vs Storybook

| Aspect | Banani | v0 | Storybook |
|---|---|---|---|
| **Output** | Visual designs, wireframes, prototypes | React + Tailwind code | Interactive component gallery |
| **Primary use** | Design exploration and stakeholder approval | Code generation | Component documentation and testing |
| **Input** | Text prompts, references, PRDs | Text prompts | Existing component code |
| **Figma integration** | Native export | None | None |
| **Code output** | No (design only) | Yes (React/TypeScript) | N/A (uses existing code) |
| **Best for** | Early-stage design, non-technical stakeholders | Developers building UI | Maintaining a component library |
| **Recommended workflow** | Design in Banani → Export to Figma → Implement with v0 → Document in Storybook |

---

## Prerequisites

- A Banani account — sign up at [banani.co](https://www.banani.co/) (free tier available)
- Optionally: a Figma account for design export and refinement
- Familiarity with PMS subsystems and requirements (see `docs/specs/system-spec.md`)

---

## Pricing

| Plan | Price | Features |
|---|---|---|
| **Free** | $0/month | Generate and edit UI designs, limited generations |
| **Premium** | $20/month | Advanced features, more generations, priority support |

The free tier is sufficient for exploration and initial prototyping.

---

## Getting Started

### Step 1: Create an Account

1. Go to [banani.co](https://www.banani.co/)
2. Sign up with email or Google account
3. Complete onboarding (select "Healthcare" as your industry if prompted)

### Step 2: Create a New Project

1. Click "New Project"
2. Name it "PMS — Patient Management System"
3. Set the design context:
   - **Platform:** Web (for `pms-frontend`) or Mobile (for `pms-android`)
   - **Style:** Clean, minimal, professional healthcare UI
   - **Colors:** Primary blue (#2563eb), white backgrounds, gray text

### Step 3: Generate Your First Design

Enter a prompt describing the screen you want. Example:

```
Design a patient list page for a HIPAA-compliant healthcare management system.
Include a search bar at the top, a table with columns for patient name, date of
birth, email, gender, and status (Active shown as a green badge, Inactive as red).
Add an "Add Patient" button in the header. Use a clean, professional healthcare
design with a white card on a light gray background. Blue primary color (#2563eb).
```

### Step 4: Review and Refine

Banani will generate one or more design variations. You can:
- **Select** the variation you prefer
- **Edit** by refining your prompt: "Make the search bar wider and add filter dropdowns for gender and status"
- **Customize** colors, typography, and spacing in the visual editor

### Step 5: Export

Export your design for the next step in the workflow:

| Export Option | Use Case |
|---|---|
| **Figma** | Hand off to designers for pixel-perfect refinement |
| **Image (PNG/SVG)** | Include in documentation or PRDs |
| **Clickable prototype** | Share link with stakeholders for feedback |

---

## Workflow Integration with PMS

### Recommended Design-to-Code Pipeline

```
1. Write PRD / Requirements    → docs/specs/requirements/
2. Generate designs in Banani  → Visual mockups for each screen
3. Export to Figma             → Refine with design team
4. Generate code with v0       → React + Tailwind components
5. Adapt to PMS codebase       → Use existing Button, Card, Badge, Input
6. Document in Storybook       → Interactive component library
7. Write tests                 → Vitest + Testing Library
```

### Design-Requirements Mapping

Use Banani to create designs for each PMS subsystem:

| Subsystem | Screens to Design |
|---|---|
| **Patient Records (SUB-PR)** | Patient list, patient detail, patient registration form, patient search |
| **Clinical Workflow (SUB-CW)** | Encounter list, encounter detail, new encounter wizard |
| **Medication Management (SUB-MM)** | Medication list, prescription form, drug interaction checker |
| **Reporting & Analytics (SUB-RA)** | Dashboard, patient volume report, encounter summary, audit log viewer |
| **Authentication** | Login page, role selection |
| **Layout** | App shell (sidebar + header), navigation |

---

## Prompt Tips for Healthcare UI

### Include HIPAA Context

```
✅ "Design a HIPAA-compliant patient registration form. Do NOT display SSN
   in plain text — use a masked input field. Include a note 'PHI is encrypted
   at rest' below sensitive fields."
```

### Specify Platform

```
# For web (pms-frontend):
✅ "Design a responsive web dashboard for a healthcare management system.
   Desktop layout with a fixed left sidebar navigation."

# For mobile (pms-android):
✅ "Design a native Android mobile app screen for viewing patient records.
   Material Design 3 style with a bottom navigation bar."
```

### Reference Your Color Palette

```
✅ "Use this color palette:
   - Primary: #2563eb (blue)
   - Success: #16a34a (green)
   - Warning: #ca8a04 (yellow)
   - Danger: #dc2626 (red)
   - Background: #f9fafb (light gray)
   - Card background: #ffffff (white)
   - Text: #111827 (near black)"
```

### Describe Badge Styles

```
✅ "Use colored status badges:
   - Active = green badge
   - Inactive = red badge
   - Scheduled = blue badge
   - In Progress = yellow badge
   - Completed = green badge
   - Cancelled = red badge"
```

---

## Limitations

| Limitation | Workaround |
|---|---|
| No code generation | Use v0 or manual coding to implement designs |
| Free tier has generation limits | Prioritize key screens; use paid plan for full project |
| May not match component API exactly | Use designs as visual reference, adapt during implementation |
| No direct React/Next.js export | Export to Figma → use as reference for v0 prompts |
| Limited template variety on free tier | Write detailed prompts to get specific results |

---

## Next Steps

- Read the [Banani Developer Tutorial](03-Banani-Developer-Tutorial.md) for PMS-specific design prompts
- Create a free account at [banani.co](https://www.banani.co/)
- Generate your first design using the patient list prompt above
- Compare with v0 output to decide which fits your workflow better

---

## Sources

- [Banani — Generate UI from Text](https://www.banani.co/)
- [Banani AI UI Generator](https://www.banani.co/product/ai-ui-generator)
- [Banani AI App Design Generator](https://www.banani.co/product/ai-app-design-generator)
- [Banani Review — AI Chief](https://aichief.com/ai-text-tools/banani/)
