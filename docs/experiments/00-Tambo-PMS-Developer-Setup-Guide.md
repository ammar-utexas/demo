# Tambo AI Self-Hosted Setup Guide for PMS Integration

**For:** MPS Inc. Engineering Team
**Version:** 1.0
**Date:** February 16, 2026
**Prerequisites Level:** Intermediate (React, Docker, Spring Boot familiarity assumed)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Part A: Self-Host the Tambo Backend](#3-part-a-self-host-the-tambo-backend)
4. [Part B: Create the PMS Tambo Frontend App](#4-part-b-create-the-pms-tambo-frontend-app)
5. [Part C: Register PMS Components](#5-part-c-register-pms-components)
6. [Part D: Define PMS API Tools](#6-part-d-define-pms-api-tools)
7. [Part E: Wire It All Together](#7-part-e-wire-it-all-together)
8. [Part F: Testing and Verification](#8-part-f-testing-and-verification)
9. [Troubleshooting](#9-troubleshooting)
10. [Reference Commands](#10-reference-commands)

---

## 1. Overview

This guide walks you through setting up a **self-hosted Tambo AI backend** on your local development machine and integrating it with the MPS PMS dashboard. By the end, you will have:

- A locally running Tambo backend (NestJS API + PostgreSQL) inside Docker
- A React frontend with Tambo's generative UI rendering PMS components
- Tools that call our existing Spring Boot APIs to fetch real data
- A working conversational analytics sidebar

### Architecture at a Glance

```
Your Development Machine
├── Docker
│   ├── Tambo API        (NestJS)        → localhost:3001
│   ├── Tambo Dashboard  (Next.js)       → localhost:3000
│   └── PostgreSQL       (Tambo state)   → localhost:5432
│
├── MPS API           (Spring Boot)   → localhost:8080 (your existing backend)
│
└── PMS Frontend         (React + Tambo SDK)  → localhost:3030
```

---

## 2. Prerequisites

Verify each of these before proceeding.

### 2.1 Required Software

| Software | Minimum Version | Check Command |
|----------|----------------|---------------|
| Node.js | 22.x | `node --version` |
| npm | 11.x | `npm --version` |
| Docker | 24.x | `docker --version` |
| Docker Compose | 2.x | `docker compose version` |
| Git | 2.x | `git --version` |
| jq | 1.6+ | `jq --version` |

### 2.2 Install Node.js 22 (if needed)

```bash
# Using nvm (recommended)
nvm install 22
nvm use 22
node --version  # Should show v22.x.x
```

### 2.3 API Keys Required

You will need an **Anthropic API key** for the LLM provider. Tambo supports other providers (OpenAI, Gemini, Mistral), but we standardize on Anthropic Claude for consistency with our other AI tooling.

1. Go to https://console.anthropic.com
2. Create an API key
3. Save it securely — you will add it to the Tambo environment file in Step 3

### 2.4 Verify MPS Backend is Running

Make sure your local MPS Spring Boot API is running and accessible:

```bash
curl http://localhost:8080/actuator/health
# Expected: {"status":"UP"}
```

If not running, start it per the standard MPS developer setup.

---

## 3. Part A: Self-Host the Tambo Backend

The Tambo backend manages conversation state, agent orchestration, and thread history. We run it locally in Docker.

### Step 1: Clone the Tambo Repository

```bash
cd ~/projects
git clone https://github.com/tambo-ai/tambo.git
cd tambo
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Configure Environment Files

The Tambo monorepo needs environment files in several locations. Start by copying the example templates:

```bash
# API environment
cp apps/api/.env.example apps/api/.env

# Web dashboard environment
cp apps/web/.env.local.example apps/web/.env.local
# If .env.local.example doesn't exist, create it:
# touch apps/web/.env.local

# Database environment
cp packages/db/.env.example packages/db/.env
```

Edit `apps/api/.env` and set the following values:

```env
# Database — matches the Docker Compose PostgreSQL config
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tambo

# LLM Provider — use your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Server
PORT=3001
NODE_ENV=development
```

Edit `apps/web/.env.local`:

```env
# Points to the local Tambo API
NEXT_PUBLIC_TAMBO_API_URL=http://localhost:3001

# You will generate this key in Step 6
NEXT_PUBLIC_TAMBO_API_KEY=
```

Edit `packages/db/.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tambo
```

### Step 4: Start PostgreSQL via Docker

```bash
# Start only PostgreSQL from the Docker Compose stack
docker compose --env-file docker.env up postgres -d
```

If `docker.env` doesn't exist yet, create it:

```bash
cat > docker.env << 'EOF'
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tambo
POSTGRES_PORT=5432
EOF
```

Then run the Docker command again.

Verify PostgreSQL is running:

```bash
docker ps | grep postgres
# Should show a running container

# Test connection
docker exec -it $(docker ps -q --filter ancestor=postgres) psql -U postgres -c "SELECT 1;"
```

### Step 5: Initialize the Database

```bash
# Generate and apply migrations
npm run db:generate -w packages/db
npm run db:migrate -w packages/db
```

If the `init-database.sh` script is available:

```bash
./scripts/init-database.sh
```

Verify the schema was created:

```bash
# Open Drizzle Studio to visually inspect the database
npm run db:studio -w packages/db
# Opens at https://local.drizzle.studio
```

### Step 6: Start the Tambo Backend

```bash
# This starts both the NestJS API (port 3001) and Next.js dashboard (port 3000)
npm run dev:cloud
```

Wait for both services to report ready, then verify:

```bash
# Check the API
curl http://localhost:3001/health
# Expected: OK or {"status":"ok"}

# Check the dashboard
open http://localhost:3000
```

### Step 7: Generate Your API Key

1. Open `http://localhost:3000/dashboard` in your browser
2. Sign up or log in with local credentials
3. Create a new project (name it "MPS PMS")
4. Navigate to the project settings and generate an API key
5. Copy the key and add it to `apps/web/.env.local`:

```env
NEXT_PUBLIC_TAMBO_API_KEY=your_generated_key_here
```

### Step 8: Verify the Setup

```bash
# Run the smoke test
open http://localhost:3000/internal/smoketest
```

If the smoke test passes, your self-hosted Tambo backend is ready.

**Checkpoint:** At this point you should have:
- PostgreSQL running in Docker on port 5432
- Tambo API running on port 3001
- Tambo Dashboard running on port 3000
- A valid Tambo API key

---

## 4. Part B: Create the PMS Tambo Frontend App

Now we create the React frontend that integrates Tambo into PMS. You have two options:

### Option A: Add Tambo to the Existing PMS Frontend (Recommended)

If the PMS frontend already exists as a React app:

```bash
cd ~/projects/pms-frontend

# Install the Tambo React SDK
npm install @tambo-ai/react zod

# Initialize Tambo (select "self-hosted" when prompted)
npx tambo init
```

During `tambo init`, when asked:
- **Backend type:** Select "Self-hosted"
- **API URL:** Enter `http://localhost:3001`
- **API Key:** Paste the key from Step 7

This writes the configuration to your `.env.local`.

### Option B: Create a Standalone Prototype

For initial prototyping before integrating into the main PMS app:

```bash
npm create tambo-app@latest pms-tambo-prototype -- --skip-tambo-init
cd pms-tambo-prototype

# Manually configure for self-hosted
cat > .env.local << 'EOF'
NEXT_PUBLIC_TAMBO_API_KEY=your_key_here
NEXT_PUBLIC_TAMBO_API_URL=http://localhost:3001
EOF

npm install
npm run dev
# Opens on localhost:3000 (change port if conflicting with Tambo dashboard)
```

---

## 5. Part C: Register PMS Components

Create the PMS-specific components that Tambo will render. Each component gets a Zod schema that tells the agent what props it accepts.

### Step 1: Create the Component Directory

```bash
mkdir -p src/components/tambo-pms
```

### Step 2: Enrollment Dashboard Component

Create `src/components/tambo-pms/enrollment-dashboard.tsx`:

```tsx
"use client";

import { useMemo } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from "recharts";

interface EnrollmentDashboardProps {
  organizationName?: string;
  dateRange?: { start: string; end: string };
  totalPatients?: number;
  enrolled?: number;
  declined?: number;
  optOut?: number;
  inactive?: number;
  ineligible?: number;
  pendingEnrollment?: number;
  enrollmentPercentage?: number;
  trend?: Array<{ week: string; enrollmentPct: number }>;
}

export default function EnrollmentDashboard({
  organizationName = "Loading...",
  totalPatients = 0,
  enrolled = 0,
  declined = 0,
  optOut = 0,
  inactive = 0,
  ineligible = 0,
  pendingEnrollment = 0,
  enrollmentPercentage = 0,
  trend = [],
}: EnrollmentDashboardProps) {
  const statusData = useMemo(() => [
    { name: "Enrolled", value: enrolled, color: "#10B981" },
    { name: "Pending", value: pendingEnrollment, color: "#F59E0B" },
    { name: "Declined", value: declined, color: "#EF4444" },
    { name: "Opt-Out", value: optOut, color: "#8B5CF6" },
    { name: "Inactive", value: inactive, color: "#6B7280" },
    { name: "Ineligible", value: ineligible, color: "#9CA3AF" },
  ], [enrolled, pendingEnrollment, declined, optOut, inactive, ineligible]);

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 max-w-2xl">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900">{organizationName}</h2>
        <p className="text-sm text-gray-500">Enrollment Overview</p>
      </div>

      {/* Key Metric */}
      <div className="flex items-center gap-4 mb-6 p-4 bg-emerald-50 rounded-lg">
        <div className="text-4xl font-bold text-emerald-600">
          {enrollmentPercentage.toFixed(1)}%
        </div>
        <div className="text-sm text-gray-600">
          <div>{enrolled} enrolled out of {totalPatients} total patients</div>
          <div>{pendingEnrollment} pending enrollment</div>
        </div>
      </div>

      {/* Status Breakdown */}
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={statusData} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="name" width={80} />
          <Tooltip />
          <Bar dataKey="value">
            {statusData.map((entry, index) => (
              <Cell key={index} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Trend (if provided) */}
      {trend.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Weekly Trend</h3>
          <ResponsiveContainer width="100%" height={150}>
            <BarChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" fontSize={12} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="enrollmentPct" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
```

### Step 3: Encounter Table Component

Create `src/components/tambo-pms/encounter-table.tsx`:

```tsx
"use client";

interface Encounter {
  patientName: string;
  encounterType: "RPM" | "CCM" | "HRA" | "APPOINTMENT";
  scheduledDate: string;
  outcome: "COMPLETED" | "NO_SHOW" | "CANCELLED" | "SCHEDULED";
  healthCoach: string;
  duration?: number;
}

interface EncounterTableProps {
  encounters?: Encounter[];
  summary?: {
    total: number;
    completed: number;
    noShow: number;
    cancelled: number;
    completionRate: number;
    noShowRate: number;
  };
}

const outcomeColors: Record<string, string> = {
  COMPLETED: "bg-green-100 text-green-800",
  NO_SHOW: "bg-red-100 text-red-800",
  CANCELLED: "bg-gray-100 text-gray-800",
  SCHEDULED: "bg-blue-100 text-blue-800",
};

const typeColors: Record<string, string> = {
  RPM: "bg-cyan-100 text-cyan-800",
  CCM: "bg-purple-100 text-purple-800",
  HRA: "bg-amber-100 text-amber-800",
  APPOINTMENT: "bg-indigo-100 text-indigo-800",
};

export default function EncounterTable({
  encounters = [],
  summary = { total: 0, completed: 0, noShow: 0, cancelled: 0, completionRate: 0, noShowRate: 0 },
}: EncounterTableProps) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 max-w-3xl">
      {/* Summary Row */}
      <div className="flex gap-4 mb-4 text-sm">
        <div className="px-3 py-1 bg-gray-50 rounded">
          Total: <span className="font-semibold">{summary.total}</span>
        </div>
        <div className="px-3 py-1 bg-green-50 rounded">
          Completion: <span className="font-semibold">{summary.completionRate.toFixed(1)}%</span>
        </div>
        <div className="px-3 py-1 bg-red-50 rounded">
          No-show: <span className="font-semibold">{summary.noShowRate.toFixed(1)}%</span>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-gray-500">
              <th className="pb-2 pr-4">Patient</th>
              <th className="pb-2 pr-4">Type</th>
              <th className="pb-2 pr-4">Date</th>
              <th className="pb-2 pr-4">Outcome</th>
              <th className="pb-2 pr-4">Health Coach</th>
            </tr>
          </thead>
          <tbody>
            {encounters.map((enc, i) => (
              <tr key={i} className="border-b border-gray-100">
                <td className="py-2 pr-4 font-medium">{enc.patientName}</td>
                <td className="py-2 pr-4">
                  <span className={`px-2 py-0.5 rounded text-xs ${typeColors[enc.encounterType]}`}>
                    {enc.encounterType}
                  </span>
                </td>
                <td className="py-2 pr-4 text-gray-600">{enc.scheduledDate}</td>
                <td className="py-2 pr-4">
                  <span className={`px-2 py-0.5 rounded text-xs ${outcomeColors[enc.outcome]}`}>
                    {enc.outcome}
                  </span>
                </td>
                <td className="py-2 pr-4 text-gray-600">{enc.healthCoach}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {encounters.length === 0 && (
        <p className="text-center text-gray-400 py-8">No encounters found for the given criteria.</p>
      )}
    </div>
  );
}
```

### Step 4: Register Components with Tambo

Create `src/lib/pms-tambo.ts`:

```typescript
import { TamboComponent } from "@tambo-ai/react";
import { z } from "zod";
import EnrollmentDashboard from "@/components/tambo-pms/enrollment-dashboard";
import EncounterTable from "@/components/tambo-pms/encounter-table";

export const pmsComponents: TamboComponent[] = [
  {
    name: "EnrollmentDashboard",
    description:
      "Displays patient enrollment metrics for a healthcare practice including " +
      "enrollment percentage, status breakdown (enrolled, declined, opt-out, " +
      "inactive, ineligible, pending), and weekly enrollment trends. Use this " +
      "when the user asks about enrollment rates, patient status distribution, " +
      "or practice performance.",
    component: EnrollmentDashboard,
    propsSchema: z.object({
      organizationName: z.string().describe("Name of the healthcare practice"),
      dateRange: z.object({
        start: z.string().describe("Start date in ISO format"),
        end: z.string().describe("End date in ISO format"),
      }),
      totalPatients: z.number(),
      enrolled: z.number(),
      declined: z.number(),
      optOut: z.number(),
      inactive: z.number(),
      ineligible: z.number(),
      pendingEnrollment: z.number(),
      enrollmentPercentage: z.number().describe("Enrollment percentage 0-100"),
      trend: z.array(z.object({
        week: z.string().describe("Week label e.g. 'Week 1'"),
        enrollmentPct: z.number(),
      })).optional().describe("Weekly enrollment trend data"),
    }),
  },
  {
    name: "EncounterTable",
    description:
      "Renders a table of patient encounters (RPM, CCM, HRA, Appointments) " +
      "with status badges and summary metrics. Use when the user asks about " +
      "encounters, appointments, no-shows, completion rates, or health coach performance.",
    component: EncounterTable,
    propsSchema: z.object({
      encounters: z.array(z.object({
        patientName: z.string(),
        encounterType: z.enum(["RPM", "CCM", "HRA", "APPOINTMENT"]),
        scheduledDate: z.string(),
        outcome: z.enum(["COMPLETED", "NO_SHOW", "CANCELLED", "SCHEDULED"]),
        healthCoach: z.string(),
        duration: z.number().optional(),
      })),
      summary: z.object({
        total: z.number(),
        completed: z.number(),
        noShow: z.number(),
        cancelled: z.number(),
        completionRate: z.number(),
        noShowRate: z.number(),
      }),
    }),
  },
];
```

---

## 6. Part D: Define PMS API Tools

Tools let the Tambo agent fetch real data from your Spring Boot backend. Create `src/lib/pms-tools.ts`:

```typescript
import { TamboTool } from "@tambo-ai/react";
import { z } from "zod";

// Base URL for your local MPS Spring Boot API
const PMS_API = process.env.NEXT_PUBLIC_PMS_API_URL || "http://localhost:8080";

// Helper: authenticated fetch using the user's JWT
async function pmsFetch(path: string, token?: string) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch(`${PMS_API}${path}`, { headers });
  if (!response.ok) {
    throw new Error(`MPS API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export const pmsTools: TamboTool[] = [
  {
    name: "queryPatientStatus",
    description:
      "Fetches patient enrollment status metrics for a specific organization " +
      "and date range. Returns counts of enrolled, declined, opt-out, inactive, " +
      "ineligible, and pending patients along with enrollment percentage.",
    tool: async (params: { organizationId: string; startDate: string; endDate: string }) => {
      const { organizationId, startDate, endDate } = params;
      return pmsFetch(
        `/api/dw/patient-status?orgId=${organizationId}&start=${startDate}&end=${endDate}`
      );
    },
    inputSchema: z.object({
      organizationId: z.string().describe("The organization/practice ID"),
      startDate: z.string().describe("Start date in ISO format (YYYY-MM-DD)"),
      endDate: z.string().describe("End date in ISO format (YYYY-MM-DD)"),
    }),
    outputSchema: z.object({
      organizationName: z.string(),
      totalPatients: z.number(),
      enrolled: z.number(),
      declined: z.number(),
      optOut: z.number(),
      inactive: z.number(),
      ineligible: z.number(),
      pendingEnrollment: z.number(),
      enrollmentPercentage: z.number(),
    }),
  },
  {
    name: "queryEvents",
    description:
      "Fetches encounter and appointment data with optional filters for " +
      "encounter type, outcome, health coach, and date range. Returns both " +
      "individual encounters and summary statistics.",
    tool: async (params: {
      organizationId: string;
      startDate: string;
      endDate: string;
      encounterType?: string;
      outcome?: string;
      healthCoachId?: string;
    }) => {
      const query = new URLSearchParams({
        orgId: params.organizationId,
        start: params.startDate,
        end: params.endDate,
      });
      if (params.encounterType) query.set("type", params.encounterType);
      if (params.outcome) query.set("outcome", params.outcome);
      if (params.healthCoachId) query.set("coachId", params.healthCoachId);

      return pmsFetch(`/api/dw/events?${query.toString()}`);
    },
    inputSchema: z.object({
      organizationId: z.string().describe("The organization/practice ID"),
      startDate: z.string().describe("Start date (YYYY-MM-DD)"),
      endDate: z.string().describe("End date (YYYY-MM-DD)"),
      encounterType: z.enum(["RPM", "CCM", "HRA", "APPOINTMENT"]).optional()
        .describe("Filter by encounter type"),
      outcome: z.enum(["COMPLETED", "NO_SHOW", "CANCELLED", "SCHEDULED"]).optional()
        .describe("Filter by outcome"),
      healthCoachId: z.string().optional()
        .describe("Filter by specific health coach"),
    }),
    outputSchema: z.object({
      encounters: z.array(z.object({
        patientName: z.string(),
        encounterType: z.string(),
        scheduledDate: z.string(),
        outcome: z.string(),
        healthCoach: z.string(),
        duration: z.number().optional(),
      })),
      summary: z.object({
        total: z.number(),
        completed: z.number(),
        noShow: z.number(),
        cancelled: z.number(),
        completionRate: z.number(),
        noShowRate: z.number(),
      }),
    }),
  },
  {
    name: "listOrganizations",
    description:
      "Returns the list of organizations/practices available to the current user. " +
      "Use this to resolve practice names to IDs before calling other tools.",
    tool: async () => {
      return pmsFetch("/api/organizations");
    },
    inputSchema: z.object({}),
    outputSchema: z.array(z.object({
      id: z.string(),
      name: z.string(),
      patientCount: z.number().optional(),
    })),
  },
];
```

---

## 7. Part E: Wire It All Together

### Step 1: Create the TamboProvider Wrapper

Create `src/components/tambo-pms/pms-tambo-provider.tsx`:

```tsx
"use client";

import { TamboProvider } from "@tambo-ai/react";
import { pmsComponents } from "@/lib/pms-tambo";
import { pmsTools } from "@/lib/pms-tools";
import { ReactNode } from "react";

interface PMSTamboProviderProps {
  children: ReactNode;
  userToken?: string;       // JWT from MPS auth
  userKey?: string;          // Fallback user identifier
  organizationId?: string;   // Current org context
}

export default function PMSTamboProvider({
  children,
  userToken,
  userKey,
  organizationId,
}: PMSTamboProviderProps) {
  return (
    <TamboProvider
      apiKey={process.env.NEXT_PUBLIC_TAMBO_API_KEY!}
      components={pmsComponents}
      tools={pmsTools}
      userToken={userToken}
      userKey={userKey}
      contextHelpers={{
        currentOrganization: () => ({
          key: "currentOrganization",
          value: organizationId || "none",
        }),
        currentPage: () => ({
          key: "currentPage",
          value: typeof window !== "undefined" ? window.location.pathname : "/",
        }),
        userRole: () => ({
          key: "userRole",
          value: "practice_admin", // Replace with actual role from auth context
        }),
      }}
    >
      {children}
    </TamboProvider>
  );
}
```

### Step 2: Create the Conversational Sidebar

Create `src/components/tambo-pms/analytics-sidebar.tsx`:

```tsx
"use client";

import { useTamboThread, useTamboThreadInput, useTamboSuggestions } from "@tambo-ai/react";

export default function AnalyticsSidebar() {
  const { thread } = useTamboThread();
  const { value, setValue, submit, isPending } = useTamboThreadInput();
  const { suggestions, accept } = useTamboSuggestions({ maxSuggestions: 3 });

  return (
    <div className="w-96 h-full flex flex-col border-l border-gray-200 bg-gray-50">
      {/* Header */}
      <div className="p-4 border-b bg-white">
        <h2 className="text-sm font-semibold text-gray-700">PMS Analytics</h2>
        <p className="text-xs text-gray-400">Ask about enrollment, encounters, engagement</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {thread?.messages.map((message) => (
          <div key={message.id} className="space-y-2">
            {/* Text content */}
            {Array.isArray(message.content) ? (
              message.content.map((part, i) =>
                part.type === "text" ? (
                  <div
                    key={i}
                    className={`text-sm p-3 rounded-lg ${
                      message.role === "user"
                        ? "bg-blue-100 text-blue-900 ml-8"
                        : "bg-white text-gray-700 mr-8 shadow-sm"
                    }`}
                  >
                    {part.text}
                  </div>
                ) : null
              )
            ) : (
              <div className="text-sm p-3 rounded-lg bg-white text-gray-700 mr-8 shadow-sm">
                {String(message.content)}
              </div>
            )}

            {/* Rendered component */}
            {message.renderedComponent && (
              <div className="mt-2">{message.renderedComponent}</div>
            )}
          </div>
        ))}

        {isPending && (
          <div className="text-sm text-gray-400 animate-pulse">Analyzing...</div>
        )}
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && !isPending && (
        <div className="px-4 py-2 flex flex-wrap gap-2">
          {suggestions.map((s) => (
            <button
              key={s.id}
              onClick={() => accept(s)}
              className="text-xs px-3 py-1.5 rounded-full border border-gray-300
                         bg-white hover:bg-gray-100 text-gray-600 transition-colors"
            >
              {s.title}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t bg-white">
        <div className="flex gap-2">
          <input
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !isPending && submit()}
            placeholder="Ask about your practice metrics..."
            className="flex-1 text-sm px-3 py-2 border rounded-lg focus:outline-none
                       focus:ring-2 focus:ring-blue-200"
            disabled={isPending}
          />
          <button
            onClick={() => submit()}
            disabled={isPending || !value.trim()}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg
                       hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
                       transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

### Step 3: Integrate into PMS Dashboard Page

In your PMS dashboard page (e.g., `src/app/dashboard/page.tsx`):

```tsx
import PMSTamboProvider from "@/components/tambo-pms/pms-tambo-provider";
import AnalyticsSidebar from "@/components/tambo-pms/analytics-sidebar";

export default function DashboardPage() {
  // Get these from your auth context
  const userToken = "...";        // JWT from MPS auth
  const organizationId = "...";   // Current org from route/context

  return (
    <PMSTamboProvider
      userToken={userToken}
      organizationId={organizationId}
    >
      <div className="flex h-screen">
        {/* Existing PMS Dashboard Content */}
        <main className="flex-1 overflow-y-auto">
          {/* Your existing dashboard components here */}
        </main>

        {/* Tambo Analytics Sidebar */}
        <AnalyticsSidebar />
      </div>
    </PMSTamboProvider>
  );
}
```

---

## 8. Part F: Testing and Verification

### Step 1: Verify All Services Are Running

Run this checklist:

```bash
# 1. PostgreSQL (Tambo state)
docker ps | grep postgres
# ✓ Container running on port 5432

# 2. Tambo API
curl http://localhost:3001/health
# ✓ Returns OK

# 3. Tambo Dashboard
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# ✓ Returns 200

# 4. MPS Spring Boot API
curl http://localhost:8080/actuator/health
# ✓ Returns {"status":"UP"}

# 5. PMS Frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3030
# ✓ Returns 200
```

### Step 2: Test Queries

Open the PMS dashboard in your browser and try these queries in the sidebar:

| Query | Expected Component |
|-------|--------------------|
| "Show enrollment for practice ABC" | EnrollmentDashboard |
| "List all no-shows this week" | EncounterTable filtered by NO_SHOW |
| "What's the encounter completion rate?" | EncounterTable with summary stats |
| "Which organizations do I have access to?" | Text response listing organizations |

### Step 3: Check Tambo Logs

```bash
# View Tambo API logs for agent reasoning and tool calls
docker compose logs -f api

# Or if running locally
# Check the terminal where npm run dev:cloud is running
```

Look for tool invocation logs that confirm the agent is calling your `queryPatientStatus` and `queryEvents` tools.

---

## 9. Troubleshooting

### "Connection refused" on port 3001
- Verify Tambo API is running: `npm run dev:cloud`
- Check if another process is using port 3001: `lsof -i :3001`
- Verify PostgreSQL is running: `docker ps`

### "Invalid API key"
- Regenerate the key at `http://localhost:3000/dashboard`
- Ensure the key is in your frontend `.env.local` as `NEXT_PUBLIC_TAMBO_API_KEY`
- Restart your dev server after changing env vars

### Agent returns text instead of rendering a component
- Check that your component descriptions in `pms-tambo.ts` are specific enough
- Verify the component is included in the `pmsComponents` array
- Check browser console for Tambo SDK errors

### Database migration errors
```bash
# Reset and re-run migrations
npm run db:migrate -w packages/db

# If that fails, drop and recreate
docker exec -it $(docker ps -q --filter ancestor=postgres) \
  psql -U postgres -c "DROP DATABASE tambo; CREATE DATABASE tambo;"
npm run db:migrate -w packages/db
```

### Port conflicts
If ports 3000/3001 conflict with other services, the Docker stack uses alternative ports:

| Service | Local Dev | Docker |
|---------|-----------|--------|
| Tambo Web | 3000 | 3210 |
| Tambo API | 3001 | 3211 |
| PostgreSQL | 5432 | 5433 |

Update your `.env.local` accordingly if using Docker ports.

---

## 10. Reference Commands

### Daily Development Workflow

```bash
# Start everything
docker compose --env-file docker.env up postgres -d   # Database
npm run dev:cloud                                       # Tambo backend
cd ~/projects/pms-frontend && npm run dev            # PMS frontend

# Stop everything
# Ctrl+C on dev:cloud
docker compose down
```

### Database Management

```bash
npm run db:generate -w packages/db    # Generate migrations from schema changes
npm run db:migrate -w packages/db     # Apply migrations
npm run db:studio -w packages/db      # Open visual database browser
```

### Quality Checks

```bash
npm run lint          # Lint all packages
npm run check-types   # TypeScript type check
npm test              # Run tests
```

### Useful URLs

| URL | Description |
|-----|-------------|
| `http://localhost:3000` | Tambo Dashboard (project management, API keys) |
| `http://localhost:3001` | Tambo API (NestJS, Swagger docs at /api) |
| `http://localhost:3030` | PMS Frontend with Tambo sidebar |
| `http://localhost:8080` | MPS Spring Boot API |
| `https://local.drizzle.studio` | Database visual browser |

---

## Next Steps

Once the Phase 1 setup is verified and working:

1. **Add more components:** `EngagementChart`, `DeviceUtilization`, `PracticeComparisonTable` (see PRD for schemas)
2. **Add more tools:** `queryEngagement`, `queryDevices`, `comparePractices`
3. **Implement context helpers:** Auto-detect current organization from URL params
4. **Add suggestion prompts:** Role-based starter queries for each user type
5. **Production deployment:** Move Docker setup to MPS staging/production infrastructure

Refer to the full PRD (PRD-PMS-TAMBO-001) for Phase 2 and Phase 3 requirements.

---

## Resources

- Tambo Documentation: https://docs.tambo.co
- Tambo GitHub: https://github.com/tambo-ai/tambo
- Tambo React SDK Reference: https://docs.tambo.co/reference/react-sdk
- Tambo Self-Hosting Guide: https://docs.tambo.co/guides/self-hosting
- Tambo Discord: https://tambo.co/discord
