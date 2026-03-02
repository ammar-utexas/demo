# Claude Code Mastery — Developer Tutorial

**Experiment:** 27 — Claude Code (AI-Native Development Environment)
**Category:** Dev Tooling
**Date:** March 2, 2026
**Video Reference:** [Claude Code Complete Guide](https://youtu.be/ZlDnsf_DOzg?si=_PqEbVtiPoilVxHW)

---

## Overview

Claude Code is Anthropic's official CLI tool that transforms a terminal session into an AI-powered development environment. Unlike chatbot interfaces, Claude Code **takes action** — it reads files, writes code, runs commands, and manages entire projects through natural language conversation. This tutorial covers every concept a PMS developer needs to master Claude Code, organized from foundational to autonomous usage.

This experiment consolidates the essential Claude Code knowledge required to maximize productivity across all other PMS experiments (00–26). Every developer on the team should complete this before starting any experiment integration work.

---

## Prerequisites

- Terminal access (macOS, Linux, or WSL on Windows)
- Claude Code installed (`npm install -g @anthropic-ai/claude-code`)
- API key or Claude Max subscription configured
- Git installed and configured

---

## Part 1: The Foundations

### 1.1 What Is Claude Code?

Claude Code is an AI tool that interacts directly with your computer — creating files, building applications, running tests, and automating tasks through plain English. Unlike web-based chatbots that only generate text, Claude Code **executes actions** in your local environment.

**Key distinction:** You describe *what* you want, Claude figures out *how* to do it.

```bash
# Launch Claude Code in the current directory
claude

# Example prompt inside Claude Code
> "Create a FastAPI endpoint for patient search with pagination"
```

Claude will:
1. Read your existing codebase to understand conventions
2. Choose the right files to modify or create
3. Write the code
4. Optionally run tests to verify

### 1.2 The Terminal

The terminal is the black screen where Claude Code runs. You do not need to memorize complex commands — Claude handles the underlying operations. The few commands you need:

| Command | Purpose |
|---------|---------|
| `claude` | Start a new session in the current directory |
| `claude --resume` | Resume your last conversation |
| `claude -p "task"` | Run a task autonomously (headless mode) |
| `Ctrl+C` | Cancel current operation |
| `exit` or `/quit` | End the session |

### 1.3 Prompts

Prompts are what you type to tell Claude Code what to do. Specificity matters — the more context you provide, the better the output.

**Weak prompt:**
> "Fix the bug"

**Strong prompt:**
> "The patient search endpoint at /api/patients returns a 500 error when the search query contains special characters like apostrophes. Fix the SQL injection vulnerability and add input sanitization."

**PMS-specific tips:**
- Reference requirement IDs: *"Implement SUB-PR-BE-001 patient CRUD endpoint"*
- Reference experiment numbers: *"Set up the MCP server per Experiment 09 PRD"*
- Reference file paths: *"Update src/api/routes/patients.py to add pagination"*

### 1.4 Permissions

Claude Code can modify files, run commands, and interact with external services. By default, it asks for your approval before each action.

**Permission levels:**
- **Ask every time** (default) — safest, Claude confirms before each action
- **Pre-approved actions** — configure in `settings.json` for faster workflow

**Pre-approving safe actions in `.claude/settings.json`:**

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(python -m pytest*)"
    ]
  }
}
```

**PMS recommendation:** Pre-approve read operations and test commands. Keep write operations and git push requiring approval.

### 1.5 Tools (Read / Write / Bash)

Claude Code has built-in tools that let it interact with your computer. You describe the goal; Claude picks the right tool.

| Tool | Purpose | Example |
|------|---------|---------|
| **Read** | View file contents | Reading `src/models/patient.py` to understand the schema |
| **Write** | Create or overwrite files | Creating a new API endpoint file |
| **Edit** | Modify specific parts of a file | Updating a function signature |
| **Bash** | Run terminal commands | `python -m pytest`, `git status`, `docker compose up` |
| **Glob** | Find files by pattern | Finding all `*.py` files in `src/api/` |
| **Grep** | Search file contents | Finding all usages of `PatientModel` |
| **Agent** | Delegate to sub-agents | Researching a complex question in parallel |

You rarely need to specify which tool to use — just describe what you want and Claude selects the appropriate tool.

### 1.6 Context Window

The context window is Claude's **short-term memory** — everything it can see and reason about in the current session. It includes:

- Your conversation history
- Files Claude has read
- Command outputs
- System instructions (CLAUDE.md)

**Why it matters:** A cluttered context window leads to "context rot" — Claude starts forgetting earlier context or making mistakes. Keep sessions focused on one task.

**PMS tips:**
- Start a new session for each experiment or feature
- Use `/compact` to summarize and free space when the context gets full
- Avoid reading very large files unnecessarily — read specific line ranges instead

### 1.7 Conversation History / Resume

Claude automatically saves your conversations. You can resume from where you left off:

```bash
# Resume the most recent conversation
claude --resume

