# Storybook Developer Tutorial for PMS Frontend

**Document ID:** PMS-EXP-STORYBOOK-002
**Version:** 1.0
**Date:** 2026-02-16
**Applies To:** `pms-frontend` (Next.js 15 / React 19 / TypeScript / Tailwind CSS 3)
**Prerequisite:** [Storybook Getting Started Guide](01-Storybook-Getting-Started.md)

---

## Overview

This tutorial walks you through writing Storybook stories for every component in the PMS frontend. By the end, you'll have a complete, interactive component library that doubles as living documentation.

**What you'll build:**
1. Stories for all 4 UI primitives (Button, Card, Badge, Input)
2. Stories for layout components (Sidebar, Header)
3. Composed page-level stories showing real PMS workflows
4. Interactive stories with actions and controls

---

## Part 1: UI Primitive Stories

### 1.1 Button

The Button component supports 4 variants (`primary`, `secondary`, `danger`, `ghost`) and 3 sizes (`sm`, `md`, `lg`).

Create `src/components/ui/button.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./button";

const meta: Meta<typeof Button> = {
  title: "UI/Button",
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "danger", "ghost"],
      description: "Visual style of the button",
    },
    size: {
      control: "select",
      options: ["sm", "md", "lg"],
      description: "Size of the button",
    },
    disabled: {
      control: "boolean",
      description: "Whether the button is disabled",
    },
    onClick: { action: "clicked" },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// --- Variants ---

export const Primary: Story = {
  args: { children: "Save Patient", variant: "primary", size: "md" },
};

export const Secondary: Story = {
  args: { children: "Cancel", variant: "secondary", size: "md" },
};

export const Danger: Story = {
  args: { children: "Deactivate Patient", variant: "danger", size: "md" },
};

export const Ghost: Story = {
  args: { children: "Sign out", variant: "ghost", size: "md" },
};

// --- Sizes ---

export const Small: Story = {
  args: { children: "Edit", variant: "primary", size: "sm" },
};

export const Large: Story = {
  args: { children: "Create New Patient", variant: "primary", size: "lg" },
};

// --- States ---

export const Disabled: Story = {
  args: { children: "Submit", variant: "primary", disabled: true },
};

// --- Composed: All Variants ---

export const AllVariants: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="danger">Danger</Button>
      <Button variant="ghost">Ghost</Button>
    </div>
  ),
};

// --- Composed: All Sizes ---

export const AllSizes: Story = {
  render: () => (
    <div className="flex items-end gap-4">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
};
```

**Key concepts:**
- `argTypes` with `action: "clicked"` logs click events in the Storybook Actions panel
- `render` function lets you compose multiple components in one story
- `tags: ["autodocs"]` generates an automatic documentation page

---

### 1.2 Badge

The Badge component has 5 variants used throughout PMS for status indicators.

Create `src/components/ui/badge.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "./badge";

const meta: Meta<typeof Badge> = {
  title: "UI/Badge",
  component: Badge,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "success", "warning", "danger", "info"],
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { children: "Draft", variant: "default" },
};

export const Success: Story = {
  args: { children: "Active", variant: "success" },
};

export const Warning: Story = {
  args: { children: "Pending Review", variant: "warning" },
};

export const Danger: Story = {
  args: { children: "Critical", variant: "danger" },
};

export const Info: Story = {
  args: { children: "Scheduled", variant: "info" },
};

// --- PMS-specific status badges ---

export const EncounterStatuses: Story = {
  name: "Encounter Status Badges",
  render: () => (
    <div className="flex gap-2">
      <Badge variant="info">Scheduled</Badge>
      <Badge variant="warning">In Progress</Badge>
      <Badge variant="success">Completed</Badge>
      <Badge variant="danger">Cancelled</Badge>
    </div>
  ),
};

export const PatientStatuses: Story = {
  name: "Patient Status Badges",
  render: () => (
    <div className="flex gap-2">
      <Badge variant="success">Active</Badge>
      <Badge variant="danger">Inactive</Badge>
    </div>
  ),
};

export const MedicationStatuses: Story = {
  name: "Medication Status Badges",
  render: () => (
    <div className="flex gap-2">
      <Badge variant="success">Active</Badge>
      <Badge variant="default">Completed</Badge>
      <Badge variant="danger">Cancelled</Badge>
    </div>
  ),
};

export const InteractionSeverity: Story = {
  name: "Drug Interaction Severity",
  render: () => (
    <div className="flex gap-2">
      <Badge variant="danger">Contraindicated</Badge>
      <Badge variant="danger">Major</Badge>
      <Badge variant="warning">Moderate</Badge>
      <Badge variant="info">Minor</Badge>
    </div>
  ),
};
```

