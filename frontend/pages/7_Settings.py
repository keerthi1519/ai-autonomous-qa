import requests
import streamlit as st

from config import BACKEND_URL

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Settings")

st.divider()

# --------------------------------------------------
# Backend connection
# --------------------------------------------------

st.subheader("🔌 Backend Connection")

st.write("Backend URL (set via the `BACKEND_URL` environment variable):")
st.code(BACKEND_URL)

if st.button("Test Connection", use_container_width=True):
    try:
        response = requests.get(BACKEND_URL, timeout=5)
        response.raise_for_status()
        st.success("🟢 Backend is reachable.")
        st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error("🔴 Backend is not reachable.")
        st.caption(str(e))

st.divider()

# --------------------------------------------------
# Session data
# --------------------------------------------------

st.subheader("🗂 Session Data")

st.write(
    "The pipeline stores intermediate results (analysis, scenarios, "
    "test cases, scripts) in this browser session."
)

pipeline_keys = [
    "analysis",
    "analysis_data",
    "application_url",
    "uploaded_file_name",
    "test_scenarios",
    "test_cases",
    "selenium_scripts",
    "execution_result",
    "pipeline_started",
    "current_step",
]

stored = [k for k in pipeline_keys if k in st.session_state]

if stored:
    st.write("Currently stored:")
    for key in stored:
        st.write(f"• `{key}`")
else:
    st.info("No pipeline data stored yet.")

if st.button("🧹 Clear Pipeline Data", use_container_width=True):
    for key in pipeline_keys:
        st.session_state.pop(key, None)
    st.success("Session data cleared. Start again from Requirement Analysis.")
    st.rerun()