# List recent conversations and pick one
claude --resume
```

**When to resume vs. start fresh:**
- **Resume:** Continuing a multi-step implementation (e.g., halfway through setting up Experiment 09)
- **Start fresh:** Switching to a different task or experiment

### 1.8 Token Usage / Cost Tracking

Claude Code usage is measured in **tokens** — roughly ¾ of a word.

| Model | Speed | Intelligence | Cost |
|-------|-------|-------------|------|
| Haiku 4.5 | Fastest | Good | Lowest |
| Sonnet 4.6 | Fast | Great | Medium |
| Opus 4.6 | Slower | Best | Highest |

**Cost optimization tips:**
- Use Haiku for simple tasks (formatting, renaming, boilerplate)
- Use Sonnet for most development work (default)
- Reserve Opus for complex architectural decisions, debugging, and security-sensitive code
- See [Experiment 15: Claude Model Selection](15-PRD-ClaudeModelSelection-PMS-Integration.md) for automated model routing

---

## Part 2: Making Claude Personal

### 2.1 CLAUDE.md

`CLAUDE.md` is a markdown file at the root of your project (or in `~/.claude/`) that Claude reads **first** in every new session. It contains your preferences, rules, and project structure.

The PMS project already has a comprehensive `CLAUDE.md` — see the project root. Key sections:

- **Repository docs as single source of truth** — all decisions go in `docs/`
- **Directory structure** — where different types of docs live
- **When to update docs** — before starting work, after completing features
- **Rules** — never rely on memory, read before you build, keep docs focused

**Creating personal preferences in `~/.claude/CLAUDE.md`:**

```markdown
# Personal Preferences
- Always use type hints in Python code
- Prefer async/await over synchronous code
- Run pytest after every code change
- Use conventional commits format
```

### 2.2 Memory Usage

Claude Code maintains an **auto-memory file** that persists across sessions. It stores:

- Patterns confirmed across multiple interactions
- Key file paths and project structure
- Your workflow preferences
- Solutions to recurring problems

Memory is stored in `.claude/projects/<project>/memory/MEMORY.md` and is automatically loaded into every session.

**You can explicitly ask Claude to remember things:**
> "Remember: always use `pms-backend` Docker network for inter-service communication"

### 2.3 Compact Context

When the context window fills up, Claude automatically summarizes key information to free space. You can also trigger this manually:

```
/compact
```

**When to compact:**
- After a long debugging session
- After reading many large files
- When Claude starts repeating itself or forgetting earlier context
- Before starting a new sub-task within the same session

### 2.4 Models (Sonnet, Opus, Haiku)

Switch models mid-session based on task complexity:

| Task Type | Recommended Model | Why |
|-----------|------------------|-----|
| Code formatting, renaming | Haiku | Fast, cheap, sufficient |
| Feature implementation | Sonnet | Good balance of speed and quality |
| Architecture design | Opus | Best reasoning for complex decisions |
| Security review | Opus | Critical to catch vulnerabilities |
| Writing tests | Sonnet | Good pattern recognition |
| Debugging | Opus | Deep reasoning through complex bugs |

**Switch models with the `/model` command or use `/fast` to toggle fast mode (same model, faster output).**

### 2.5 Denying Access to Files

Prevent Claude from reading large, sensitive, or irrelevant files via `.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(*.pdf)",
      "Read(*.docx)",
      "Read(node_modules/**)",
      "Read(.env*)"
    ]
  }
}
```

**PMS-specific deny recommendations:**
- `.env` files (contain secrets)
- `node_modules/` and `__pycache__/` (generated files)
- Large binary files (PDFs, images, .docx)
- `*.lock` files (too large, rarely useful to read)

### 2.6 Flags

Flags customize Claude Code behavior for a specific session:

| Flag | Purpose | Example |
|------|---------|---------|
| `--resume` | Resume last conversation | `claude --resume` |
| `-p "task"` | Headless mode (no interaction) | `claude -p "run all tests"` |
| `--model` | Choose model | `claude --model opus` |
| `--allowedTools` | Pre-approve specific tools | `claude --allowedTools Read,Grep` |
| `--verbose` | Show detailed tool usage | `claude --verbose` |

---

## Part 3: Power Features

### 3.1 Extended Thinking

Claude can reason through complex problems step-by-step using a dedicated "thinking budget." This is enabled by default and is especially valuable for:

- Debugging multi-file issues
- Designing architecture
- Writing complex algorithms
- Security analysis

**You don't need to do anything to enable it** — Claude automatically uses extended thinking when the problem requires it. For harder problems, you can encourage deeper reasoning:

> "Think carefully through the race conditions in the concurrent prescription update flow before suggesting a fix."

### 3.2 Slash Commands

Built-in shortcuts for common actions:

| Command | Action |
|---------|--------|
| `/init` | Generate a CLAUDE.md for the current project |
| `/compact` | Summarize context to free memory |
| `/clear` | Clear conversation history |
| `/model` | Switch AI model |
| `/fast` | Toggle fast output mode |
| `/re` | Review and restore previous file states |
| `/help` | Show available commands |

**Custom slash commands:** Create `.claude/commands/` directory with markdown files:

```markdown
<!-- .claude/commands/pms-test.md -->
Run the PMS backend test suite with coverage:
1. cd to pms-backend/
2. Run: python -m pytest --cov=src --cov-report=term-missing
3. Report any failures with file paths and line numbers
```

Then invoke with `/pms-test` in any session.

### 3.3 Skills

Skills are pre-written instructions that teach Claude how to handle specific tasks well. They improve output quality for specialized work.

**PMS-relevant skills:**
- HIPAA compliance checking
- FHIR resource mapping
- Clinical documentation formatting
- Database migration generation

See [Experiment 19: Superpowers](19-PRD-Superpowers-PMS-Integration.md) for the PMS skills framework and [Experiment 24: Knowledge Work Plugins](24-PRD-KnowledgeWorkPlugins-PMS-Integration.md) for packaging skills into distributable plugins.

### 3.4 Hooks

Hooks are custom scripts that trigger automatically after specific events:

| Hook Event | Use Case |
|-----------|----------|
| `PostToolUse` (Edit/Write) | Auto-format code after file changes |
| `PostToolUse` (Bash) | Log all commands for audit |
| `PreToolUse` | Validate before destructive actions |

**Example: Auto-format Python files after edit:**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "if [[ \"$CLAUDE_FILE_PATH\" == *.py ]]; then ruff format \"$CLAUDE_FILE_PATH\"; fi"
      }
    ]
  }
}
```

