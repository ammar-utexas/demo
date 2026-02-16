# Tambo AI Developer Onboarding Tutorial

**Welcome to the MPS PMS Conversational Analytics Team**

This tutorial will take you from zero to building your first Tambo-powered component. By the end, you will understand how Tambo works, have a running local environment, and have built and tested a custom PMS component end-to-end.

**Estimated time:** 2-3 hours
**Difficulty:** Beginner-friendly (assumes basic React and TypeScript knowledge)

---

## What You Will Learn

1. What Tambo is and why we use it
2. How the pieces fit together (mental model)
3. Setting up your local environment
4. Building your first component
5. Building your first tool
6. Testing with real queries
7. Debugging common issues
8. Adding a second component (practice exercise)
9. How to contribute to the PMS Tambo codebase

---

## Part 1: Understanding Tambo (15 min read)

### 1.1 What Problem Does Tambo Solve?

Today, our PMS stakeholders (practice admins, health coaches, account managers) get a static weekly PDF report. If they want to ask "which patients missed their RPM check-in last week?" they have to email engineering and wait for a custom query.

Tambo lets us build a **chat sidebar** where users type questions in plain English and get back **real React components** — charts, tables, dashboards — populated with live data from our APIs. The AI agent decides which component to show based on the question.

### 1.2 How Tambo Works — The Three Pieces

Think of Tambo as a translator sitting between a user's question and your React components.

```
USER QUESTION                    TAMBO AGENT                     YOUR CODE
─────────────                    ───────────                     ─────────
"Show me enrollment              Thinks: "This is about          Calls queryPatientStatus()
 for Dr. Smith's                 enrollment metrics.             → hits Spring Boot API
 practice"                       I should use the                → returns data
                                 EnrollmentDashboard             
                                 component and call              Renders <EnrollmentDashboard>
                                 queryPatientStatus              with the API data as props
                                 to get data."                   
                                                                 User sees a live chart
```

**The three things you define:**

| You Build | What It Does | Example |
|-----------|-------------|---------|
| **Components** | React components with a Zod schema describing their props | `EnrollmentDashboard`, `EncounterTable` |
| **Tools** | Functions that fetch data (usually API calls) | `queryPatientStatus()` → calls Spring Boot |
| **Descriptions** | Text that tells the AI when to use each component/tool | "Use this when the user asks about enrollment rates" |

The AI reads your descriptions and schemas, decides what to call, and Tambo streams the result into your component.

### 1.3 Key Vocabulary

| Term | Meaning |
|------|---------|
| **Generative component** | A component rendered once in response to a message (charts, tables, summaries) |
| **Interactable component** | A component that persists and updates across messages (task boards, forms) |
| **TamboProvider** | The React context wrapper that connects your app to the Tambo backend |
| **Thread** | A conversation (list of messages). Each message can have text and/or a rendered component |
| **Tool** | A function the AI agent can call to get data or perform actions |
| **Zod schema** | A TypeScript-first schema declaration that defines the shape of your component props |
| **Context helper** | Extra info you pass to the AI (current page, user role, selected org) |

### 1.4 Our Architecture

```
┌─────────────────────────────────────────────────┐
│              Your Browser                        │
│                                                  │
│  PMS Dashboard          Analytics Sidebar        │
│  (existing views)       (Tambo-powered)          │
│                         ┌──────────────────┐     │
│                         │ User types query │     │
│                         │ ────────────────│     │
│                         │ Tambo renders    │     │
│                         │ component with   │     │
│                         │ live data        │     │
│                         └────────┬─────────┘     │
└──────────────────────────────────┼───────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   Tambo Backend (Docker)     │
                    │   Manages conversations,     │
                    │   calls the LLM, streams     │
                    │   props to your components   │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   MPS Spring Boot API     │
                    │   Your tools call these      │
                    │   endpoints to get data      │
                    └─────────────────────────────┘
```

---

## Part 2: Environment Setup (30 min)

### 2.1 Prerequisites Checklist

Before you start, confirm you have everything installed. Open a terminal and run each command:

```bash
node --version
# Need: v22.x.x or higher
# If not: nvm install 22 && nvm use 22

npm --version
# Need: 11.x.x or higher

docker --version
# Need: 24.x or higher

docker compose version
# Need: v2.x or higher

git --version
# Need: 2.x or higher
```

If any of these fail, install the missing tool before continuing. Ask the team lead for help if needed.

### 2.2 Clone and Install

```bash
# Clone the PMS frontend repo (which already includes Tambo integration)
cd ~/projects
git clone git@github.com:utexas-demo/pms-frontend.git
cd pms-frontend

# Switch to the tambo-integration branch
git checkout feature/tambo-pms-integration

# Install dependencies (this includes @tambo-ai/react and zod)
npm install
```

