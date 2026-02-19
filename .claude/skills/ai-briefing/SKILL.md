---
name: ai-briefing
description: Generate a comprehensive AI Intelligence Brief covering the last 14 days of AI ecosystem developments relevant to a healthcare technology CTO. Creates a timestamped markdown file in the news/ directory.
argument-hint: [optional focus area or date override]
---

# AI Intelligence Briefing Skill

You are generating a comprehensive **AI Intelligence Brief** for Ammar Kazanli, CTO of a healthcare technology company focused on AI-powered automation, voice AI systems, remote patient monitoring, and AI-assisted development workflows.

Your task is to research the last 14 days of AI ecosystem news and produce a **single timestamped markdown file** in the `news/` directory.

---

## Step 0: Setup

1. Create the `news/` directory if it does not exist.
2. Generate the filename using the current timestamp: `YYYY-MM-DD-HH-MM-SS.md` (use `date "+%Y-%m-%d-%H-%M-%S"`).
3. Calculate the coverage period: today's date minus 14 days through today.
4. If `$ARGUMENTS` contains a specific focus area, give it extra weight in the research and scoring. Otherwise, cover all categories equally.

## Step 1: Research (Parallel Web Searches)

Use **WebSearch** extensively across all categories below. Launch searches in parallel batches to maximize efficiency. Perform **at least 12 distinct searches** covering:

### 1.1 Major AI Labs
Search for announcements, model releases, and significant updates from:
- Anthropic (Claude models, Claude Code, API changes, enterprise features)
- OpenAI (GPT models, ChatGPT, Codex, API changes, partnerships)
- Google (Gemini models, Workspace AI, API changes, Google I/O)
- Meta (LLaMA models, open-weight releases)
- xAI (Grok models, voice, API access)
- Mistral (model releases, edge deployment, pricing)
- Cohere (enterprise AI, RAG, embeddings)

### 1.2 AI Coding & Dev Tools
Search for updates from:
- GitHub Copilot (agent mode, features, pricing)
- Cursor (new versions, multi-agent, features)
- Windsurf (Cascade updates, features)
- Claude Code (enterprise adoption, GitHub integration, new capabilities)
- Devin (autonomous coding, pricing, capabilities)
- Replit Agent (new versions, autonomous workflows)
- v0 / Bolt.new / Lovable (AI app builders, vibe coding)

### 1.3 AI Automation Platforms
Search for updates from:
- n8n (AI agent features, HITL, new nodes)
- Make / Zapier AI (automation capabilities)
- LangChain / LangGraph (framework updates, production features)
- CrewAI (multi-agent, new versions)
- AutoGen (Microsoft, agent frameworks)
- OpenAI Agents SDK (Agent Builder, ChatKit)

### 1.4 Infrastructure & Models
Search for:
- Hugging Face (trending models, platform updates)
- Ollama (new versions, performance improvements)
- vLLM (inference optimizations)
- New open-weight models and fine-tuning breakthroughs
- NVIDIA AI inference updates
- GitHub trending AI repositories

### 1.5 Voice & Healthcare AI
Search for:
- Voice AI platforms (Speechmatics, Deepgram, AssemblyAI, ElevenLabs)
- Medical AI tools and clinical AI
- EHR integrations and ambient clinical AI
- Remote patient monitoring and wearables
- Healthcare AI market developments

### 1.6 Standards & Regulation
Search for:
- MCP (Model Context Protocol) updates and ecosystem
- AI executive orders and federal policy
- HIPAA/AI guidance and enforcement
- FDA AI/ML framework updates
- State AI regulation (Colorado, etc.)
- Healthcare compliance developments

### 1.7 Community & Research
Search for:
- GitHub trending repos (AI-tagged)
- Reddit community sentiment (r/LocalLLaMA, r/ClaudeAI, r/ChatGPT, r/MachineLearning)
- ArXiv notable papers (applied AI, agents, healthcare AI)
- Product Hunt AI launches

## Step 2: Score Each Development

For each notable development found, assign a **Disruption Score (1-10)**:

| Score Range | Meaning |
|-------------|---------|
| 1-3 | Incremental improvement, nice to know |
| 4-6 | Meaningful capability change, worth evaluating within 30 days |
| 7-8 | Significant shift, should prototype or adopt within 2 weeks |
| 9-10 | Potential game-changer, immediate action recommended |

**Score adjustment rules:**
- +1 for sustained community momentum over 48hrs
- +1 for enterprise/healthcare adoption signals
- -1 for unresolved critical bugs or broken promises
- -1 for hype fade with no real usage evidence

**Always frame impact through these lenses:**
1. Healthcare AI automation and voice AI systems
2. AI-assisted software development workflows
3. Remote patient monitoring and data integration
4. Teaching AI/data science in biomedical informatics

## Step 3: Generate the Report

Write the markdown file with the following structure. Every section is **required**.