---

### 1.3 Input

The Input component supports labels, error states, and all standard HTML input attributes.

Create `src/components/ui/input.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Input } from "./input";

const meta: Meta<typeof Input> = {
  title: "UI/Input",
  component: Input,
  tags: ["autodocs"],
  argTypes: {
    label: { control: "text" },
    error: { control: "text" },
    placeholder: { control: "text" },
    type: {
      control: "select",
      options: ["text", "email", "password", "date", "number", "tel"],
    },
    disabled: { control: "boolean" },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    label: "First Name",
    placeholder: "Enter first name",
    id: "first-name",
  },
};

export const WithError: Story = {
  args: {
    label: "Email",
    placeholder: "patient@example.com",
    error: "Email already exists in the system",
    id: "email",
    type: "email",
  },
};

export const Password: Story = {
  args: {
    label: "Password",
    placeholder: "Enter password",
    type: "password",
    id: "password",
  },
};

export const Disabled: Story = {
  args: {
    label: "Patient ID",
    value: "550e8400-e29b-41d4-a716-446655440000",
    disabled: true,
    id: "patient-id",
  },
};

export const DateInput: Story = {
  args: {
    label: "Date of Birth",
    type: "date",
    id: "dob",
  },
};

// --- Composed: Patient Form ---

export const PatientFormFields: Story = {
  name: "Patient Registration Form",
  render: () => (
    <div className="max-w-md space-y-4">
      <Input id="first" label="First Name" placeholder="John" />
      <Input id="last" label="Last Name" placeholder="Doe" />
      <Input id="email" label="Email" type="email" placeholder="john.doe@example.com" />
      <Input id="dob" label="Date of Birth" type="date" />
      <Input id="phone" label="Phone" type="tel" placeholder="(555) 123-4567" />
      <Input
        id="ssn"
        label="SSN (Encrypted at rest)"
        type="password"
        placeholder="XXX-XX-XXXX"
      />
    </div>
  ),
};
```

---

### 1.4 Card

The Card component is used for content containers throughout the PMS dashboard.

Create `src/components/ui/card.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Card, CardHeader, CardTitle, CardContent } from "./card";
import { Badge } from "./badge";
import { Button } from "./button";

const meta: Meta<typeof Card> = {
  title: "UI/Card",
  component: Card,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Card className="max-w-sm">
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
      </CardHeader>
      <CardContent>
        This is a basic card component used throughout the PMS application.
      </CardContent>
    </Card>
  ),
};

export const PatientCard: Story = {
  name: "Patient Summary Card",
  render: () => (
    <Card className="max-w-sm">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>John Doe</CardTitle>
          <Badge variant="success">Active</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-1 text-sm text-gray-600">
          <p><span className="font-medium">DOB:</span> 1985-03-15</p>
          <p><span className="font-medium">Email:</span> john.doe@example.com</p>
          <p><span className="font-medium">Phone:</span> (555) 123-4567</p>
        </div>
        <div className="mt-4 flex gap-2">
          <Button size="sm">View Details</Button>
          <Button size="sm" variant="secondary">Edit</Button>
        </div>
      </CardContent>
    </Card>
  ),
};

export const EncounterCard: Story = {
  name: "Encounter Card",
  render: () => (
    <Card className="max-w-sm">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Office Visit</CardTitle>
          <Badge variant="warning">In Progress</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-1 text-sm text-gray-600">
          <p><span className="font-medium">Patient:</span> John Doe</p>
          <p><span className="font-medium">Provider:</span> Dr. Smith</p>
          <p><span className="font-medium">Date:</span> 2026-02-16 10:30 AM</p>
        </div>
        <div className="mt-4 flex gap-2">
          <Button size="sm">Complete</Button>
          <Button size="sm" variant="danger">Cancel</Button>
        </div>
      </CardContent>
    </Card>
  ),
};

export const StatsCard: Story = {
  name: "Dashboard Stats Card",
  render: () => (
    <div className="grid max-w-2xl grid-cols-3 gap-4">
      <Card>
        <CardContent>
          <p className="text-sm text-gray-500">Total Patients</p>
          <p className="mt-1 text-3xl font-bold text-gray-900">1,247</p>
          <p className="mt-1 text-xs text-green-600">+12% this month</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent>
          <p className="text-sm text-gray-500">Today&apos;s Encounters</p>
          <p className="mt-1 text-3xl font-bold text-gray-900">38</p>
          <p className="mt-1 text-xs text-blue-600">5 in progress</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent>
          <p className="text-sm text-gray-500">Active Prescriptions</p>
          <p className="mt-1 text-3xl font-bold text-gray-900">892</p>
          <p className="mt-1 text-xs text-yellow-600">3 interaction alerts</p>
        </CardContent>
      </Card>
    </div>
  ),
};

export const MedicationCard: Story = {
  name: "Medication Card",
  render: () => (
    <Card className="max-w-sm">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Amoxicillin 500mg</CardTitle>
          <Badge variant="success">Active</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-1 text-sm text-gray-600">
          <p><span className="font-medium">Patient:</span> John Doe</p>
          <p><span className="font-medium">Prescriber:</span> Dr. Smith</p>
          <p><span className="font-medium">Dosage:</span> 500mg 3x daily</p>
          <p><span className="font-medium">Refills:</span> 2 remaining</p>
        </div>
      </CardContent>
    </Card>
  ),
};
```