### 2.3 Start the Backend Services

You need three services running. Open three terminal tabs:

**Terminal 1 — Tambo Database (PostgreSQL)**

```bash
cd ~/projects/tambo
docker compose --env-file docker.env up postgres -d

# Verify it started
docker ps | grep postgres
# You should see a running container
```

**Terminal 2 — Tambo Backend (API + Dashboard)**

```bash
cd ~/projects/tambo
npm run dev:cloud

# Wait for output like:
#   ✓ API ready on http://localhost:3001
#   ✓ Web ready on http://localhost:3000
```

**Terminal 3 — MPS Spring Boot API**

```bash
cd ~/projects/pms-backend
./mvnw spring-boot:run

# Wait for:
#   Started MPSApiApplication in X seconds
#   Listening on http://localhost:8080
```

### 2.4 Configure Your Environment

Copy the example env file and fill in your values:

```bash
cd ~/projects/pms-frontend
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
# Tambo self-hosted backend
NEXT_PUBLIC_TAMBO_API_KEY=ask_team_lead_for_shared_dev_key
NEXT_PUBLIC_TAMBO_API_URL=http://localhost:3001

# MPS backend
NEXT_PUBLIC_MEDIFY_API_URL=http://localhost:8080
```

If you need to generate your own Tambo API key:

1. Open http://localhost:3000/dashboard
2. Log in (or create an account on the local instance)
3. Open the "MPS PMS" project
4. Go to Settings → API Keys → Generate
5. Paste the key into your `.env.local`

### 2.5 Start the Frontend

```bash
cd ~/projects/pms-frontend
npm run dev

# Opens at http://localhost:3030
```

### 2.6 Verify Everything Works

Open http://localhost:3030/dashboard in your browser. You should see the PMS dashboard with an **Analytics Sidebar** on the right side. Type "hello" and press Enter. If you get a text response from the AI, your setup is working.

**Checkpoint:** All four services running, sidebar responding to messages.

---

## Part 3: Build Your First Component (45 min)

Let's build a simple component from scratch so you understand every piece.

### 3.1 What We Are Building

A **NoShowAlert** component that displays a list of patients who missed their appointments today, with a count and urgency indicator. The user will trigger it by asking something like "Who were my no-shows today?"

### 3.2 Step 1 — Create the React Component

Create `src/components/tambo-pms/no-show-alert.tsx`:

