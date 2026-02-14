# Project Agent Instructions

## NotebookLM as Single Source of Truth

This project uses **NotebookLM** as the central knowledge repository. All project context, decisions, and implementation details must be stored there — not in local markdown files, comments, or memory alone.

### Notebook Management

- At the start of each session, check for an existing project notebook using `notebooklm notebook list`. If none exists, create one with `notebooklm create "<project-name>"`.
- The notebook ID should be stored in `.notebooklm-project.json` at the project root for persistence across sessions.

### What to Store

**Architectural Decisions**
- Record every architectural decision as a notebook source immediately when made.
- Include the context, options considered, rationale, and trade-offs.
- Tag entries clearly (e.g., prefix with `[ADR]` in the title).

**Implementation Details**
- After completing a feature or significant change, add a source summarizing:
  - What was built and why
  - Key files and components involved
  - Any non-obvious design choices
  - Known limitations or follow-up work

**Bug Fixes and Incidents**
- Document root cause analysis for non-trivial bugs.
- Include what was tried, what failed, and what ultimately resolved the issue.

**API Contracts and Interfaces**
- Store API schemas, interface definitions, and integration details.
- Update these whenever contracts change.

**Dependencies and Configuration**
- Record decisions about dependencies (why chosen, alternatives rejected).
- Document environment-specific configuration and setup steps.

### When to Update the Notebook

- **Before starting work**: Query the notebook for relevant context (`notebooklm ask <notebookId> "<question>"`).
- **After completing a feature**: Add implementation details as a new source.
- **After an architectural decision**: Record it immediately — do not defer.
- **After resolving a bug**: Document the root cause and fix.
- **When onboarding context changes**: Update or replace outdated sources.

### How to Interact with NotebookLM

Use the `notebooklm` CLI or the `notebooklm-mcp` MCP tools:

```bash
# List notebooks
notebooklm list

# Ask the notebook a question (use it before making decisions)
notebooklm ask <notebookId> "How does authentication work in this project?"

# Add a source (after completing work)
notebooklm source add <notebookId> --text "## [ADR] Chose JWT over sessions ..."
```

### Rules

1. **Never rely on memory alone.** If a decision or implementation detail matters, it goes in the notebook.
2. **Query before you build.** Check the notebook for existing context before starting any non-trivial task.
3. **Keep sources focused.** One topic per source — don't dump everything into a single entry.
4. **Update, don't duplicate.** If context has changed, update the existing source rather than adding a conflicting one.
5. **Notebook is authoritative.** When there is a conflict between the notebook and other sources (comments, docs, memory), the notebook wins.