### 3.5 MCP Servers

Model Context Protocol (MCP) connects Claude Code to external tools — databases, project management tools, APIs — allowing it to interact with your full tech stack.

**PMS-relevant MCP connections:**
- PMS Backend API (Experiment 09) — Claude can query patient records, encounters, prescriptions directly
- PostgreSQL — Direct database queries for debugging
- GitHub — PR management, issue tracking
- Docker — Container management

See [Experiment 09: MCP](09-PRD-MCP-PMS-Integration.md) for the complete PMS MCP server implementation.

### 3.6 Sub-Agents

Sub-agents are specialists that run in their own separate context window. They improve quality and speed by:

- **Isolating research** — exploring code without cluttering your main context
- **Parallelizing work** — multiple sub-agents can run simultaneously
- **Specializing** — different agent types for different tasks (explore, review, plan)

**Available sub-agent types:**
| Type | Purpose |
|------|---------|
| `Explore` | Fast codebase exploration and search |
| `Plan` | Architecture and implementation planning |
| `general-purpose` | Complex multi-step research |
| `code-reviewer` | Code review against project standards |

**When to use sub-agents:**
- Searching for patterns across many files
- Reviewing code before committing
- Exploring unfamiliar parts of the codebase
- Running parallel research tasks

### 3.7 Agent Teams

A newer feature where multiple agents communicate directly and share a task list. Designed for complex builds requiring collaboration.

**How it works:**
1. A lead agent breaks a task into sub-tasks
2. Sub-agents claim tasks from the shared task list
3. Agents work in parallel, each in their own context
4. Results are coordinated through the shared state

See [Experiment 14: Agent Teams](14-agent-teams-claude-whitepaper.md) for architecture details and [14-AgentTeams-Developer-Tutorial](14-AgentTeams-Developer-Tutorial.md) for hands-on exercises.

### 3.8 Image / Screenshot Support

Claude Code can analyze images and screenshots, enabling:

- **UI bug reports:** Drop a screenshot and say "fix this layout issue"
- **Design-to-code:** Upload a mockup and say "build this component"
- **Error analysis:** Screenshot an error dialog for faster debugging

```bash
# Reference an image in your prompt
> "Look at /tmp/screenshot.png and fix the alignment of the patient list table"
```