```tsx
"use client";

interface NoShowPatient {
  name: string;
  appointmentTime: string;
  encounterType: string;
  healthCoach: string;
  phone: string;
}

interface NoShowAlertProps {
  date?: string;
  patients?: NoShowPatient[];
  totalScheduled?: number;
}

export default function NoShowAlert({
  date = "Today",
  patients = [],
  totalScheduled = 0,
}: NoShowAlertProps) {
  const noShowCount = patients.length;
  const noShowRate = totalScheduled > 0
    ? ((noShowCount / totalScheduled) * 100).toFixed(1)
    : "0.0";

  // Color coding based on severity
  const severity =
    noShowCount === 0 ? "green" :
    noShowCount <= 3 ? "yellow" : "red";

  const severityStyles = {
    green:  { bg: "bg-green-50",  border: "border-green-200", text: "text-green-800",  badge: "bg-green-100" },
    yellow: { bg: "bg-amber-50",  border: "border-amber-200", text: "text-amber-800",  badge: "bg-amber-100" },
    red:    { bg: "bg-red-50",    border: "border-red-200",   text: "text-red-800",    badge: "bg-red-100" },
  };

  const s = severityStyles[severity];

  return (
    <div className={`rounded-xl border ${s.border} ${s.bg} p-5 max-w-md`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className={`text-sm font-semibold ${s.text}`}>No-Shows — {date}</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${s.badge} ${s.text} font-medium`}>
          {noShowCount} of {totalScheduled} ({noShowRate}%)
        </span>
      </div>

      {/* Patient List */}
      {patients.length === 0 ? (
        <p className="text-sm text-green-600">No missed appointments. Great day!</p>
      ) : (
        <ul className="space-y-3">
          {patients.map((patient, i) => (
            <li key={i} className="bg-white rounded-lg p-3 shadow-sm">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm font-medium text-gray-900">{patient.name}</p>
                  <p className="text-xs text-gray-500">
                    {patient.encounterType} at {patient.appointmentTime}
                  </p>
                  <p className="text-xs text-gray-400">Coach: {patient.healthCoach}</p>
                </div>
                <span className="text-xs text-blue-600 font-mono">{patient.phone}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

This is just a normal React component. Nothing Tambo-specific yet. You could render it anywhere with hardcoded props. Save the file.

### 3.3 Step 2 — Define the Zod Schema

The Zod schema tells Tambo what props your component accepts. The agent reads this schema to understand what data it needs to provide.

Open `src/lib/pms-tambo.ts` and add your component to the `pmsComponents` array:

```typescript
// Add this import at the top
import NoShowAlert from "@/components/tambo-pms/no-show-alert";

// Add this entry to the pmsComponents array
{
  name: "NoShowAlert",
  description:
    "Displays patients who missed their appointments (no-shows) for a given " +
    "day. Shows patient names, appointment times, encounter types, and contact " +
    "info. Includes severity color coding based on no-show count. Use this " +
    "when the user asks about no-shows, missed appointments, or patients who " +
    "didn't show up.",
  component: NoShowAlert,
  propsSchema: z.object({
    date: z.string().describe("The date being reported, e.g. 'February 16, 2026'"),
    patients: z.array(z.object({
      name: z.string().describe("Patient full name"),
      appointmentTime: z.string().describe("Scheduled time, e.g. '9:00 AM'"),
      encounterType: z.string().describe("Type: RPM, CCM, HRA, or APPOINTMENT"),
      healthCoach: z.string().describe("Assigned health coach name"),
      phone: z.string().describe("Patient phone number for follow-up"),
    })).describe("List of patients who no-showed"),
    totalScheduled: z.number().describe("Total appointments scheduled for the day"),
  }),
},
```

**Why descriptions matter:** The `.describe()` calls are not just documentation — the AI reads them to understand what each field means. Better descriptions lead to more accurate component rendering.

### 3.4 Step 3 — Test It

Save your files and let hot reload pick up the changes. Go to the Analytics Sidebar and type:

> "Who were the no-shows today?"

The agent should render your `NoShowAlert` component. Since we haven't connected a real API tool yet, the agent will generate sample data based on your schema descriptions.

**What just happened:**

1. Your message went to the Tambo backend
2. The backend sent it to the LLM with your component schemas
3. The LLM decided `NoShowAlert` was the right component
4. The LLM generated props matching your Zod schema
5. Tambo streamed those props to your React component
6. Your component rendered in the sidebar

---

## Part 4: Build Your First Tool (30 min)

Components render the UI, but **tools** provide the real data. Right now the AI is making up sample data. Let's connect it to our actual API.

### 4.1 What a Tool Does

A tool is a function that the AI agent can call. When a user asks "Who were the no-shows today?", the agent will:

1. Decide it needs no-show data → call the `getNoShows` tool
2. The tool hits the Spring Boot API → returns real patient data
3. The agent feeds that data into the `NoShowAlert` component props

### 4.2 Create the Tool

Open `src/lib/pms-tools.ts` and add:

```typescript
{
  name: "getNoShows",
  description:
    "Fetches the list of patients who no-showed (missed their appointment) " +
    "for a given date and organization. Returns patient names, scheduled times, " +
    "encounter types, health coach assignments, and contact info. Also returns " +
    "the total number of appointments scheduled that day for rate calculation.",
  tool: async (params: { organizationId: string; date: string }) => {
    const { organizationId, date } = params;
    const response = await pmsFetch(
      `/api/dw/events?orgId=${organizationId}&date=${date}&outcome=NO_SHOW`
    );

    // Transform the API response to match what the component expects
    return {
      date: new Date(date).toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      }),
      patients: response.encounters.map((enc: any) => ({
        name: enc.patientName,
        appointmentTime: new Date(enc.scheduledDate).toLocaleTimeString("en-US", {
          hour: "numeric",
          minute: "2-digit",
        }),
        encounterType: enc.encounterType,
        healthCoach: enc.healthCoach,
        phone: enc.patientPhone || "N/A",
      })),
      totalScheduled: response.summary.total,
    };
  },
  inputSchema: z.object({
    organizationId: z.string().describe("The practice/organization ID"),
    date: z.string().describe("Date to check in YYYY-MM-DD format"),
  }),
  outputSchema: z.object({
    date: z.string(),
    patients: z.array(z.object({
      name: z.string(),
      appointmentTime: z.string(),
      encounterType: z.string(),
      healthCoach: z.string(),
      phone: z.string(),
    })),
    totalScheduled: z.number(),
  }),
},
```

### 4.3 Test with Real Data

Save the file and go back to the sidebar. Type:

> "Show me today's no-shows"

This time the agent should:
1. Call `listOrganizations` to get available orgs (from your context or the tool)
2. Call `getNoShows` with today's date
3. Render `NoShowAlert` with real patient data from your Spring Boot API

Check your browser's Network tab to see the actual API call being made to `localhost:8080`.

### 4.4 Testing Tip — Mock Data Fallback

If the Spring Boot API doesn't have the exact endpoint yet, you can temporarily return mock data from your tool:

```typescript
tool: async (params: { organizationId: string; date: string }) => {
  // TODO: Replace with real API call once endpoint is ready
  return {
    date: "February 16, 2026",
    patients: [
      {
        name: "Jane Doe",
        appointmentTime: "9:00 AM",
        encounterType: "RPM",
        healthCoach: "Sarah Johnson",
        phone: "(555) 123-4567",
      },
      {
        name: "John Smith",
        appointmentTime: "10:30 AM",
        encounterType: "CCM",
        healthCoach: "Sarah Johnson",
        phone: "(555) 987-6543",
      },
    ],
    totalScheduled: 12,
  };
},
```

This lets you develop and test the UI without waiting for backend changes.

---

## Part 5: Debugging Common Issues (15 min read)

### 5.1 "The agent shows text instead of my component"

This usually means the agent couldn't match your query to a component.

**Fixes:**
- Make your component `description` more specific and cover more phrasings
- Add keywords the user might use: "no-shows", "missed", "didn't show up", "absent"
- Check that your component is included in the `pmsComponents` array in `pms-tambo.ts`
- Restart the dev server after changes to the component registry

### 5.2 "The component renders but with wrong/empty data"

**Fixes:**
- Check the browser console for errors in your tool function
- Add `console.log` in your tool to see what the API returns
- Verify your `outputSchema` matches what the tool actually returns
- Check the Network tab to see if the Spring Boot API is responding

### 5.3 "Connection refused" or network errors

```bash
# Check which services are running
curl http://localhost:3001/health    # Tambo API
curl http://localhost:8080/actuator/health  # Spring Boot
docker ps                            # PostgreSQL

# If Tambo API is down, restart it
cd ~/projects/tambo && npm run dev:cloud

# If PostgreSQL is down
docker compose --env-file docker.env up postgres -d
```

### 5.4 "Zod validation error"

This means the data returned by your tool doesn't match the `outputSchema`. Check:
- Are field names exactly right (case-sensitive)?
- Are number fields returning numbers (not strings)?
- Are optional fields marked with `.optional()` in the schema?

### 5.5 Reading Agent Reasoning

The Tambo API logs show what the agent is thinking. Look for lines like:

```
[Agent] User message: "show me no-shows"
[Agent] Selected tool: getNoShows
[Agent] Tool input: { organizationId: "org-123", date: "2026-02-16" }
[Agent] Tool output: { date: "...", patients: [...], totalScheduled: 12 }
[Agent] Selected component: NoShowAlert
[Agent] Streaming props...
```

This is invaluable for understanding why the agent made a particular choice.

---

## Part 6: Practice Exercise — Build a Component (45 min)

Now it's your turn. Build one of these components on your own:

### Option A: HealthCoachLeaderboard

A ranked table showing health coaches sorted by encounter completion rate.

**Hints:**
- Props: `coaches` array with name, completedCount, totalAssigned, completionRate, avgEngagementDelta
- Tool: calls `/api/dw/events` grouped by healthCoachId with completion stats
- Useful for: "Who's my top performing health coach?" or "Coach performance this month"

### Option B: DeviceComplianceCard

A summary card showing RPM device reading compliance.

**Hints:**
- Props: totalDevices, activeDevices, complianceRate, devicesNeedingAttention array
- Tool: calls `/api/dw/devices` with compliance filters
- Useful for: "How many devices are reporting?" or "Which devices need attention?"

### Option C: WeeklyTrendMiniChart

A small sparkline-style chart comparing this week vs. last week for a single metric.

**Hints:**
- Props: metricName, thisWeekValue, lastWeekValue, trend array, percentChange
- Tool: calls the relevant DW endpoint with two date ranges
- Useful for: "How are we doing compared to last week?" or "Enrollment trend"

**Steps to follow:**
1. Create the React component in `src/components/tambo-pms/`
2. Define the Zod schema and add it to `pmsComponents` in `pms-tambo.ts`
3. Create a tool in `pms-tools.ts` (use mock data if the API endpoint isn't ready)
4. Test with natural language queries in the sidebar
5. Commit your work on a feature branch

---

## Part 7: Development Workflow and Conventions

### 7.1 File Organization

```
src/
├── components/
│   └── tambo-pms/              # All Tambo PMS components live here
│       ├── enrollment-dashboard.tsx
│       ├── encounter-table.tsx
│       ├── no-show-alert.tsx
│       ├── analytics-sidebar.tsx
│       └── pms-tambo-provider.tsx
├── lib/
│   ├── pms-tambo.ts            # Component registrations (schemas + descriptions)
│   └── pms-tools.ts            # Tool definitions (API calls)
```

### 7.2 Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Component file | kebab-case | `no-show-alert.tsx` |
| Component name | PascalCase | `NoShowAlert` |
| Tool name | camelCase | `getNoShows` |
| Tambo registration name | PascalCase (matches component) | `"NoShowAlert"` |

### 7.3 Writing Good Descriptions

The description is the most important part of the registration. It determines whether the agent picks your component/tool for a given query.

**Do:**
- List specific keywords users might say
- Explain what the component shows
- Mention the data source
- Be specific about when to use it vs. similar components

**Don't:**
- Write generic descriptions like "A chart component"
- Assume the agent knows domain terms — spell out "no-show means missed appointment"
- Leave descriptions shorter than 2 sentences

**Good example:**
```
"Displays patients who missed their appointments (no-shows) for a given day.
Shows patient names, appointment times, encounter types, and contact info.
Includes severity color coding based on no-show count. Use this when the user
asks about no-shows, missed appointments, or patients who didn't show up."
```

**Bad example:**
```
"Shows no-show data"
```

### 7.4 PR Checklist

When submitting a PR that adds a Tambo component:

- [ ] Component file created in `src/components/tambo-pms/`
- [ ] Component registered in `pms-tambo.ts` with Zod schema
- [ ] Description is detailed (2+ sentences, includes trigger keywords)
- [ ] All props have `.describe()` annotations
- [ ] Tool created in `pms-tools.ts` (or mock data with TODO comment)
- [ ] Tool `inputSchema` and `outputSchema` match actual data shapes
- [ ] Tested with at least 3 different natural language phrasings
- [ ] No PHI exposed in component descriptions or tool definitions
- [ ] TypeScript types pass (`npm run check-types`)

### 7.5 Security Reminders

- **Never put PHI in descriptions or schemas.** Descriptions go to the LLM. Only structural info (field names, types) should be in schemas.
- **All data flows through authenticated Spring Boot APIs.** The user's JWT is passed through and validated server-side.
- **The Tambo backend is self-hosted.** Conversation state stays in our PostgreSQL instance.
- **LLM API calls contain only:** the user's natural language query, component/tool schemas, and tool output. No raw patient records are sent to the LLM unless a tool returns them — design tools to return minimal, relevant data.

---

## Part 8: Quick Reference Card

Print this or keep it open while developing.

### Key Commands

```bash
# Start everything (run in separate terminals)
docker compose --env-file docker.env up postgres -d    # DB
npm run dev:cloud                                       # Tambo backend
cd pms-backend && ./mvnw spring-boot:run                # Spring Boot
cd pms-frontend && npm run dev                      # Frontend
```

### Key Files to Edit

| What | Where |
|------|-------|
| Add a component | `src/components/tambo-pms/your-component.tsx` |
| Register it | `src/lib/pms-tambo.ts` → `pmsComponents` array |
| Add a tool | `src/lib/pms-tools.ts` → `pmsTools` array |
| Change sidebar UI | `src/components/tambo-pms/analytics-sidebar.tsx` |
| Change provider config | `src/components/tambo-pms/pms-tambo-provider.tsx` |
| Environment variables | `.env.local` |

### Key URLs

| Service | URL |
|---------|-----|
| PMS Frontend | http://localhost:3030 |
| Tambo Dashboard | http://localhost:3000 |
| Tambo API | http://localhost:3001 |
| MPS API | http://localhost:8080 |
| Drizzle Studio (DB browser) | https://local.drizzle.studio |

### Tambo React Hooks

| Hook | Purpose |
|------|---------|
| `useTamboThread()` | Access current thread messages |
| `useTamboThreadInput()` | Control the message input (value, submit, isPending) |
| `useTamboSuggestions()` | Get AI-generated prompt suggestions |

---

## Next Steps

Once you've completed this tutorial:

1. **Read the PRD** (`PRD-Tambo-PMS-Integration.md`) for the full list of planned components and tools
2. **Pick a Phase 2 component** from the PRD and implement it
3. **Join the Tambo Discord** (https://tambo.co/discord) for community support
4. **Review the Tambo docs** (https://docs.tambo.co) for advanced patterns like interactable components and MCP integration
5. **Pair with a teammate** — build a component together to share knowledge

Questions? Reach out on the `#tambo-pms` Slack channel or tag the team lead in your PR.