---

## Part 2: Layout Component Stories

Layout components use Next.js features (`usePathname`, `useRouter`, `Link`). The `@storybook/nextjs` framework mocks these automatically.

### 2.1 Sidebar

Create `src/components/layout/sidebar.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Sidebar } from "./sidebar";

const meta: Meta<typeof Sidebar> = {
  title: "Layout/Sidebar",
  component: Sidebar,
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
    nextjs: {
      appDirectory: true,
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const DashboardActive: Story = {
  name: "Dashboard Active",
  parameters: {
    nextjs: {
      navigation: { pathname: "/" },
    },
  },
};

export const PatientsActive: Story = {
  name: "Patients Active",
  parameters: {
    nextjs: {
      navigation: { pathname: "/patients" },
    },
  },
};

export const EncountersActive: Story = {
  name: "Encounters Active",
  parameters: {
    nextjs: {
      navigation: { pathname: "/encounters" },
    },
  },
};

export const MedicationsActive: Story = {
  name: "Medications Active",
  parameters: {
    nextjs: {
      navigation: { pathname: "/medications" },
    },
  },
};

export const ReportsActive: Story = {
  name: "Reports Active",
  parameters: {
    nextjs: {
      navigation: { pathname: "/reports" },
    },
  },
};
```

**Key concept:** The `parameters.nextjs.navigation.pathname` option tells Storybook which route to simulate, so the correct nav item is highlighted.

---

### 2.2 Header

Create `src/components/layout/header.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Header } from "./header";

const meta: Meta<typeof Header> = {
  title: "Layout/Header",
  component: Header,
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
    nextjs: {
      appDirectory: true,
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
```

---

## Part 3: Composed Page Stories

Page-level stories combine multiple components to show complete PMS workflows. These are ideal for stakeholder demos.

### 3.1 Patient List Page

Create `src/stories/pages/patient-list.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const meta: Meta = {
  title: "Pages/Patient List",
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
    nextjs: { appDirectory: true },
  },
};

export default meta;
type Story = StoryObj;

const mockPatients = [
  { id: "1", firstName: "John", lastName: "Doe", email: "john.doe@example.com", dob: "1985-03-15", gender: "Male", isActive: true },
  { id: "2", firstName: "Jane", lastName: "Smith", email: "jane.smith@example.com", dob: "1990-07-22", gender: "Female", isActive: true },
  { id: "3", firstName: "Robert", lastName: "Johnson", email: "r.johnson@example.com", dob: "1978-11-03", gender: "Male", isActive: true },
  { id: "4", firstName: "Emily", lastName: "Williams", email: "e.williams@example.com", dob: "1995-01-28", gender: "Female", isActive: false },
  { id: "5", firstName: "Michael", lastName: "Brown", email: "m.brown@example.com", dob: "1982-09-14", gender: "Male", isActive: true },
];

export const Default: Story = {
  render: () => (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
          <Button>Add Patient</Button>
        </div>
        <Card>
          <div className="mb-4">
            <Input
              id="search"
              placeholder="Search by name, email, or patient ID..."
            />
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="pb-3 font-medium">Name</th>
                <th className="pb-3 font-medium">Email</th>
                <th className="pb-3 font-medium">DOB</th>
                <th className="pb-3 font-medium">Gender</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {mockPatients.map((p) => (
                <tr key={p.id} className="border-b last:border-0">
                  <td className="py-3 font-medium text-gray-900">
                    {p.firstName} {p.lastName}
                  </td>
                  <td className="py-3 text-gray-600">{p.email}</td>
                  <td className="py-3 text-gray-600">{p.dob}</td>
                  <td className="py-3 text-gray-600">{p.gender}</td>
                  <td className="py-3">
                    <Badge variant={p.isActive ? "success" : "danger"}>
                      {p.isActive ? "Active" : "Inactive"}
                    </Badge>
                  </td>
                  <td className="py-3">
                    <div className="flex gap-2">
                      <Button size="sm" variant="secondary">View</Button>
                      <Button size="sm" variant="ghost">Edit</Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  ),
};

export const EmptyState: Story = {
  name: "Empty State",
  render: () => (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Patients</h1>
          <Button>Add Patient</Button>
        </div>
        <Card>
          <div className="py-12 text-center">
            <p className="text-lg font-medium text-gray-900">No patients found</p>
            <p className="mt-1 text-sm text-gray-500">Get started by adding your first patient.</p>
            <div className="mt-4">
              <Button>Add Patient</Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  ),
};
```

