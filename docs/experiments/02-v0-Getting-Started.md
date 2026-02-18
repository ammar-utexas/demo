# v0 by Vercel — Getting Started Guide

**Document ID:** PMS-EXP-V0-001
**Version:** 1.0
**Date:** 2026-02-16
**Applies To:** `pms-frontend` (Next.js 15 / React 19 / TypeScript / Tailwind CSS 3)

---

## What is v0?

v0 is Vercel's AI-powered generative UI tool. You describe what you want in plain English, and v0 generates production-ready React + Tailwind CSS code. It's purpose-built for the Next.js ecosystem — the exact stack used by `pms-frontend`.

### Why Consider v0 for PMS?

| Benefit | Description |
|---|---|
| **Stack-native** | Generates Next.js / React / TypeScript / Tailwind code — matches `pms-frontend` exactly |
| **Rapid prototyping** | Go from description to working UI in seconds |
| **shadcn/ui integration** | Generates components based on shadcn/ui, the most popular React component library |
| **Copy-paste workflow** | No vendor lock-in — generated code is yours to modify |
| **Iteration via prompts** | Refine the UI by describing changes in natural language |

### v0 vs Storybook

| Aspect | v0 | Storybook |
|---|---|---|
| **Purpose** | Generate new UI code from descriptions | Document and test existing UI components |
| **Input** | Text prompts | Existing component code |
| **Output** | New React components | Interactive component gallery |
| **Best for** | Building new pages and components quickly | Maintaining a component library |
| **Recommendation** | Use v0 to **create** components, then document them in Storybook |

---

## Prerequisites

- A Vercel account (free tier available) — sign up at [vercel.com](https://vercel.com)
- The `pms-frontend` repo cloned with dependencies installed
- Node.js 18+ and npm 9+

---

## Access Methods

### Method 1: Web Interface (Recommended for Exploration)

1. Go to [v0.dev](https://v0.dev)
2. Sign in with your Vercel account
3. Type a prompt describing the UI you want
4. Browse generated variations
5. Click "Code" to copy the React component
6. Paste into your `pms-frontend` project

### Method 2: CLI Integration

Install and use v0 directly from your terminal:

```bash
# Install v0 CLI
npm install -g v0

# Generate a component from a prompt
npx v0 generate "a patient registration form with fields for name, DOB, email, phone, and SSN"
```

### Method 3: VS Code Extension

1. Install the "v0" extension from the VS Code marketplace
2. Open command palette → "v0: Generate Component"
3. Type your prompt
4. Insert generated code directly into your file

---

## How to Use v0 with PMS Frontend

### Step 1: Describe Your Component

Write a clear, specific prompt. Include:
- What the component is (table, form, card, dashboard)
- What data it displays (patient names, encounter statuses, medications)
- Styling preferences (use Tailwind, match existing design)
- Interaction requirements (clickable rows, sort, filter)

### Step 2: Generate and Review

v0 will produce one or more variations. Review the generated code for:
- Compatibility with your existing components (`Button`, `Card`, `Badge`, `Input`)
- Correct use of TypeScript types
- Tailwind classes that match your `primary-*` color palette
- Proper accessibility attributes

### Step 3: Integrate into PMS

1. Copy the generated code
2. Create a new file in the appropriate directory:
   - UI primitives → `src/components/ui/`
   - Layout components → `src/components/layout/`
   - Page components → `src/app/{route}/page.tsx`
3. Replace any shadcn/ui imports with your existing PMS components:
   ```typescript
   // v0 generates:
   import { Button } from "@/components/ui/button"
   // Your PMS project already has this — no change needed!
   ```
4. Adjust the color palette if needed:
   ```typescript
   // v0 might generate generic blue:
   className="bg-blue-600"
   // Replace with your PMS primary:
   className="bg-primary-600"
   ```

### Step 4: Refine with Follow-up Prompts

If the first generation isn't perfect, iterate:
- "Make the table sortable by clicking column headers"
- "Add a loading skeleton state"
- "Change the color scheme to use a blue primary palette"
- "Add pagination controls at the bottom"

---

## Prompt Engineering Tips for PMS

### Be Specific About Domain

```
❌ "Create a table"
✅ "Create a patient records table with columns for name, DOB, email, gender,
   and status (active/inactive badge). Include a search bar at the top and
   an 'Add Patient' button in the header. Use Tailwind CSS."
```

### Reference HIPAA Context

```
✅ "Create a clinical encounter form for a HIPAA-compliant healthcare app.
   Include fields for patient (dropdown), encounter type (office visit,
   telehealth, emergency, follow-up), date/time, provider, and clinical
   notes textarea. Add a status badge showing 'Scheduled'."
```

### Specify Existing Components

```
✅ "Create a medication management page using these existing components:
   - Button (variants: primary, secondary, danger, ghost)
   - Badge (variants: success, warning, danger, info)
   - Card with CardHeader, CardTitle, CardContent
   - Input with label and error props
   Show a table of prescriptions with drug interaction severity badges."
```

### Request Specific States

```
✅ "Create a patient detail page with three states:
   1. Loading state with skeleton placeholders
   2. Loaded state showing patient demographics, encounters list, and medications
   3. Error state with a retry button"
```

---

## Adapting v0 Output to PMS Conventions

### Import Paths

v0 generates standard shadcn/ui imports which align with your project:

```typescript
// v0 output — usually compatible as-is:
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
```

### Component API Differences

Your PMS components may have slightly different APIs than shadcn/ui defaults. Common adjustments:

| v0 Output | PMS Equivalent | Change Needed |
|---|---|---|
| `<Button variant="default">` | `<Button variant="primary">` | Rename variant |
| `<Button variant="outline">` | `<Button variant="secondary">` | Rename variant |
| `<Button variant="destructive">` | `<Button variant="danger">` | Rename variant |
| `<Badge variant="secondary">` | `<Badge variant="default">` | Rename variant |
| `<Badge variant="destructive">` | `<Badge variant="danger">` | Rename variant |
| `<Input />` (no label prop) | `<Input label="..." />` | Add label prop |

### Color Palette

Replace generic Tailwind colors with your PMS primary palette:

```
bg-blue-600  →  bg-primary-600
text-blue-700  →  text-primary-700
border-blue-500  →  border-primary-500
ring-blue-500  →  ring-primary-500
```

### Adding "use client"

v0 generates server components by default. If the component uses:
- `useState`, `useEffect`, or other hooks
- `onClick` or other event handlers
- `useRouter`, `usePathname`

Add `"use client";` at the top of the file.

---

## Limitations

| Limitation | Workaround |
|---|---|
| Generated code may need API wiring | Integrate with your `src/lib/api.ts` client |
| May not match your exact component API | Adjust variant names and props (see table above) |
| No direct database/backend integration | Use as UI layer only; connect to FastAPI endpoints separately |
| Free tier has generation limits | Use paid plan for heavy usage, or iterate carefully |
| May generate extra dependencies | Remove unused imports; prefer your existing components |

---

## Next Steps

- Read the [v0 Developer Tutorial](02-v0-Developer-Tutorial.md) for PMS-specific generation prompts
- Try generating a component at [v0.dev](https://v0.dev)
- Compare v0 output with existing `pms-frontend` components for compatibility
