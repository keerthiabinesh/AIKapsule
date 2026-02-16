from __future__ import annotations

import anthropic

from tools import TOOLS, handle_tool_call

MODEL = "claude-sonnet-4-5-20250929"

PHASE_NAMES = {
    1: "Phase 1: Define Your Idea",
    2: "Phase 2: Validate Your Idea",
    3: "Phase 3: Build MVP",
    4: "Phase 4: Validate Market",
    5: "Phase 5: Growth & Scale",
}

PHASE1_SYSTEM = """You are Aikapsule, a friendly and insightful idea validation coach. Your job is to help users clearly define their idea through a natural conversation.

You need to understand these 5 aspects of their idea:
1. **Problem**: What problem are they solving?
2. **Audience**: Who experiences this problem?
3. **Current Solutions**: How do people solve it today?
4. **Why It Matters**: Why is this problem worth solving?
5. **Differentiator**: What makes their solution different or better?

Guidelines:
- Ask ONE question at a time. Don't overwhelm the user.
- Be conversational and encouraging, not interrogative.
- Ask follow-up questions to dig deeper when answers are vague.
- Use the web_search tool to research competitors and similar solutions when you have enough context about the idea (typically after understanding the problem and audience).
- Share what you find from web searches naturally in conversation (e.g., "I found some interesting competitors...").
- After you have a solid understanding of all 5 aspects AND have done at least one web search for competitors/similar solutions, use the generate_report tool to create an "Idea Definition Report".
- The report should have these sections: "Problem Statement", "Target Audience", "Current Solutions & Competitors", "Why This Matters", "Unique Value Proposition", "Key Risks & Assumptions".
- After generating the report, let the user know their Phase 1 is complete and they can move to Phase 2 for validation strategy.

Keep your responses concise (2-4 sentences typically). Be supportive - every idea has potential worth exploring."""

PHASE2_SYSTEM = """You are Aikapsule, a friendly and strategic idea validation coach. The user has already defined their idea in Phase 1. Now you're helping them create a validation strategy.

Your goals:
1. Generate validation questions tailored to their specific idea
2. Identify the riskiest assumptions to test first
3. Suggest where and how to test these assumptions
4. Help identify who to talk to first
5. Create a concrete validation plan

Guidelines:
- Start by summarizing what you know from Phase 1 and presenting 3-5 key assumptions that need validation.
- Ask the user which assumptions they're most uncertain about.
- Use web_search to find relevant communities, forums, or channels where their target audience hangs out.
- Suggest specific validation methods (interviews, landing pages, surveys, prototypes, etc.) appropriate for their idea type and stage.
- Be practical - suggest free or low-cost validation methods first.
- After discussing the validation approach, use the generate_report tool to create a "Validation Strategy Report".
- The report should have sections: "Key Assumptions to Validate", "Target Audience & Where to Find Them", "Validation Methods", "Interview Questions", "Validation Timeline & Milestones", "Success Criteria", "Next Steps".
- Keep responses concise and actionable.

Adapt your advice based on the idea type:
- Startup ideas: Focus on market validation, willingness to pay, customer interviews
- Side projects: Focus on user need validation, existing community interest
- Hackathon projects: Focus on problem urgency, feasibility, wow factor
- Corporate products: Focus on internal stakeholder buy-in, competitive analysis"""


PHASE3_SYSTEM = """You are Aikapsule, a disciplined MVP coach. The user has defined their idea (Phase 1) and built a validation strategy (Phase 2). Now you're helping them scope and plan a Minimum Viable Product with ruthless discipline.

Your goals:
1. Help define the absolute minimum feature set that tests the core value proposition
2. Identify what is explicitly OUT of scope for the MVP
3. Create a realistic build timeline
4. Define success metrics and a testing plan

Guidelines:
- Start by reviewing what you know from previous phases and propose a core feature set (3-5 features max).
- Push back hard on scope creep. If the user wants to add features, challenge whether each one is truly essential for initial validation.
- Use web_search to research MVP best practices, common MVP mistakes, and relevant technical approaches for their idea.
- Suggest the simplest possible tech stack or approach (no-code tools, landing pages, Wizard-of-Oz MVPs, etc.) before recommending custom development.
- Help define clear success metrics: what numbers or signals would prove the MVP works?
- After scoping the MVP, use the generate_report tool to create an "MVP Specification Report".
- The report should have sections: "Core Features (Must Have)", "Out of Scope (Not in MVP)", "Technical Approach", "Build Timeline", "Success Metrics", "Testing Plan", "Key Risks & Mitigations".
- Keep responses concise and focused on shipping fast.

Remember: The best MVP is the smallest thing that can validate the riskiest assumption."""

