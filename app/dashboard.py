import sys
import os
import pandas as pd
import streamlit as st
import time
import uuid

# 1. PATH INJECTION
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 2. SESSION-BASED PRIVACY LOGIC (Move this BEFORE other path definitions)
if 'session_id' not in st.session_state:
    st.session_state['session_id'] = str(uuid.uuid4())

# Create a private sandbox folder for this specific visitor
session_base = os.path.join("data", "sessions", st.session_state['session_id'])
raw_dir = os.path.join(session_base, "raw")
processed_dir = os.path.join(session_base, "processed")

os.makedirs(raw_dir, exist_ok=True)
os.makedirs(processed_dir, exist_ok=True)

# These are the variables the rest of the app will use
output_csv = os.path.join(processed_dir, "evaluation_report.csv")
# Note: Since your DB module might be hardcoded to yield_engine.db, 
# we focus on the session-based folders for PDFs and CSVs for now.

# 3. IMPORTS & INIT
from src.main import process_resumes_to_csv
from src.database import init_db, get_all_evaluations
from src.visualizer import create_radar_chart
from src.optimizer import generate_optimized_bullets

# Initialize the global DB structure if not exists
init_db()

# --- SETTINGS ---
st.set_page_config(page_title="Yield.ai | MLE Evaluation Engine", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("🛠️ System Status")
# The Clear button now only clears THIS session
if st.sidebar.button("🗑️ Clear My Session", type="secondary"):
    for f in os.listdir(raw_dir):
        os.remove(os.path.join(raw_dir, f))
    if os.path.exists(output_csv):
        os.remove(output_csv)
    st.sidebar.success("Session Cleared!")
    st.rerun()

# --- MAIN UI ---
st.title("🤖 Yield.ai: Biometric & Ability Based Yield-engine")
st.markdown("---")

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("📄 Upload Resumes")
    uploaded_files = st.file_uploader("Choose PDF files", accept_multiple_files=True, type="pdf")
with col2:
    st.subheader("📝 Job Description")
    jd_text = st.text_area("Paste the target JD here...", height=200)

if st.button("🚀 Run AI Evaluation", type="primary", use_container_width=True):
    # Save uploads to the SESSION folder
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with open(os.path.join(raw_dir, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
    
    files_to_process = [f for f in os.listdir(raw_dir) if f.endswith(".pdf")]
    
    if not files_to_process:
        st.warning("⚠️ No resumes found.")
    elif not jd_text:
        st.warning("⚠️ Please paste a Job Description.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_ui_callback(current_index, total, filename):
            percent = int(((current_index + 1) / total) * 100)
            progress_bar.progress(percent)
            status_text.text(f"🧪 Analyzing ({current_index + 1}/{total}): {filename}...")

        with st.spinner("Pipeline active..."):
            process_resumes_to_csv(raw_dir, output_csv, jd_text, progress_callback=update_ui_callback)
            
        status_text.success(f"✅ Success! {len(files_to_process)} resumes analyzed.")
        time.sleep(1)
        st.rerun()

# --- TABS ---
tab1, tab2 = st.tabs(["🏆 Leaderboard", "✨ AI Resume Optimizer"])

with tab1:
    st.header("Session Analysis")
    
    # Check for the password to see the "Global" history
    with st.expander("🔓 Admin Access (View Global History)"):
        pw = st.text_input("Enter Admin Password", type="password")
    
    if pw == st.secrets.get("ADMIN_PASSWORD"):
        st.success("Admin Mode: Showing all historical data.")
        display_df = get_all_evaluations()
    else:
        # Show ONLY session data
        if os.path.exists(output_csv):
            display_df = pd.read_csv(output_csv)
            st.info("Showing current session results only.")
        else:
            display_df = pd.DataFrame()

    if not display_df.empty:
        selected_candidate = st.selectbox("Select Candidate", display_df["Candidate Name"].unique())
        candidate_row = display_df[display_df["Candidate Name"] == selected_candidate].iloc[0]
        
        chart = create_radar_chart(
            candidate_row["Candidate Name"], 
            candidate_row["Matched Skills"], 
            candidate_row["Missing Skills"]
        )
        st.plotly_chart(chart, use_container_width=True)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No evaluations to display yet.")

with tab2:
    # Use session CSV for optimization
    if os.path.exists(output_csv):
        df = pd.read_csv(output_csv)
        selected_name = st.selectbox("Select Candidate to Optimize", df["Candidate Name"], key="opt_select")
        candidate_data = df[df["Candidate Name"] == selected_name].iloc[0]
        
        st.write(f"**Missing Skills:** {candidate_data['Missing Skills']}")
        
        if st.button("✨ Generate Optimized Bullet Points"):
            with st.spinner("Analyzing..."):
                missing_list = str(candidate_data["Missing Skills"]).split(", ")
                suggestions = generate_optimized_bullets(missing_list, "Candidate Context")
                for i, tip in enumerate(suggestions):
                    st.success(f"**Suggestion {i+1}:** {tip}")
    else:
        st.info("Run an evaluation first to see optimization tips.")