### 3.2 Encounter List Page

Create `src/stories/pages/encounter-list.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const meta: Meta = {
  title: "Pages/Encounter List",
  parameters: {
    layout: "fullscreen",
    nextjs: { appDirectory: true },
  },
};

export default meta;
type Story = StoryObj;

const statusVariant = {
  scheduled: "info",
  in_progress: "warning",
  completed: "success",
  cancelled: "danger",
} as const;

const mockEncounters = [
  { id: "1", patient: "John Doe", type: "Office Visit", provider: "Dr. Smith", date: "2026-02-16 09:00", status: "completed" },
  { id: "2", patient: "Jane Smith", type: "Telehealth", provider: "Dr. Adams", date: "2026-02-16 10:30", status: "in_progress" },
  { id: "3", patient: "Robert Johnson", type: "Follow Up", provider: "Dr. Smith", date: "2026-02-16 11:00", status: "scheduled" },
  { id: "4", patient: "Emily Williams", type: "Emergency", provider: "Dr. Lee", date: "2026-02-16 08:15", status: "completed" },
  { id: "5", patient: "Michael Brown", type: "Office Visit", provider: "Dr. Adams", date: "2026-02-15 14:00", status: "cancelled" },
];

export const Default: Story = {
  render: () => (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Encounters</h1>
          <Button>New Encounter</Button>
        </div>
        <Card>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="pb-3 font-medium">Patient</th>
                <th className="pb-3 font-medium">Type</th>
                <th className="pb-3 font-medium">Provider</th>
                <th className="pb-3 font-medium">Date</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {mockEncounters.map((e) => (
                <tr key={e.id} className="border-b last:border-0">
                  <td className="py-3 font-medium text-gray-900">{e.patient}</td>
                  <td className="py-3 text-gray-600">{e.type}</td>
                  <td className="py-3 text-gray-600">{e.provider}</td>
                  <td className="py-3 text-gray-600">{e.date}</td>
                  <td className="py-3">
                    <Badge variant={statusVariant[e.status as keyof typeof statusVariant]}>
                      {e.status.replace("_", " ")}
                    </Badge>
                  </td>
                  <td className="py-3">
                    <Button size="sm" variant="secondary">View</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  ),
};
```

### 3.3 Dashboard Page

Create `src/stories/pages/dashboard.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

const meta: Meta = {
  title: "Pages/Dashboard",
  parameters: {
    layout: "fullscreen",
    nextjs: { appDirectory: true },
  },
};

export default meta;
type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 text-2xl font-bold text-gray-900">Dashboard</h1>

        {/* Stats Row */}
        <div className="mb-6 grid grid-cols-4 gap-4">
          <Card>
            <CardContent>
              <p className="text-sm text-gray-500">Total Patients</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">1,247</p>
              <p className="mt-1 text-xs text-green-600">+12 this week</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent>
              <p className="text-sm text-gray-500">Today&apos;s Encounters</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">38</p>
              <p className="mt-1 text-xs text-blue-600">5 in progress</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent>
              <p className="text-sm text-gray-500">Active Prescriptions</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">892</p>
              <p className="mt-1 text-xs text-yellow-600">3 alerts</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent>
              <p className="text-sm text-gray-500">Pending Reports</p>
              <p className="mt-1 text-3xl font-bold text-gray-900">7</p>
              <p className="mt-1 text-xs text-gray-500">2 overdue</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Recent Patients */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Recent Patients</CardTitle>
                <Button size="sm" variant="ghost">View All</Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: "John Doe", date: "Feb 16, 2026", status: "Active" },
                  { name: "Jane Smith", date: "Feb 15, 2026", status: "Active" },
                  { name: "Robert Johnson", date: "Feb 14, 2026", status: "Active" },
                ].map((p) => (
                  <div key={p.name} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{p.name}</p>
                      <p className="text-xs text-gray-500">Registered {p.date}</p>
                    </div>
                    <Badge variant="success">{p.status}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Today's Encounters */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Today&apos;s Encounters</CardTitle>
                <Button size="sm" variant="ghost">View All</Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { patient: "John Doe", type: "Office Visit", status: "completed", variant: "success" as const },
                  { patient: "Jane Smith", type: "Telehealth", status: "in progress", variant: "warning" as const },
                  { patient: "Robert Johnson", type: "Follow Up", status: "scheduled", variant: "info" as const },
                ].map((e) => (
                  <div key={e.patient} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{e.patient}</p>
                      <p className="text-xs text-gray-500">{e.type}</p>
                    </div>
                    <Badge variant={e.variant}>{e.status}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  ),
};
```