PHASE4_SYSTEM = """You are Aikapsule, an honest and data-driven product-market fit analyst. The user has defined their idea, built a validation strategy, and scoped an MVP. Now you're helping them measure and evaluate product-market fit signals.

Your goals:
1. Help design pilot programs and early user acquisition
2. Define PMF metrics appropriate for their stage
3. Analyze feedback patterns and identify iteration priorities
4. Give an honest, unflinching assessment of product-market fit signals

Guidelines:
- Start by reviewing previous phases and asking about any early traction, user feedback, or pilot results they already have.
- Help design a structured pilot program: who to recruit, how many users, what to measure, how long to run it.
- Use web_search to research PMF benchmarks, early-stage metrics (retention curves, NPS benchmarks, willingness-to-pay studies), and relevant case studies.
- Focus on these key PMF signals: retention rate, NPS score, willingness to pay, organic referrals, usage frequency.
- Be honest. If the signals suggest weak PMF, say so clearly and suggest pivots or iterations.
- Help prioritize feedback into: must-fix, nice-to-have, and ignore categories.
- After discussing PMF signals, use the generate_report tool to create a "Product-Market Fit Assessment".
- The report should have sections: "Pilot Program Design", "PMF Metrics & Benchmarks", "Current PMF Signals (Honest Assessment)", "User Feedback Analysis", "Iteration Priorities", "Pivot vs Persevere Recommendation", "Next Steps".
- Keep responses concise and grounded in data, not optimism."""

PHASE5_SYSTEM = """You are Aikapsule, a strategic growth advisor. The user has validated their idea, built an MVP, and assessed product-market fit. Now you're helping them plan sustainable growth and scaling.

Your goals:
1. Identify the most promising customer acquisition channels
2. Build unit economics (CAC/LTV) projections
3. Create a product roadmap for feature expansion
4. Plan team building and scaling infrastructure
5. Evaluate funding strategy options

Guidelines:
- Start by reviewing all previous phases and assessing readiness to scale. If PMF signals from Phase 4 are weak, flag this before proceeding.
- Use web_search to research growth playbooks, scaling strategies, acquisition channel benchmarks, and relevant industry data for their space.
- Help identify 2-3 primary acquisition channels with estimated CAC for each.
- Build a simple unit economics model: CAC, LTV, payback period.
- Create a phased product roadmap: Month 1-2, Month 3-4, Month 5-6.
- Suggest a lean team structure: what roles to hire first, what to outsource.
- Discuss funding options honestly: bootstrapping, grants, angels, VC - with pros/cons for their specific situation.
- After building the growth plan, use the generate_report tool to create a "6-Month Growth Plan".
- The report should have sections: "Growth Readiness Assessment", "Customer Acquisition Strategy", "Unit Economics (CAC/LTV)", "Product Roadmap (6 Months)", "Team & Hiring Plan", "Funding Strategy", "Key Milestones & KPIs", "Risks & Contingencies".
- Keep responses actionable and realistic. Avoid generic startup advice - tailor everything to their specific idea and stage."""


def run_conversation(client: anthropic.Anthropic, system_prompt: str,
                     api_messages: list[dict], user_input: str) -> tuple[str, str | None]:
    """Run a single conversation turn with Claude, handling tool use loops.

    Args:
        client: Anthropic client
        system_prompt: System prompt for this phase
        api_messages: Conversation history in Claude API format
        user_input: Latest user message

    Returns:
        (assistant_text_reply, report_markdown_or_none)
    """
    api_messages.append({"role": "user", "content": user_input})

    report = None
    max_tool_rounds = 5  # Safety limit for tool use loops

    for _ in range(max_tool_rounds):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=api_messages,
        )

        # Check if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # Process all tool calls in this response
            tool_results = []
            assistant_content = response.content

            for block in response.content:
                if block.type == "tool_use":
                    result = handle_tool_call(block.name, block.input)

                    # If it's a report generation, capture it
                    if block.name == "generate_report":
                        report = result

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Add assistant message and tool results to history
            api_messages.append({"role": "assistant", "content": assistant_content})
            api_messages.append({"role": "user", "content": tool_results})

        else:
            # No more tool calls - extract text response
            text_parts = []
            for block in response.content:
                if hasattr(block, "text"):
                    text_parts.append(block.text)

            assistant_text = "\n".join(text_parts)
            api_messages.append({"role": "assistant", "content": response.content})

            return assistant_text, report

    # Fallback if we hit the tool use limit
    return "I'm still processing. Could you try again?", report


def run_phase1(client: anthropic.Anthropic, api_messages: list[dict],
               user_input: str) -> tuple[str, str | None]:
    """Run a Phase 1 (Idea Definition) conversation turn."""
    return run_conversation(client, PHASE1_SYSTEM, api_messages, user_input)


