import sys
import os
import pandas as pd
import streamlit as st
import time
import uuid

# --- 1. PAGE CONFIG ---
st.set_page_config(
    page_title="Yield.ai | AI Evaluation Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. NEURAL TERMINAL CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;600;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Global Reset ───────────────────────────────────────────── */
html, body, .stApp {
    background-color: #050508 !important;
    font-family: 'Syne', sans-serif !important;
}

/* Animated grid background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(245,166,35,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(245,166,35,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}

/* ── Typography ─────────────────────────────────────────────── */
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
    color: #E8EDF5 !important;
}
p, li, span, div {
    font-family: 'Syne', sans-serif;
}

/* ── Sidebar ────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #08080D !important;
    border-right: 1px solid rgba(245,166,35,0.15) !important;
}
section[data-testid="stSidebar"] * {
    color: #A0A8B8 !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMarkdown p {
    color: #A0A8B8 !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

/* ── Buttons ────────────────────────────────────────────────── */
.stButton>button {
    background: transparent !important;
    color: #F5A623 !important;
    border: 1px solid #F5A623 !important;
    border-radius: 0px !important;
    padding: 0.6rem 2rem !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}
.stButton>button:hover {
    background: #F5A623 !important;
    color: #050508 !important;
    box-shadow: 0 0 30px rgba(245,166,35,0.3) !important;
    transform: none !important;
}
.stButton>button[kind="primary"] {
    background: #F5A623 !important;
    color: #050508 !important;
    border: 1px solid #F5A623 !important;
    font-weight: 700 !important;
}
.stButton>button[kind="primary"]:hover {
    background: transparent !important;
    color: #F5A623 !important;
    box-shadow: 0 0 40px rgba(245,166,35,0.4) !important;
}

/* ── Inputs & Textareas ─────────────────────────────────────── */
.stTextArea textarea, .stTextInput input {
    background: #0D0D12 !important;
    border: 1px solid rgba(245,166,35,0.2) !important;
    border-radius: 0 !important;
    color: #E8EDF5 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #F5A623 !important;
    box-shadow: 0 0 0 1px #F5A623 !important;
}

/* ── File Uploader ──────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #0D0D12 !important;
    border: 1px dashed rgba(245,166,35,0.3) !important;
    border-radius: 0 !important;
}

/* ── Tabs ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(245,166,35,0.2) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #4A5568 !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 12px 24px !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    color: #F5A623 !important;
    border-bottom: 2px solid #F5A623 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #E8EDF5 !important;
}

/* ── Expanders ──────────────────────────────────────────────── */
div[data-testid="stExpander"] {
    background: #0D0D12 !important;
    border: 1px solid rgba(245,166,35,0.15) !important;
    border-radius: 0 !important;
}
div[data-testid="stExpander"] summary {
    color: #A0A8B8 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
}

/* ── Progress Bar ───────────────────────────────────────────── */
.stProgress > div > div {
    background: #F5A623 !important;
    border-radius: 0 !important;
}
.stProgress > div {
    background: rgba(245,166,35,0.1) !important;
    border-radius: 0 !important;
}

/* ── Selectbox ──────────────────────────────────────────────── */
.stSelectbox > div > div {
    background: #0D0D12 !important;
    border: 1px solid rgba(245,166,35,0.2) !important;
    border-radius: 0 !important;
    color: #E8EDF5 !important;
}

/* ── Dataframe ──────────────────────────────────────────────── */
.stDataFrame {
    border: 1px solid rgba(245,166,35,0.15) !important;
}

/* ── Info / Success / Warning boxes ────────────────────────── */
.stAlert {
    border-radius: 0 !important;
    border-left: 3px solid #F5A623 !important;
    background: rgba(245,166,35,0.05) !important;
}

