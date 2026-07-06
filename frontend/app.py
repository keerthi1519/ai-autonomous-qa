import requests
import streamlit as st

from config import BACKEND_URL

st.set_page_config(
    page_title="AI Autonomous QA Engineer",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Autonomous QA Engineer")
st.caption("AI-powered requirement analysis and Selenium test automation")

# --------------------------------------------------
# Backend health check
# --------------------------------------------------

def backend_online() -> bool:
    try:
        r = requests.get(BACKEND_URL, timeout=5)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


online = backend_online()

with st.sidebar:
    st.header("Backend Status")
    if online:
        st.success("🟢 Connected")
    else:
        st.error("🔴 Offline")
    st.caption(BACKEND_URL)

if not online:
    st.error(
        "Cannot reach the backend. Start it first, then reload this page."
    )
    st.code("uvicorn app.main:app --reload   # or: docker compose up")

st.divider()

# --------------------------------------------------
# Pipeline progress
# --------------------------------------------------

st.subheader("Pipeline Progress")

steps = [
    ("1. Requirement Analysis", "analysis"),
    ("2. Test Scenarios", "test_scenarios"),
    ("3. Test Cases", "test_cases"),
    ("4. Selenium Scripts", "selenium_scripts"),
    ("5. Execution", "execution_result"),
]

cols = st.columns(len(steps))

for col, (label, key) in zip(cols, steps):
    with col:
        if key in st.session_state:
            st.success(f"✅ {label}")
        else:
            st.info(f"⬜ {label}")

st.divider()

# --------------------------------------------------
# Statistics
# --------------------------------------------------

st.subheader("Statistics")

scenarios = (
    st.session_state.get("test_scenarios", {})
    .get("test_scenarios", [])
)
cases = (
    st.session_state.get("test_cases", {})
    .get("test_cases", [])
)
scripts = (
    st.session_state.get("selenium_scripts", {})
    .get("scripts", [])
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Requirement", "✔" if "analysis" in st.session_state else "—")
c2.metric("Scenarios", len(scenarios))
c3.metric("Test Cases", len(cases))
c4.metric("Scripts", len(scripts))

st.divider()

# --------------------------------------------------
# How to use
# --------------------------------------------------

st.subheader("How to Use")

st.markdown(
    """
**Option A — one click:** open **AI QA Pipeline** in the sidebar,
upload a requirement document, enter your application URL, and press
**Run Full Pipeline**.

**Option B — step by step:** go through the sidebar pages in order:

1. **Requirement Analysis** — upload the document and set the application URL
2. **Test Scenarios** — generate scenarios from the analysis
3. **Test Cases** — turn scenarios into detailed test cases
4. **Selenium Scripts** — generate runnable pytest + Selenium code
5. **Execute Tests** — run everything and view the HTML report
"""
)
