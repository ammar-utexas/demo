# Storybook Getting Started Guide

**Document ID:** PMS-CONFIG-STORYBOOK-001
**Version:** 1.0
**Date:** 2026-02-16
**Applies To:** `pms-frontend` (Next.js 15 / React 19 / TypeScript / Tailwind CSS 3)

---

## What is Storybook?

Storybook is an open-source tool for building, testing, and documenting UI components in isolation. Instead of navigating through the full application to see a component, you can view and interact with every state of every component in a dedicated sandbox.

For the PMS project, Storybook serves as:

- **A living component library** — browse all UI primitives (Button, Card, Badge, Input) and layout components (Sidebar, Header)
- **A visual testing tool** — verify that components render correctly across all variants and states
- **Developer documentation** — new team members can explore the UI without running the full app
- **A stakeholder demo tool** — show clickable UI prototypes without backend dependencies

---

## Prerequisites

Before starting, ensure you have:

- **Node.js** 18+ installed (`node --version`)
- **npm** 9+ installed (`npm --version`)
- The `pms-frontend` repo cloned and dependencies installed:

```bash
cd pms-frontend
npm install
```

---

## Installation

### Step 1: Initialize Storybook

From the `pms-frontend` root directory, run:

```bash
npx storybook@latest init
```

This will:
- Detect your Next.js + React + TypeScript setup
- Install `@storybook/nextjs`, `@storybook/react`, and related packages
- Create `.storybook/` config directory
- Create example stories in `src/stories/` (you can delete these later)

### Step 2: Configure Tailwind CSS

Storybook needs to load your Tailwind styles. Edit `.storybook/preview.ts` to import your global CSS:

```typescript
// .storybook/preview.ts
import type { Preview } from "@storybook/react";
import "../src/app/globals.css";

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
};

export default preview;
```

### Step 3: Configure Path Aliases

Your project uses `@/*` path aliases. Edit `.storybook/main.ts` to support them:

```typescript
// .storybook/main.ts
import type { StorybookConfig } from "@storybook/nextjs";
import path from "path";

const config: StorybookConfig = {
  stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
  addons: [
    "@storybook/addon-onboarding",
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
  ],
  framework: {
    name: "@storybook/nextjs",
    options: {},
  },
  webpackFinal: async (config) => {
    if (config.resolve) {
      config.resolve.alias = {
        ...config.resolve.alias,
        "@": path.resolve(__dirname, "../src"),
      };
    }
    return config;
  },
};

export default config;
```

### Step 4: Add npm Scripts

Add these scripts to `package.json`:

```json
{
  "scripts": {
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  }
}
```

### Step 5: Run Storybook

```bash
npm run storybook
```

Storybook will open at **http://localhost:6006**.

---

## Project Structure

After setup, your project will look like this:

```
pms-frontend/
├── .storybook/
│   ├── main.ts          # Storybook configuration (addons, framework, webpack)
│   └── preview.ts       # Global decorators, styles, and parameters
├── src/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.tsx
│   │   │   ├── button.stories.tsx    ← story file (co-located)
│   │   │   ├── card.tsx
│   │   │   ├── card.stories.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── badge.stories.tsx
│   │   │   ├── input.tsx
│   │   │   └── input.stories.tsx
│   │   └── layout/
│   │       ├── sidebar.tsx
│   │       ├── sidebar.stories.tsx
│   │       ├── header.tsx
│   │       └── header.stories.tsx
```

**Convention:** Story files are co-located with their component using the `.stories.tsx` suffix.

---

## Writing Your First Story

A "story" represents a single state of a component. Each component can have multiple stories showing different variants, sizes, and states.

### Anatomy of a Story File

```typescript
// src/components/ui/button.stories.tsx
import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./button";

// 1. Meta — defines the component and its controls
const meta: Meta<typeof Button> = {
  title: "UI/Button",              // Sidebar path in Storybook
  component: Button,               // The component to render
  tags: ["autodocs"],              // Auto-generate a docs page
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "danger", "ghost"],
    },
    size: {
      control: "select",
      options: ["sm", "md", "lg"],
    },
    disabled: { control: "boolean" },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

// 2. Stories — each export is a named story
export const Primary: Story = {
  args: {
    children: "Primary Button",
    variant: "primary",
    size: "md",
  },
};

export const Secondary: Story = {
  args: {
    children: "Secondary Button",
    variant: "secondary",
    size: "md",
  },
};

export const Danger: Story = {
  args: {
    children: "Delete Patient",
    variant: "danger",
    size: "md",
  },
};

export const Ghost: Story = {
  args: {
    children: "Cancel",
    variant: "ghost",
    size: "md",
  },
};

export const Small: Story = {
  args: {
    children: "Small",
    variant: "primary",
    size: "sm",
  },
};

export const Large: Story = {
  args: {
    children: "Large Button",
    variant: "primary",
    size: "lg",
  },
};

export const Disabled: Story = {
  args: {
    children: "Disabled",
    variant: "primary",
    disabled: true,
  },
};
```

---

## Running and Building

| Command | Description |
|---|---|
| `npm run storybook` | Start dev server at http://localhost:6006 |
| `npm run build-storybook` | Build static site to `storybook-static/` |

The static build can be deployed to GitHub Pages, Netlify, or any static hosting for stakeholder reviews.

---

## Troubleshooting

### Tailwind styles not loading
- Ensure `globals.css` is imported in `.storybook/preview.ts`
- Verify `.storybook/` is not excluded in `tailwind.config.ts` content paths

### Path alias `@/` not resolving
- Confirm `webpackFinal` is configured in `.storybook/main.ts`
- Restart Storybook after config changes

### Next.js components (Link, Image, useRouter) not working
- The `@storybook/nextjs` framework handles most Next.js features automatically
- For `useRouter` / `usePathname`, Storybook provides mock implementations

### React 19 compatibility
- Ensure you're using Storybook 8.x+ which supports React 19
- If issues arise, check: `npx storybook@latest doctor`

---

## Next Steps

- Read the [Storybook Developer Tutorial](storybook-developer-tutorial.md) for writing stories for all PMS components
- Explore [Storybook docs](https://storybook.js.org/docs) for advanced features (interaction testing, visual regression, accessibility)