/* ── Hero header ────────────────────────────────────────────── */
.yield-hero {
    padding: 48px 0 32px 0;
    border-bottom: 1px solid rgba(245,166,35,0.15);
    margin-bottom: 40px;
}
.yield-hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #F5A623;
    margin-bottom: 12px;
}
.yield-hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 52px;
    font-weight: 800;
    color: #E8EDF5;
    line-height: 1;
    margin-bottom: 12px;
    letter-spacing: -2px;
}
.yield-hero-title span {
    color: #F5A623;
}
.yield-hero-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    color: #4A5568;
    letter-spacing: 1px;
}

/* ── Section labels ─────────────────────────────────────────── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #F5A623;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(245,166,35,0.2);
}

/* ── Score display ──────────────────────────────────────────── */
.score-display {
    text-align: center;
    padding: 32px 0;
    border: 1px solid rgba(245,166,35,0.15);
    margin-bottom: 24px;
    background: #0D0D12;
    position: relative;
}
.score-display::before {
    content: 'YIELD SCORE';
    position: absolute;
    top: -8px;
    left: 50%;
    transform: translateX(-50%);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    color: #F5A623;
    background: #0D0D12;
    padding: 0 12px;
}
.score-number {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 72px;
    font-weight: 700;
    color: #F5A623;
    line-height: 1;
}
.score-unit {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 24px;
    color: rgba(245,166,35,0.5);
}

