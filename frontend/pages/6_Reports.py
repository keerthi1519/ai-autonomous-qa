import requests
import streamlit as st
import streamlit.components.v1 as components

from config import BACKEND_URL

st.set_page_config(
    page_title="Reports",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Selenium Execution Report")

st.divider()

# -------------------------------------------------------
# Execution summary (from session, if available)
# -------------------------------------------------------

if "execution_result" in st.session_state:

    execution = st.session_state["execution_result"]

    return_code = execution.get("return_code", -1)

    st.subheader("📈 Execution Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if return_code == 0:
            st.success("🟢 PASSED")
        else:
            st.error("🔴 FAILED")

    c2.metric("Passed", execution.get("passed", 0))
    c3.metric("Failed", execution.get("failed", 0))
    c4.metric("Duration", f"{execution.get('duration_seconds', 0):.0f}s")

    st.divider()

# -------------------------------------------------------
# HTML report (served by the backend)
# -------------------------------------------------------

try:
    response = requests.get(f"{BACKEND_URL}/report", timeout=30)
except requests.exceptions.RequestException:
    response = None

if response is not None and response.status_code == 200:

    html = response.text

    st.success("✅ HTML Report Available")

    st.download_button(
        label="⬇ Download HTML Report",
        data=html,
        file_name="report.html",
        mime="text/html",
        use_container_width=True
    )

    st.divider()

    st.subheader("📄 HTML Report Preview")

    components.html(html, height=900, scrolling=True)

else:
    st.warning("⚠ HTML Report not found.")
    st.info("Execute the Selenium tests to generate the report.")

# -------------------------------------------------------
# Console output (from session)
# -------------------------------------------------------

if "execution_result" in st.session_state:

    execution = st.session_state["execution_result"]

    st.divider()

    with st.expander("📜 Console Output"):
        if execution.get("stdout"):
            st.code(execution["stdout"])
        else:
            st.info("No console output available.")

    with st.expander("❌ Error Log"):
        if execution.get("stderr"):
            st.code(execution["stderr"])
        else:
            st.success("No errors reported.")