```markdown
# AI INTELLIGENCE BRIEF — {Full Date}

**Coverage Period:** {14 days ago} - {today}
**Prepared For:** Ammar Kazanli, CTO — Healthcare Technology / AI Automation / Voice AI / Remote Patient Monitoring
**Generated:** {timestamp}

---

## TOP SCORER OF THE DAY

**{Item Name} — Score: X/10**

Why this score: {2-3 sentence justification citing specific signals — e.g., GitHub stars growth, enterprise announcements, benchmark results, community validation}

---

## MOVERS (Score changed this period)

| Item | Score | Change | Reason |
|------|-------|--------|--------|
{Items whose scores would have changed from a previous brief. For first-time items, mark as NEW.}

---

## NEW ENTRIES

| Item | Score | What + Why It Matters |
|------|-------|-----------------------|
{All newly discovered items this period with one-line descriptions}

---

## TOP 10 LINKS I MUST VISIT TODAY

{Curate the 10 most important URLs from the research that Ammar should personally read today. Rank by urgency and relevance to his work. For each link:}

| # | Link | Why Visit | Score Context |
|---|------|-----------|---------------|
| 1 | [{descriptive title}]({URL}) | {One sentence on what you'll learn and why it matters today} | {Related item score}/10 |
| 2 | ... | ... | ... |
| ... | ... | ... | ... |
| 10 | ... | ... | ... |

{Selection criteria for these 10 links:
- Prioritize official announcements, release posts, and technical docs over news aggregator summaries
- Include at least 1 link from each of these categories: AI models, dev tools, healthcare AI, regulation
- Bias toward links with actionable information (APIs to try, docs to read, tools to evaluate)
- Include any link that relates to a score 8+ item
- Prefer primary sources (company blogs, GitHub repos, official docs) over secondary coverage}

---

## ACTIVE WATCHLIST (Top 15 by Score)

| Rank | Item | Score | Status | Action By |
|------|------|-------|--------|-----------|
{Top 15 items sorted by score descending. Status options: Adopt / Prototype / Evaluate / Watch}

---

## DETAILED ANALYSIS BY CATEGORY

---

### 1. Major AI Labs

{For each lab with news this period, include:}

#### {Lab Name} — {Headline}

**Source:** {Markdown links to sources}

**What Changed:**
{Bullet list of specific changes}

**Impact on You:**
{Bullet list with italic category labels: *Healthcare AI automation*, *AI-assisted development*, *Remote patient monitoring*, *Teaching*}

**Disruption Score: X/10** — {One-line action recommendation}

---

### 2. AI Coding & Dev Tools

{Same format as above for each tool with significant news}

---

### 3. AI Automation Platforms

{Same format}

---

### 4. Infrastructure & Open Models

{Same format}

---

### 5. Voice & Healthcare AI

{Same format}

---

### 6. Standards & Regulation

{Same format, with sub-sections for MCP, FDA, State regulation, HIPAA as relevant}

---

## FULL WATCHLIST DETAIL

| # | Item | Score | Entered | Days Tracked | Trend | Notes |
|---|------|-------|---------|--------------|-------|-------|
{All tracked items with entry dates, trend arrows (NEW/+N/-N/=), and brief notes}

---

## RECOMMENDED ACTIONS

### Immediate (This Week)

{3-4 numbered actions with bold titles and explanations}

### This Sprint (Next 2 Weeks)

{3-4 numbered actions}

### This Month

{3-4 numbered actions}

---

## MARKET CONTEXT & TRENDS

### The Big Picture ({coverage period})

{5-7 numbered macro observations about the AI landscape, each as a bold thesis with 2-3 sentences of supporting evidence. Always relate back to healthcare tech / AI automation / voice AI / RPM / AI-assisted dev.}

---

*Next brief: {tomorrow's date}*
*Archive items scoring below 5 after 14 days on watchlist*
*Flag any item hitting 8+ immediately — do not wait for daily brief*
```

## Step 4: Scan Previous Briefs (if any)

Before finalizing, scan the `news/` directory for any existing brief files. If previous briefs exist:
- Read the most recent one to identify previously tracked items
- Carry forward watchlist items that are still scoring 5+ and within 14 days
- Calculate score changes (movers) relative to the previous brief
- Note items that should be archived (below 5 for 14+ days)

If no previous briefs exist, treat all items as NEW entries.

## Important Guidelines

- **Bias toward signal over noise.** Don't report minor version bumps unless they unlock new capability.
- **Always frame impact through Ammar's lens:** healthcare CTO, automation builder, AI-assisted dev, educator.
- **Be honest about hype vs. substance.** Miss a trend for a day rather than chase vaporware.
- **Primary sources first.** Prefer official blogs, changelogs, GitHub repos, and documentation over news aggregator summaries.
- **Top 10 Links must be clickable.** Every URL in the links section must be a real, valid URL discovered during research. Never fabricate URLs.
- **Disruption scores must be justified.** Cite specific evidence (benchmarks, GitHub activity, enterprise announcements) for every score.
- **Healthcare relevance is mandatory.** Every item must have a clear "Impact on You" that connects to healthcare tech, voice AI, RPM, AI-assisted dev, or teaching.
- **Use markdown tables consistently.** All tabular data must use proper markdown table formatting.
- **Include source links.** Every detailed analysis section must include markdown hyperlinks to sources.
- **Perform at least 12 web searches.** Cover all 7 sub-categories in Step 1. Run searches in parallel batches for efficiency.
- **Track items for 14 days** on the watchlist, then archive unless still scoring 5+.
