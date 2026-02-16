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

### Key patterns

- **Claude tool_use loop**: Claude decides when to search for competitors and when to generate reports. The `run_conversation` loop continues calling Claude until `stop_reason` is not `tool_use`.
- **Per-phase message histories**: `api_messages_p1` through `p5` hold the raw Claude API message format (including tool_use/tool_result blocks). `messages` holds the simplified display-only format for the chat UI.
- **Report detection**: When Claude calls `generate_report`, the returned markdown is captured separately and stored in `session_state.phase{N}_report` for sidebar download buttons.
- **Cumulative context**: Each phase injects all prior phase reports as context, so Phase 5 has the full picture from Phases 1-4.
- **Model**: Currently set to `claude-sonnet-4-5-20250929` in `agents.py:MODEL`.
- **Python 3.9 compat**: Uses `from __future__ import annotations` in agents.py for `X | None` syntax.