### 3.9 Checkpoints / Undo

Claude automatically creates session-level snapshots before every file edit. If something goes wrong:

```
/re
```

This shows a list of previous states you can review and restore. Use it when:
- A refactoring went too far
- A generated file has issues
- You want to compare before/after states

---

## Part 4: Using Claude Autonomously

### 4.1 Git Integration

Claude Code integrates with Git and GitHub for version control:

```bash
# Claude can handle the full git workflow
> "Commit the patient search changes with a descriptive message"
> "Create a PR for the FHIR integration feature"
> "Review the diff and suggest improvements"
```

**PMS git conventions:**
- Conventional commit messages (see recent git log for style)
- Feature branches for experiment integrations
- PRs require review before merging to main

### 4.2 Headless Mode (CLI Mode)

Run Claude Code with **zero human interaction** using the `-p` flag:

```bash
# Run tests autonomously
claude -p "Run all backend tests and report failures"

# Generate documentation
claude -p "Generate API docs for all endpoints in src/api/routes/"

# Security scan
claude -p "Review src/api/ for OWASP Top 10 vulnerabilities"
```

**PMS use cases for headless mode:**
- CI/CD pipeline integration (Experiment 12: AI Zero-Day Scan)
- Automated test execution
- Batch documentation generation
- Pre-commit security checks

### 4.3 Claude Max vs API (How You Pay)

| Option | Model | Pricing | Best For |
|--------|-------|---------|----------|
| **Claude Max** | Subscription | $20–$200/month | Individual developers, predictable costs |
| **API** | Pay-as-you-go | Per-token pricing | Teams, CI/CD, heavy usage, production |

**PMS recommendation:** Use Claude Max for interactive development. Use API keys for CI/CD headless mode and automated scanning.

### 4.4 Worktrees

Worktrees enable **multiple Claude instances** working on different tasks simultaneously, each in an isolated copy of the repository:

```bash
# Start a worktree session
> /worktree

# Claude creates an isolated branch and working directory
# You can run another Claude session in the main repo at the same time
```

**PMS parallel development scenarios:**
- One worktree: implementing FHIR endpoints (Experiment 16)
- Another worktree: building Storybook components (Experiment 01)
- Main repo: reviewing PRs and managing releases

Each worktree has full isolation — changes in one cannot affect another until explicitly merged.

---

## Exercises

### Exercise 1: Foundation Setup (15 min)

1. Launch Claude Code in the PMS demo repo
2. Ask Claude to read `CLAUDE.md` and summarize the key rules
3. Ask Claude to find all experiment PRD files using Glob
4. Practice resuming a conversation with `claude --resume`

### Exercise 2: Personalization (20 min)

1. Create a custom slash command `.claude/commands/pms-status.md` that checks git status, lists recent commits, and summarizes any uncommitted changes
2. Configure `settings.json` to deny access to `*.pdf` and `*.docx` files
3. Pre-approve Read, Glob, and Grep tools in settings
4. Test your slash command by running `/pms-status`

### Exercise 3: Power Features (30 min)

1. Use a sub-agent to explore how MCP is referenced across all experiment docs
2. Create a custom hook that runs `ruff check` after any Python file edit
3. Ask Claude to analyze a screenshot of the PMS architecture diagram
4. Practice using `/re` to undo a file change

### Exercise 4: Autonomous Execution (20 min)

1. Run Claude in headless mode to generate a summary of all experiment PRDs
2. Set up a worktree and make a change in isolation
3. Practice the full git workflow: branch → implement → commit → PR

---

## Relationship to Other Experiments

| Experiment | Relationship |
|-----------|-------------|
| 09 MCP | Claude Code connects to PMS via MCP servers |
| 14 Agent Teams | Advanced multi-agent patterns built on Claude Code |
| 19 Superpowers | Skills framework running inside Claude Code |
| 24 Knowledge Work Plugins | Plugin packaging for Claude Code |
| 12 AI Zero-Day Scan | Headless mode for automated security scanning |
| 15 Claude Model Selection | Model routing applies to Claude Code model choices |

---

## Further Reading

- [Video: Claude Code Complete Guide](https://youtu.be/ZlDnsf_DOzg?si=_PqEbVtiPoilVxHW)
- [Experiment 14: Agent Teams](14-agent-teams-claude-whitepaper.md) — Multi-agent architecture
- [Experiment 19: Superpowers](19-PRD-Superpowers-PMS-Integration.md) — Skills framework
- [Experiment 24: Knowledge Work Plugins](24-PRD-KnowledgeWorkPlugins-PMS-Integration.md) — Plugin packaging