---

## Part 4: Interactive Stories with Play Functions

Play functions let you simulate user interactions — useful for testing form flows.

### 4.1 Login Form

Create `src/stories/pages/login.stories.tsx`:

```tsx
import type { Meta, StoryObj } from "@storybook/react";
import { within, userEvent } from "@storybook/testing-library";
import { expect } from "@storybook/jest";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const meta: Meta = {
  title: "Pages/Login",
  parameters: {
    layout: "fullscreen",
    nextjs: { appDirectory: true },
  },
};

export default meta;
type Story = StoryObj;

const LoginForm = () => (
  <div className="flex min-h-screen items-center justify-center bg-gray-50">
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="text-center text-2xl">
          Patient Management System
        </CardTitle>
        <p className="text-center text-sm text-gray-500">
          Sign in to access patient records
        </p>
      </CardHeader>
      <CardContent>
        <form className="space-y-4">
          <Input
            id="username"
            label="Username"
            placeholder="Enter your username"
          />
          <Input
            id="password"
            label="Password"
            type="password"
            placeholder="Enter your password"
          />
          <Button className="w-full">Sign In</Button>
        </form>
      </CardContent>
    </Card>
  </div>
);

export const Default: Story = {
  render: () => <LoginForm />,
};

export const FilledForm: Story = {
  render: () => <LoginForm />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    const usernameInput = canvas.getByLabelText("Username");
    const passwordInput = canvas.getByLabelText("Password");

    await userEvent.type(usernameInput, "dr.smith", { delay: 50 });
    await userEvent.type(passwordInput, "securepassword", { delay: 50 });
  },
};
```

---

## Part 5: Story Organization

### Recommended Sidebar Structure

```
Storybook Sidebar
├── UI/
│   ├── Button        ← all button variants and states
│   ├── Badge         ← all badge variants + PMS-specific combos
│   ├── Card          ← card variations + patient/encounter/medication cards
│   └── Input         ← input states + patient form fields
├── Layout/
│   ├── Sidebar       ← nav with each route active
│   └── Header        ← header with sign-out
└── Pages/
    ├── Dashboard     ← stats + recent activity
    ├── Login         ← login form + auto-fill demo
    ├── Patient List  ← table + empty state
    └── Encounter List← table with status badges
```

### Naming Conventions

| Convention | Example |
|---|---|
| Story file | `button.stories.tsx` (co-located with component) |
| Page story | `src/stories/pages/dashboard.stories.tsx` |
| Title path | `"UI/Button"`, `"Layout/Sidebar"`, `"Pages/Dashboard"` |
| Story name | PascalCase export: `AllVariants`, `EmptyState`, `FilledForm` |

---

## Part 6: Best Practices for PMS

### Do
- **Write stories for every new component** — treat it like writing tests
- **Show real PMS data** — use realistic patient names, encounter types, medication names
- **Cover all states** — empty, loading, error, single item, many items
- **Use `autodocs` tag** — auto-generates documentation pages
- **Keep stories simple** — one concept per story

### Don't
- **Don't import real API calls** — use mock data in stories
- **Don't use real PHI** — always use fake patient data
- **Don't test business logic in stories** — that's what Vitest is for
- **Don't skip edge cases** — empty states and error states are valuable

### HIPAA Reminder

Never use real patient data in Storybook stories. All mock data should use clearly fictional names, emails, and dates. Storybook builds are static HTML and may be deployed publicly.

---

## Quick Reference

```bash
# Start Storybook dev server
npm run storybook

# Build static Storybook site
npm run build-storybook

# Add to .gitignore
echo "storybook-static/" >> .gitignore
```

---

## Next Steps

1. Follow the [Getting Started Guide](01-Storybook-Getting-Started.md) to install Storybook
2. Create stories for the 4 UI primitives (Part 1)
3. Add layout stories (Part 2)
4. Build page-level stories for stakeholder demos (Part 3)
5. Optionally set up [Chromatic](https://www.chromatic.com/) for visual regression testing in CI