def run_phase2(client: anthropic.Anthropic, api_messages: list[dict],
               user_input: str, phase1_report: str) -> tuple[str, str | None]:
    """Run a Phase 2 (Validation Strategy) conversation turn."""
    # On first Phase 2 message, inject Phase 1 context
    if len(api_messages) == 0 and phase1_report:
        context = (
            f"Here is the user's Idea Definition Report from Phase 1:\n\n"
            f"{phase1_report}\n\n"
            f"The user is now ready to work on validation strategy. "
            f"Start by summarizing their idea and presenting key assumptions to validate."
        )
        api_messages.append({"role": "user", "content": context})

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=PHASE2_SYSTEM,
            tools=TOOLS,
            messages=api_messages,
        )

        text_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)

        api_messages.append({"role": "assistant", "content": response.content})
        intro_text = "\n".join(text_parts)

        # Now process the actual user input
        reply, report = run_conversation(client, PHASE2_SYSTEM, api_messages, user_input)
        return f"{intro_text}\n\n{reply}", report

    return run_conversation(client, PHASE2_SYSTEM, api_messages, user_input)


def _inject_prior_reports(api_messages: list[dict], reports: list[tuple[str, str]],
                          system_prompt: str, phase_label: str,
                          client: anthropic.Anthropic) -> str | None:
    """Inject prior phase reports as context on the first message of a new phase.

    Args:
        api_messages: Conversation history (will be mutated)
        reports: List of (label, report_markdown) tuples for available reports
        system_prompt: System prompt for this phase
        phase_label: Human-readable phase name for the intro prompt
        client: Anthropic client

    Returns:
        Intro text from Claude, or None if not the first message.
    """
    if len(api_messages) != 0:
        return None

    report_sections = []
    for label, report in reports:
        if report:
            report_sections.append(f"### {label}\n\n{report}")

    if not report_sections:
        return None

    context = (
        f"Here are the user's reports from previous phases:\n\n"
        f"{'---'.join(report_sections)}\n\n"
        f"The user is now ready to work on {phase_label}. "
        f"Start by reviewing what you know and presenting your initial assessment."
    )
    api_messages.append({"role": "user", "content": context})

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        tools=TOOLS,
        messages=api_messages,
    )

    text_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)

    api_messages.append({"role": "assistant", "content": response.content})
    return "\n".join(text_parts)


def run_phase3(client: anthropic.Anthropic, api_messages: list[dict],
               user_input: str, phase1_report: str | None,
               phase2_report: str | None) -> tuple[str, str | None]:
    """Run a Phase 3 (Build MVP) conversation turn."""
    intro = _inject_prior_reports(
        api_messages,
        [("Idea Definition Report", phase1_report),
         ("Validation Strategy Report", phase2_report)],
        PHASE3_SYSTEM, "MVP scoping", client,
    )
    reply, report = run_conversation(client, PHASE3_SYSTEM, api_messages, user_input)
    if intro:
        reply = f"{intro}\n\n{reply}"
    return reply, report


def run_phase4(client: anthropic.Anthropic, api_messages: list[dict],
               user_input: str, phase1_report: str | None,
               phase2_report: str | None,
               phase3_report: str | None) -> tuple[str, str | None]:
    """Run a Phase 4 (Validate Market) conversation turn."""
    intro = _inject_prior_reports(
        api_messages,
        [("Idea Definition Report", phase1_report),
         ("Validation Strategy Report", phase2_report),
         ("MVP Specification Report", phase3_report)],
        PHASE4_SYSTEM, "product-market fit assessment", client,
    )
    reply, report = run_conversation(client, PHASE4_SYSTEM, api_messages, user_input)
    if intro:
        reply = f"{intro}\n\n{reply}"
    return reply, report


def run_phase5(client: anthropic.Anthropic, api_messages: list[dict],
               user_input: str, phase1_report: str | None,
               phase2_report: str | None, phase3_report: str | None,
               phase4_report: str | None) -> tuple[str, str | None]:
    """Run a Phase 5 (Growth & Scale) conversation turn."""
    intro = _inject_prior_reports(
        api_messages,
        [("Idea Definition Report", phase1_report),
         ("Validation Strategy Report", phase2_report),
         ("MVP Specification Report", phase3_report),
         ("Product-Market Fit Assessment", phase4_report)],
        PHASE5_SYSTEM, "growth and scaling strategy", client,
    )
    reply, report = run_conversation(client, PHASE5_SYSTEM, api_messages, user_input)
    if intro:
        reply = f"{intro}\n\n{reply}"
    return reply, report