/* ── Metric cards ───────────────────────────────────────────── */
.metric-card {
    background: #0D0D12;
    border: 1px solid rgba(245,166,35,0.1);
    border-left: 3px solid #F5A623;
    padding: 20px;
    height: 100%;
    position: relative;
    transition: border-color 0.2s;
}
.metric-card:hover {
    border-color: rgba(245,166,35,0.3);
    border-left-color: #F5A623;
}
.metric-card.blue { border-left-color: #4A9EFF; }
.metric-card.green { border-left-color: #2ECC71; }
.metric-card-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #4A5568;
    margin-bottom: 12px;
}
.metric-card-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 42px;
    font-weight: 700;
    color: #E8EDF5;
    line-height: 1;
}
.metric-card-value.amber { color: #F5A623; }
.metric-card-value.blue  { color: #4A9EFF; }
.metric-card-value.green { color: #2ECC71; }
.metric-card-desc {
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    color: #4A5568;
    margin-top: 8px;
    line-height: 1.4;
}

/* ── Skill tags ─────────────────────────────────────────────── */
.matched-tag {
    background: rgba(46,204,113,0.05);
    color: #2ECC71;
    padding: 4px 10px;
    margin: 3px;
    display: inline-block;
    font-size: 11px;
    font-family: 'IBM Plex Mono', monospace;
    border: 1px solid rgba(46,204,113,0.3);
    border-radius: 0;
    letter-spacing: 0.5px;
    transition: all 0.15s;
}
.matched-tag:hover {
    background: rgba(46,204,113,0.15);
    border-color: #2ECC71;
}
.missing-tag {
    background: rgba(231,76,60,0.05);
    color: #E74C3C;
    padding: 4px 10px;
    margin: 3px;
    display: inline-block;
    font-size: 11px;
    font-family: 'IBM Plex Mono', monospace;
    border: 1px solid rgba(231,76,60,0.3);
    border-radius: 0;
    letter-spacing: 0.5px;
    transition: all 0.15s;
}
.missing-tag:hover {
    background: rgba(231,76,60,0.15);
    border-color: #E74C3C;
}

/* ── Leaderboard ────────────────────────────────────────────── */
.leaderboard-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 24px;
}
.leaderboard-table th {
    color: #F5A623;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(245,166,35,0.2);
    text-align: left;
    background: #0D0D12;
}
.leaderboard-table td {
    padding: 14px 16px;
    color: #A0A8B8;
    font-size: 13px;
    border-bottom: 1px solid rgba(255,255,255,0.03);
}
.leaderboard-table tr:hover td {
    background: rgba(245,166,35,0.03);
    color: #E8EDF5;
}
.rank-badge { font-weight: 700; font-size: 14px; }
.score-bar-wrap {
    background: rgba(255,255,255,0.05);
    border-radius: 0;
    height: 4px;
    width: 100%;
    min-width: 120px;
}
.score-bar-fill {
    height: 4px;
    border-radius: 0;
    background: linear-gradient(90deg, #F5A623, #FF6B35);
}

/* ── Candidate name heading ──────────────────────────────────── */
.candidate-heading {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #E8EDF5;
    letter-spacing: -0.5px;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(245,166,35,0.15);
}

/* ── Hide streamlit branding ─────────────────────────────────── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. PATH INJECTION & SESSION LOGIC ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

session_base = os.path.join("data", "sessions", st.session_state['session_id'])
raw_dir = os.path.join(session_base, "raw")
processed_dir = os.path.join(session_base, "processed")

os.makedirs(raw_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)

output_csv = os.path.join(processed_dir, "evaluation_report.csv")

# --- 4. BACKEND IMPORTS ---
from src.main import process_resumes_to_csv
from src.database import init_db, get_all_evaluations
from src.visualizer import create_radar_chart
from src.optimizer import generate_optimized_bullets

init_db()

# --- 5. HELPERS ---
def score_color(score):
    if score >= 75:
        return "#2ECC71"
    elif score >= 50:
        return "#F5A623"
    else:
        return "#E74C3C"

def score_class(score):
    if score >= 75:
        return "green"
    elif score >= 50:
        return "amber"
    else:
        return "red"

def rank_emoji(rank):
    medals = ["🥇", "🥈", "🥉"]
    return medals[rank - 1] if rank - 1 < len(medals) else f"#{rank}"

# --- 6. SCORECARD ---
def render_scorecard(candidate_name, row_data):
    row_dict = dict(row_data)
    overall = row_dict.get("Score", 0)
    skill_m = row_dict.get("Skill Match", 0)
    sem_m   = row_dict.get("Semantic Match", 0)
    exp_m   = row_dict.get("Experience Relevance", 0)
    model_u = row_dict.get("Model Used", "—")

    st.markdown(f'<div class="candidate-heading">{candidate_name}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="score-display"><div class="score-number">{overall}<span class="score-unit">%</span></div></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-card-label">Skill Match · 40%</div><div class="metric-card-value amber">{skill_m}%</div><div class="metric-card-desc">Direct keyword overlap with JD requirements.</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card blue"><div class="metric-card-label">Semantic Match · 35%</div><div class="metric-card-value blue">{sem_m}%</div><div class="metric-card-desc">Contextual project alignment via LLM.</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card green"><div class="metric-card-label">Experience · 25%</div><div class="metric-card-value green">{exp_m}%</div><div class="metric-card-desc">Career progression and tool seniority.</div></div>', unsafe_allow_html=True)

    st.write("")
    with st.expander("HOW IS THIS SCORE CALCULATED?"):
        st.markdown(f"""
**Weighted composite:** `({skill_m} × 0.40) + ({sem_m} × 0.35) + ({exp_m} × 0.25) = {overall}%`

- **Skill Match (40%)** — Direct overlap of technical keywords identified in the JD
- **Semantic Match (35%)** — Contextual relevance via Llama 3.1 RAG pipeline
- **Experience Relevance (25%)** — Career progression and tool seniority depth

*Model used: `{model_u}`*
        """)

    matched_skills = str(row_dict.get("Matched Skills", "")).split(", ")
    missing_skills = str(row_dict.get("Missing Skills", "")).split(", ")

    st.write("")
    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown('<div class="section-label">Matched Skills</div>', unsafe_allow_html=True)
        if matched_skills and matched_skills[0] not in ["nan", "", "None"]:
            st.markdown("".join([f'<span class="matched-tag">{s}</span>' for s in matched_skills]), unsafe_allow_html=True)
        else:
            st.caption("None identified.")
    with right_col:
        st.markdown('<div class="section-label">Missing Skills</div>', unsafe_allow_html=True)
        if missing_skills and missing_skills[0] not in ["nan", "", "None"]:
            st.markdown("".join([f'<span class="missing-tag">{s}</span>' for s in missing_skills]), unsafe_allow_html=True)
        else:
            st.caption("No gaps identified.")


# --- 7. LEADERBOARD ---
def render_leaderboard(df):
    st.markdown('<div class="section-label">Candidate Rankings</div>', unsafe_allow_html=True)
    ranked = df.sort_values(by="Score", ascending=False).reset_index(drop=True)

    rows = []
    for i, row in ranked.iterrows():
        rank     = i + 1
        score    = float(row.get("Score", 0))
        color    = score_color(score)
        bar_w    = min(int(score), 100)
        skill    = row.get("Skill Match", 0)
        semantic = row.get("Semantic Match", 0)
        exp      = row.get("Experience Relevance", 0)
        name     = row["Candidate Name"]
        model    = row.get("Model Used", "—")

        bar = f'<div style="display:flex;align-items:center;gap:12px;"><div class="score-bar-wrap"><div class="score-bar-fill" style="width:{bar_w}%;"></div></div><span style="color:{color};font-weight:700;min-width:44px;font-size:14px;">{score}%</span></div>'
        rows.append(
            f'<tr>'
            f'<td><span class="rank-badge" style="color:{color};">{rank_emoji(rank)}</span></td>'
            f'<td><span style="color:#E8EDF5;font-family:Syne,sans-serif;font-weight:700;">{name}</span><br><span style="font-size:10px;color:#2A2F3A;letter-spacing:1px;">{model}</span></td>'
            f'<td>{bar}</td>'
            f'<td style="color:#F5A623;">{skill}%</td>'
            f'<td style="color:#4A9EFF;">{semantic}%</td>'
            f'<td style="color:#2ECC71;">{exp}%</td>'
            f'</tr>'
        )

    header = '<tr><th>Rank</th><th>Candidate</th><th>Overall Score</th><th>Skill</th><th>Semantic</th><th>Experience</th></tr>'
    st.markdown(f'<table class="leaderboard-table"><thead>{header}</thead><tbody>{"".join(rows)}</tbody></table>', unsafe_allow_html=True)


# --- 8. SIDEBAR ---
from src.chains import AVAILABLE_MODELS

st.sidebar.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;letter-spacing:3px;color:#F5A623;padding:20px 0 8px 0;">YIELD.AI</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:2px;color:#2A2F3A;padding-bottom:16px;border-bottom:1px solid rgba(245,166,35,0.1);">NEURAL EVALUATION ENGINE</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:2px;color:#4A5568;padding:16px 0 8px 0;">MODEL</div>', unsafe_allow_html=True)
selected_model_label = st.sidebar.selectbox(
    "LLM Backend",
    options=list(AVAILABLE_MODELS.keys()),
    index=0,
    label_visibility="collapsed"
)
selected_model = AVAILABLE_MODELS[selected_model_label]
st.sidebar.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:#2A2F3A;padding-bottom:16px;">{selected_model}</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div style="border-top:1px solid rgba(245,166,35,0.1);margin:8px 0 16px 0;"></div>', unsafe_allow_html=True)
if st.sidebar.button("CLEAR SESSION", type="secondary"):
    import shutil
    if os.path.exists(session_base):
        shutil.rmtree(session_base)
    st.sidebar.success("Session cleared.")
    time.sleep(1)
    st.rerun()

# ── session file count indicator
n_files = len([f for f in os.listdir(raw_dir) if f.lower().endswith(('.pdf', '.docx'))]) if os.path.exists(raw_dir) else 0
st.sidebar.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:2px;color:#2A2F3A;margin-top:24px;">SESSION FILES&nbsp;&nbsp;<span style="color:#F5A623;">{n_files}</span></div>', unsafe_allow_html=True)


# --- 9. HERO ---
st.markdown("""
<div class="yield-hero">
    <div class="yield-hero-eyebrow">AI · ML Engineering · Evaluation Pipeline</div>
    <div class="yield-hero-title">Yield<span>.</span>ai</div>
    <div class="yield-hero-sub">B.A.B.Y. — Biometric & Ability Based Yield-engine &nbsp;·&nbsp; RAG · LangChain · RAGAS · ChromaDB</div>
</div>
""", unsafe_allow_html=True)

# --- 10. UPLOAD + JD ---
col1, col2 = st.columns([1, 1], gap="large")
with col1:
    st.markdown('<div class="section-label">Upload Resumes</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "PDF or DOCX files",
        accept_multiple_files=True,
        type=["pdf", "docx"],
        label_visibility="collapsed"
    )
with col2:
    st.markdown('<div class="section-label">Job Description</div>', unsafe_allow_html=True)
    jd_text = st.text_area("Paste JD", height=160, placeholder="Paste the target job description here...", label_visibility="collapsed")

st.write("")
if st.button("▶ RUN EVALUATION", type="primary", use_container_width=True):
    if uploaded_files:
        for f in uploaded_files:
            with open(os.path.join(raw_dir, f.name), "wb") as out:
                out.write(f.getbuffer())

    files_to_process = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.pdf', '.docx'))]

    if not files_to_process:
        st.warning("No resumes found in session.")
    elif not jd_text:
        st.warning("Please paste a Job Description.")
    else:
        progress_bar = st.progress(0)
        status_text  = st.empty()

        def update_ui_callback(current_index, total, filename):
            percent = int(((current_index + 1) / total) * 100)
            progress_bar.progress(percent)
            status_text.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;letter-spacing:1px;">PROCESSING {current_index+1}/{total} — {filename}</div>', unsafe_allow_html=True)

        with st.spinner(""):
            process_resumes_to_csv(raw_dir, output_csv, jd_text, progress_callback=update_ui_callback, model_name=selected_model)

        status_text.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#2ECC71;letter-spacing:1px;">✓ {len(files_to_process)} RESUMES EVALUATED</div>', unsafe_allow_html=True)
        time.sleep(1)
        st.rerun()


# --- 11. TABS ---
st.write("")
tab1, tab2, tab3 = st.tabs(["LEADERBOARD", "OPTIMIZER", "LIVE ANALYSIS"])

with tab1:
    with st.expander("ADMIN ACCESS — VIEW GLOBAL HISTORY"):
        pw = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter admin password...")

    display_df = pd.DataFrame()
    admin_pw   = ""
    try:
        admin_pw = st.secrets.get("ADMIN_PASSWORD", "")
    except Exception:
        pass

    if pw and admin_pw and pw == admin_pw:
        st.success("Admin mode active.")
        display_df = get_all_evaluations()
        display_df = display_df.rename(columns={"Match Score (%)": "Score"})
    else:
        if os.path.exists(output_csv):
            display_df = pd.read_csv(output_csv)
            st.info("Showing current session results.")

    if not display_df.empty:
        render_leaderboard(display_df)
        st.markdown('<div style="border-top:1px solid rgba(245,166,35,0.1);margin:32px 0;"></div>', unsafe_allow_html=True)

        selected_candidate = st.selectbox(
            "Deep dive →",
            display_df["Candidate Name"].unique(),
            label_visibility="collapsed"
        )
        candidate_row = display_df[display_df["Candidate Name"] == selected_candidate].iloc[0]
        render_scorecard(candidate_row["Candidate Name"], candidate_row)

        st.markdown('<div style="border-top:1px solid rgba(245,166,35,0.1);margin:32px 0;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Skill Gap Radar</div>', unsafe_allow_html=True)
        chart = create_radar_chart(
            candidate_row["Candidate Name"],
            skill_match=candidate_row.get("Skill Match", 0),
            semantic_match=candidate_row.get("Semantic Match", 0),
            experience_relevance=candidate_row.get("Experience Relevance", 0)
        )
        st.plotly_chart(chart, use_container_width=True)

        with st.expander("RAW DATA"):
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:12px;color:#2A2F3A;letter-spacing:2px;padding:48px 0;text-align:center;">NO EVALUATIONS YET — UPLOAD RESUMES AND RUN THE PIPELINE</div>', unsafe_allow_html=True)


with tab2:
    if os.path.exists(output_csv):
        df = pd.read_csv(output_csv)
        selected_name  = st.selectbox("Select candidate", df["Candidate Name"], label_visibility="collapsed")
        candidate_data = df[df["Candidate Name"] == selected_name].iloc[0]

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-label">Matched Skills</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:12px;color:#2ECC71;">{candidate_data.get("Matched Skills","N/A")}</div>', unsafe_allow_html=True)
        with col_b:
            st.markdown('<div class="section-label">Missing Skills</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:12px;color:#E74C3C;">{candidate_data.get("Missing Skills","N/A")}</div>', unsafe_allow_html=True)

        st.write("")
        if st.button("▶ GENERATE RESUME BULLETS", type="primary"):
            with st.spinner(""):
                missing_list = [s.strip() for s in str(candidate_data["Missing Skills"]).split(",") if s.strip() and s.strip().lower() != "nan"]
                matched_raw  = candidate_data.get("Matched Skills", "")
                suggestions  = generate_optimized_bullets(missing_skills=missing_list, matched_skills=matched_raw, candidate_name=selected_name)

            st.markdown('<div style="border-top:1px solid rgba(245,166,35,0.1);margin:24px 0;"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">AI-Generated Bullets</div>', unsafe_allow_html=True)
            for i, tip in enumerate(suggestions):
                st.markdown(f'<div style="background:#0D0D12;border-left:3px solid #F5A623;padding:16px 20px;margin-bottom:12px;font-family:Syne,sans-serif;font-size:14px;color:#E8EDF5;line-height:1.6;">{tip}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:12px;color:#2A2F3A;letter-spacing:2px;padding:48px 0;text-align:center;">RUN AN EVALUATION FIRST</div>', unsafe_allow_html=True)


with tab3:
    st.markdown('<div class="section-label">Live Streaming Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:11px;color:#4A5568;margin-bottom:24px;">Token-by-token narrative evaluation streamed directly from the LLM.</div>', unsafe_allow_html=True)

    from src.chains import stream_evaluation
    from src.sanitizer import clean_pii as _clean

    stream_resume = st.text_area("Resume", height=180, placeholder="Paste resume text...", key="stream_resume", label_visibility="collapsed")
    stream_jd     = st.text_area("JD", height=120, placeholder="Paste job description...", key="stream_jd", label_visibility="collapsed")

    st.write("")
    if st.button("▶ STREAM ANALYSIS", type="primary"):
        if not stream_resume.strip() or not stream_jd.strip():
            st.warning("Paste both a resume and JD to continue.")
        else:
            st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:9px;letter-spacing:2px;color:#F5A623;margin-bottom:12px;">MODEL — {selected_model}</div>', unsafe_allow_html=True)
            st.markdown('<div style="border-top:1px solid rgba(245,166,35,0.1);margin-bottom:16px;"></div>', unsafe_allow_html=True)
            output_box = st.empty()
            full_text  = ""
            for token in stream_evaluation(resume_text=_clean(stream_resume), jd_text=stream_jd, model_name=selected_model):
                full_text += token
                output_box.markdown(f'<div style="font-family:Syne,sans-serif;font-size:14px;color:#E8EDF5;line-height:1.8;background:#0D0D12;padding:24px;border-left:3px solid #F5A623;">{full_text}▌</div>', unsafe_allow_html=True)
            output_box.markdown(f'<div style="font-family:Syne,sans-serif;font-size:14px;color:#E8EDF5;line-height:1.8;background:#0D0D12;padding:24px;border-left:3px solid #F5A623;">{full_text}</div>', unsafe_allow_html=True)