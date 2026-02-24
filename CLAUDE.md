# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Install dependencies
pip3 install -r requirements.txt

# Set up API key (copy .env.example to .env and add your key)
cp .env.example .env

# Run the app
streamlit run app.py
```

There are no tests or linting configured yet.

## Architecture

Aikapsule is a five-phase conversational idea validation and launch tool built with Streamlit + Claude API.

**Data flow:** User input in `app.py` -> phase-specific agent in `agents.py` -> Claude API with tool_use -> tools executed in `tools.py` -> response + optional report returned to `app.py`.

### Three-file structure

- **`app.py`** — Streamlit UI. Manages five separate conversation histories (`api_messages_p1` through `api_messages_p5`) in session state. Renders chat, sidebar with phase navigation and progress tracking, inline report display, and download buttons for all five phase reports. Phase transition is manual (user clicks "Move to Phase N").

- **`agents.py`** — Claude API orchestration. `run_conversation()` is the core loop: sends messages to Claude, handles tool_use responses in a loop (max 5 rounds), dispatches tool calls via `handle_tool_call()`, and captures generated reports. Phase 1 (`run_phase1`) and Phase 2 (`run_phase2`) use original patterns. Phases 3-5 (`run_phase3`, `run_phase4`, `run_phase5`) use the shared `_inject_prior_reports()` helper to inject all prior phase reports as context on first message.

- **`tools.py`** — Tool definitions and implementations. Contains the `TOOLS` list (Claude API tool_use schema) and `handle_tool_call()` dispatcher. Two tools: `web_search` (DuckDuckGo HTML scraping via urllib) and `generate_report` (markdown formatter). Web search uses the `html.duckduckgo.com` endpoint directly — no third-party search library needed.

- **`complete_aikapsule_prompts.py`** — Reference/archive file containing all five phase system prompts. Not imported by the running application; the canonical prompts live in `agents.py` as `PHASE1_SYSTEM` through `PHASE5_SYSTEM`.

### Key patterns

- **Claude tool_use loop**: Claude decides when to search for competitors and when to generate reports. The `run_conversation` loop continues calling Claude until `stop_reason` is not `tool_use`.
- **Per-phase message histories**: `api_messages_p1` through `p5` hold the raw Claude API message format (including tool_use/tool_result blocks). `messages` holds the simplified display-only format for the chat UI.
- **Report detection**: When Claude calls `generate_report`, the returned markdown is captured separately and stored in `session_state.phase{N}_report` for sidebar download buttons.
- **Cumulative context**: Each phase injects all prior phase reports as context, so Phase 5 has the full picture from Phases 1-4.
- **Model**: Currently set to `claude-sonnet-4-6` in `agents.py:MODEL`.
- **Python 3.9 compat**: Uses `from __future__ import annotations` in agents.py for `X | None` syntax.

### System prompt methodology

All five phase prompts use a consistent framework stack: **The Mom Test + Jobs-to-be-Done + Lean Startup**. The tone is skeptical/constructive rather than encouraging — prompts are designed to challenge founder assumptions and force evidence-based thinking.

- **Phase 1 (Define)**: Uncovers the job-to-be-done, demands specific customers (not personas), explores switching dynamics (push/pull/anxiety/habit), uses web_search for competitive reality check.
- **Phase 2 (Validate)**: Designs experiments using a validation quality hierarchy (Tier 1: pre-orders/LOIs, Tier 2: waitlists/interviews, Tier 3: surveys/opinions). Pushes Build-Measure-Learn loops and minimum viable tests (landing page, concierge, Wizard of Oz, smoke test).
- **Phase 3 (MVP)**: Applies a 4-question decision framework per feature (tests assumption? → can test without building? → can do manually? → can use no-code?). Uses Kano Model for scope discipline.
- **Phase 4 (PMF)**: Uses Sean Ellis test (40% "very disappointed" threshold), green/yellow/red PMF assessment framework, and Mom Test lens for interpreting feedback. Includes pivot-type taxonomy.
- **Phase 5 (Growth)**: Gates on PMF readiness. Covers 3 engines of growth (sticky/viral/paid), 19 traction channels, unit economics modeling (CAC/LTV/payback), and funding strategy decision tree.

When editing prompts, update both `agents.py` (canonical) and `complete_aikapsule_prompts.py` (reference) to keep them in sync.
