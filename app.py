import os

import anthropic
import streamlit as st
from dotenv import load_dotenv

from agents import run_phase1, run_phase2, run_phase3, run_phase4, run_phase5, PHASE_NAMES

load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="Aikapsule",
    page_icon="⬡",
    layout="wide",
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

    * { box-sizing: border-box; }

    .stApp {
        background-color: #0a0a0a;
        font-family: 'DM Sans', sans-serif;
    }

    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    [data-testid="stSidebar"] {
        background-color: #0f0f0f !important;
        border-right: 1px solid #1e1e1e !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }

    [data-testid="stSidebar"] > div {
        padding: 2rem 1.5rem !important;
    }

    [data-testid="stSidebar"] .stMarkdown p {
        color: #666 !important;
        font-size: 0.75rem !important;
        font-family: 'DM Mono', monospace !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: #1a1a1a !important;
        margin: 1rem 0 !important;
    }

    .phase-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 7px 0;
        border-bottom: 1px solid #131313;
    }

    .pdot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
    .pdot-done { background: #22c55e; }
    .pdot-active { background: #f59e0b; box-shadow: 0 0 5px rgba(245,158,11,0.5); }
    .pdot-pending { background: #1e1e1e; border: 1px solid #2a2a2a; }

    .plabel { font-family: 'DM Mono', monospace; font-size: 0.72rem; }
    .plabel-done { color: #22c55e; }
    .plabel-active { color: #f0f0f0; }
    .plabel-pending { color: #3a3a3a; }

    .stButton > button {
        background: transparent !important;
        border: 1px solid #222 !important;
        color: #666 !important;
        border-radius: 5px !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.72rem !important;
        padding: 7px 12px !important;
        width: 100% !important;
        text-align: left !important;
        transition: all 0.12s !important;
    }

    .stButton > button:hover {
        border-color: #333 !important;
        color: #ccc !important;
        background: #111 !important;
    }

    .stButton > button[kind="primary"] {
        background: #f59e0b !important;
        border-color: #f59e0b !important;
        color: #0a0a0a !important;
        font-weight: 600 !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #d97706 !important;
        border-color: #d97706 !important;
    }

    .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid #1a1a1a !important;
        color: #555 !important;
        border-radius: 5px !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.68rem !important;
        padding: 6px 10px !important;
        width: 100% !important;
        transition: all 0.12s !important;
    }

    .stDownloadButton > button:hover {
        border-color: #22c55e !important;
        color: #22c55e !important;
        background: rgba(34,197,94,0.04) !important;
    }

    .stMarkdown p {
        color: #bbb !important;
        font-size: 0.88rem !important;
        line-height: 1.75 !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #e8e8e8 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        letter-spacing: -0.01em !important;
    }

    .stMarkdown h2 { font-size: 1rem !important; }
    .stMarkdown h3 { font-size: 0.9rem !important; }

    .stMarkdown code {
        font-family: 'DM Mono', monospace !important;
        background: #161616 !important;
        color: #f59e0b !important;
        padding: 1px 5px !important;
        border-radius: 3px !important;
        font-size: 0.8rem !important;
    }

    .stMarkdown ul li, .stMarkdown ol li {
        color: #aaa !important;
        font-size: 0.86rem !important;
        margin-bottom: 3px !important;
    }

    .stMarkdown strong { color: #e8e8e8 !important; font-weight: 600 !important; }

    [data-testid="stChatInput"] {
        background: #0d0d0d !important;
        border-top: 1px solid #1a1a1a !important;
    }

    [data-testid="stChatInput"] textarea {
        background: #141414 !important;
        border: 1px solid #222 !important;
        border-radius: 7px !important;
        color: #e0e0e0 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.875rem !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: #f59e0b !important;
        box-shadow: 0 0 0 2px rgba(245,158,11,0.06) !important;
    }

    [data-testid="stChatInput"] textarea::placeholder { color: #333 !important; }

    [data-testid="stChatInput"] button {
        background: #f59e0b !important;
        border: none !important;
        border-radius: 6px !important;
    }

    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 0.5rem 0 !important;
    }

    .stSpinner > div { border-top-color: #f59e0b !important; }

    details summary {
        background: #111 !important;
        border: 1px solid #1e1e1e !important;
        border-radius: 5px !important;
        color: #555 !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.72rem !important;
        padding: 8px 12px !important;
        cursor: pointer !important;
    }

    details[open] summary {
        border-radius: 5px 5px 0 0 !important;
        color: #888 !important;
    }

    details .stMarkdown {
        background: #0d0d0d !important;
        border: 1px solid #1a1a1a !important;
        border-top: none !important;
        border-radius: 0 0 5px 5px !important;
        padding: 1.5rem !important;
    }

    .stCaption p { color: #333 !important; font-family: 'DM Mono', monospace !important; font-size: 0.68rem !important; }

    ::-webkit-scrollbar { width: 3px; height: 3px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #1e1e1e; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# --- Session State Init ---
def init_state():
    defaults = {
        "phase": 1,
        "messages": [],
        "api_messages_p1": [],
        "api_messages_p2": [],
        "api_messages_p3": [],
        "api_messages_p4": [],
        "api_messages_p5": [],
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


@st.cache_resource
def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("ANTHROPIC_API_KEY not set. Add it to your .env file.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


client = get_client()

phase_reports = {
    1: st.session_state.phase1_report,
    2: st.session_state.phase2_report,
    3: st.session_state.phase3_report,
    4: st.session_state.phase4_report,
    5: st.session_state.phase5_report,
}
current = st.session_state.phase

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:2.5rem">
      <span style="font-family:'DM Sans',sans-serif;font-size:1.1rem;font-weight:600;color:#f0f0f0;letter-spacing:-0.02em">⬡ Aikapsule</span><br>
      <span style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#333;text-transform:uppercase;letter-spacing:0.12em">Idea Validation</span>
    </div>
    """, unsafe_allow_html=True)

    phase_labels = {1: "Define", 2: "Validate", 3: "Build MVP", 4: "Market Fit", 5: "Scale"}

    for p in range(1, 6):
        if phase_reports[p]:
            dot, lbl = "pdot-done", "plabel-done"
            text = f"✓ {phase_labels[p]}"
        elif current == p:
            dot, lbl = "pdot-active", "plabel-active"
            text = f"→ {phase_labels[p]}"
        else:
            dot, lbl = "pdot-pending", "plabel-pending"
            text = f"  {phase_labels[p]}"

        st.markdown(f"""
        <div class="phase-row">
          <div class="pdot {dot}"></div>
          <div class="plabel {lbl}">{text}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    phase_transitions = {
        1: ("Phase 2: Validate", "Okay — let's figure out what you need to prove. What's the part of this idea you're most uncertain about?"),
        2: ("Phase 3: Build MVP", "Good. Now let's scope the smallest thing that tests your core assumption. What's the one job it must do?"),
        3: ("Phase 4: Market Fit", "Time for a real pilot. Do you have early users you can put this in front of?"),
        4: ("Phase 5: Scale", "Let's talk growth. First, I want to check your PMF signals before we go further."),
    }

    if current in phase_transitions and phase_reports[current]:
        next_phase = current + 1
        label, intro_msg = phase_transitions[current]
        if st.button(f"→ {label}", type="primary"):
            st.session_state.phase = next_phase
            st.session_state.messages.append({"role": "assistant", "content": intro_msg})
            st.rerun()

    if any(phase_reports.values()):
        st.markdown("""
        <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:#2a2a2a;
                    text-transform:uppercase;letter-spacing:0.1em;margin:1.25rem 0 0.6rem">
        Reports
        </div>""", unsafe_allow_html=True)

        report_config = [
            ("phase1_report", "↓ Idea Definition", "aikapsule_idea_definition.md"),
            ("phase2_report", "↓ Validation Strategy", "aikapsule_validation_strategy.md"),
            ("phase3_report", "↓ MVP Specification", "aikapsule_mvp_specification.md"),
            ("phase4_report", "↓ PMF Assessment", "aikapsule_pmf_assessment.md"),
            ("phase5_report", "↓ Growth Plan", "aikapsule_growth_plan.md"),
        ]
        for key, label, filename in report_config:
            if st.session_state[key]:
                st.download_button(label, data=st.session_state[key],
                                   file_name=filename, mime="text/markdown",
                                   use_container_width=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    if st.button("↺ Reset"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# --- Welcome ---
if not st.session_state.welcomed:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hey. I'm Aikapsule.\n\n"
            "Most ideas fail because founders fall in love with their solution before they understand the problem. "
            "I'm here to fix that.\n\n"
            "I'll ask hard questions, search for real market signals, and push back on weak assumptions. "
            "I won't tell you your idea is great — I'll help you figure out if it actually is.\n\n"
            "**What are you trying to build — and what problem does it solve?**"
        )
    })
    st.session_state.welcomed = True


# --- Phase label header ---
phase_header = {
    1: "01 — Define",
    2: "02 — Validate",
    3: "03 — Build MVP",
    4: "04 — Market Fit",
    5: "05 — Scale",
}

st.markdown(f"""
<div style="max-width:740px;margin:0 auto;padding:2rem 1rem 0.25rem">
  <span style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#f59e0b;
               text-transform:uppercase;letter-spacing:0.12em">
    {phase_header[current]}
  </span>
  <div style="border-bottom:1px solid #181818;margin-top:0.5rem"></div>
</div>
""", unsafe_allow_html=True)

# --- Chat messages ---
for msg in st.session_state.messages:
    avatar = "⬡" if msg["role"] == "assistant" else "○"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg.get("report"):
            with st.expander("↓ View report", expanded=False):
                st.markdown(msg["report"])

# --- Input ---
if user_input := st.chat_input("Your response..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="○"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="⬡"):
        with st.spinner(""):
            phase = st.session_state.phase
            report = None

            if phase == 1:
                reply, report = run_phase1(client, st.session_state.api_messages_p1, user_input)
                if report: st.session_state.phase1_report = report
            elif phase == 2:
                reply, report = run_phase2(client, st.session_state.api_messages_p2, user_input, st.session_state.phase1_report)
                if report: st.session_state.phase2_report = report
            elif phase == 3:
                reply, report = run_phase3(client, st.session_state.api_messages_p3, user_input, st.session_state.phase1_report, st.session_state.phase2_report)
                if report: st.session_state.phase3_report = report
            elif phase == 4:
                reply, report = run_phase4(client, st.session_state.api_messages_p4, user_input, st.session_state.phase1_report, st.session_state.phase2_report, st.session_state.phase3_report)
                if report: st.session_state.phase4_report = report
            else:
                reply, report = run_phase5(client, st.session_state.api_messages_p5, user_input, st.session_state.phase1_report, st.session_state.phase2_report, st.session_state.phase3_report, st.session_state.phase4_report)
                if report: st.session_state.phase5_report = report

        st.markdown(reply)
        if report:
            with st.expander("↓ View report", expanded=True):
                st.markdown(report)

    entry = {"role": "assistant", "content": reply}
    if report:
        entry["report"] = report
    st.session_state.messages.append(entry)
    st.rerun()