import os

import anthropic
import streamlit as st
from dotenv import load_dotenv

from agents import run_phase1, run_phase2, run_phase3, run_phase4, run_phase5, PHASE_NAMES

load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="Aikapsule",
    page_icon="💊",
    layout="centered",
)

# --- Custom CSS ---
st.markdown("""
<style>
    .stApp {
        max-width: 900px;
        margin: 0 auto;
    }
    .report-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    [data-testid="stSidebar"] {
        min-width: 260px;
        max-width: 300px;
    }
</style>
""", unsafe_allow_html=True)


# --- Session State Init ---
def init_state():
    defaults = {
        "phase": 1,
        "messages": [],          # Display messages: [{role, content}]
        "api_messages_p1": [],   # Claude API history for Phase 1
        "api_messages_p2": [],   # Claude API history for Phase 2
        "api_messages_p3": [],   # Claude API history for Phase 3
        "api_messages_p4": [],   # Claude API history for Phase 4
        "api_messages_p5": [],   # Claude API history for Phase 5
        "phase1_report": None,
        "phase2_report": None,
        "phase3_report": None,
        "phase4_report": None,
        "phase5_report": None,
        "welcomed": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_state()


# --- API Client ---
@st.cache_resource
def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("Please set your ANTHROPIC_API_KEY in a .env file. See .env.example for reference.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


client = get_client()


# --- Sidebar ---
with st.sidebar:
    st.markdown("## 💊 Aikapsule")
    st.caption("Validate any idea in minutes")
    st.divider()

    # Phase indicator
    st.markdown("### Progress")
    phase_labels = {
        1: "Define Your Idea",
        2: "Validate Your Idea",
        3: "Build MVP",
        4: "Validate Market",
        5: "Growth & Scale",
    }
    phase_reports = {
        1: st.session_state.phase1_report,
        2: st.session_state.phase2_report,
        3: st.session_state.phase3_report,
        4: st.session_state.phase4_report,
        5: st.session_state.phase5_report,
    }

    for p in range(1, 6):
        if phase_reports[p]:
            icon = "✅"
        elif st.session_state.phase == p:
            icon = "🔄"
        else:
            icon = "⏳"
        st.markdown(f"{icon} **Phase {p}:** {phase_labels[p]}")

    st.divider()

    # Phase navigation — show "Move to Phase N+1" when current phase has a report
    current = st.session_state.phase
    phase_transitions = {
        1: ("Phase 2: Validation Strategy", "I'll help you figure out how to test your idea's key assumptions. Let's get started - what aspect of your idea are you most uncertain about?"),
        2: ("Phase 3: Build MVP", "I'll help you scope the smallest possible product that validates your core value proposition. What do you think is the single most important feature?"),
        3: ("Phase 4: Validate Market", "I'll help you measure product-market fit signals and assess whether you're on the right track. Have you had any early users or feedback yet?"),
        4: ("Phase 5: Growth & Scale", "I'll help you build a growth strategy and scaling plan. Let's start by reviewing your readiness to scale."),
    }
    if current in phase_transitions and phase_reports[current]:
        next_phase = current + 1
        label, intro_msg = phase_transitions[current]
        if st.button(f"➡️ Move to {label}", use_container_width=True, type="primary"):
            st.session_state.phase = next_phase
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Great! Let's move to **{label}**. {intro_msg}",
            })
            st.rerun()
    elif current > 1:
        st.info(f"📋 {PHASE_NAMES[current]}")

    # Report downloads
    st.divider()
    st.markdown("### Reports")

    report_buttons = [
        ("phase1_report", "📥 Idea Definition Report", "aikapsule_idea_definition.md"),
        ("phase2_report", "📥 Validation Strategy Report", "aikapsule_validation_strategy.md"),
        ("phase3_report", "📥 MVP Specification Report", "aikapsule_mvp_specification.md"),
        ("phase4_report", "📥 PMF Assessment Report", "aikapsule_pmf_assessment.md"),
        ("phase5_report", "📥 6-Month Growth Plan", "aikapsule_growth_plan.md"),
    ]
    has_any_report = False
    for key, label, filename in report_buttons:
        if st.session_state[key]:
            has_any_report = True
            st.download_button(
                label,
                data=st.session_state[key],
                file_name=filename,
                mime="text/markdown",
                use_container_width=True,
            )

    if not has_any_report:
        st.caption("Reports will appear here as they're generated.")

    # Reset button
    st.divider()
    if st.button("🔄 Start Over", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# --- Welcome Message ---
if not st.session_state.welcomed:
    welcome = (
        "Welcome to **Aikapsule**! I help you validate and launch any idea - whether it's a "
        "startup, side project, hackathon concept, or product feature.\n\n"
        "We'll work through five phases:\n"
        "1. **Define Your Idea** - Clarify your concept\n"
        "2. **Validate Your Idea** - Test your assumptions\n"
        "3. **Build MVP** - Scope the smallest viable product\n"
        "4. **Validate Market** - Measure product-market fit\n"
        "5. **Growth & Scale** - Plan acquisition and scaling\n\n"
        "Let's start! **What problem are you trying to solve?**"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    st.session_state.welcomed = True


# --- Chat Display ---
st.markdown("#### 💊 Aikapsule")
st.caption(PHASE_NAMES[st.session_state.phase])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Show report inline if this message contains one
        if msg.get("report"):
            with st.expander("📄 View Generated Report", expanded=True):
                st.markdown(msg["report"])


# --- Chat Input ---
if user_input := st.chat_input("Type your response..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            phase = st.session_state.phase
            if phase == 1:
                reply, report = run_phase1(
                    client,
                    st.session_state.api_messages_p1,
                    user_input,
                )
                if report:
                    st.session_state.phase1_report = report
            elif phase == 2:
                reply, report = run_phase2(
                    client,
                    st.session_state.api_messages_p2,
                    user_input,
                    st.session_state.phase1_report,
                )
                if report:
                    st.session_state.phase2_report = report
            elif phase == 3:
                reply, report = run_phase3(
                    client,
                    st.session_state.api_messages_p3,
                    user_input,
                    st.session_state.phase1_report,
                    st.session_state.phase2_report,
                )
                if report:
                    st.session_state.phase3_report = report
            elif phase == 4:
                reply, report = run_phase4(
                    client,
                    st.session_state.api_messages_p4,
                    user_input,
                    st.session_state.phase1_report,
                    st.session_state.phase2_report,
                    st.session_state.phase3_report,
                )
                if report:
                    st.session_state.phase4_report = report
            else:  # phase 5
                reply, report = run_phase5(
                    client,
                    st.session_state.api_messages_p5,
                    user_input,
                    st.session_state.phase1_report,
                    st.session_state.phase2_report,
                    st.session_state.phase3_report,
                    st.session_state.phase4_report,
                )
                if report:
                    st.session_state.phase5_report = report

        st.markdown(reply)

        # Show report inline
        if report:
            with st.expander("📄 View Generated Report", expanded=True):
                st.markdown(report)

    # Save to message history
    msg_entry = {"role": "assistant", "content": reply}
    if report:
        msg_entry["report"] = report
    st.session_state.messages.append(msg_entry)

    st.rerun()
