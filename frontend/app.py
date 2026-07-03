import streamlit as st
import requests

from config import BACKEND_URL

st.set_page_config(
    page_title="AI Autonomous QA Engineer",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Autonomous QA Engineer")
st.caption("AI-powered Requirement Analysis & Test Automation")

st.divider()

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:

    st.header("Navigation")

    st.success("Backend Status")

    st.write(BACKEND_URL)

# ----------------------------
# Metrics
# ----------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("Requirements", "0")
col2.metric("Scenarios", "0")
col3.metric("Test Cases", "0")
col4.metric("Scripts", "0")

st.divider()

uploaded_file = st.file_uploader(
    "📄 Upload Requirement Document",
    type=["txt", "pdf", "docx"]
)

if uploaded_file:

    st.success(f"{uploaded_file.name} uploaded.")

    if st.button(
        "🚀 Analyze Requirement",
        use_container_width=True
    ):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue()
            )
        }

        with st.spinner("Analyzing Requirement..."):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/upload",
                    files=files,
                    timeout=300
                )

                response.raise_for_status()

            except requests.exceptions.ConnectionError:

                st.error("❌ Cannot connect to backend.")

                st.info(
                    f"Backend URL: {BACKEND_URL}"
                )

                st.stop()

            except requests.exceptions.Timeout:

                st.error(
                    "Backend request timed out."
                )

                st.stop()

            except Exception as e:

                st.exception(e)

                st.stop()

        result = response.json()

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📋 Functional",
                "⚙ Non Functional",
                "⚠ Edge Cases",
                "🚨 Risks"
            ]
        )

        with tab1:

            for item in result["analysis"]["functional_requirements"]:
                st.success(item)

        with tab2:

            for item in result["analysis"]["non_functional_requirements"]:
                st.info(item)

        with tab3:

            for item in result["analysis"]["edge_cases"]:
                st.warning(item)

        with tab4:

            for item in result["analysis"]["risks"]:
                st.error(item)