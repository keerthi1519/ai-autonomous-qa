import os
import streamlit as st
import streamlit.components.v1 as components

REPORT_PATH = "reports/report.html"

st.set_page_config(
    page_title="Reports",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Selenium Execution Report")

st.divider()

# -------------------------------------------------------
# Validate Execution
# -------------------------------------------------------

if "execution_result" not in st.session_state:

    st.warning("⚠ Please execute the Selenium tests first.")

    st.stop()

execution = st.session_state["execution_result"]

status = execution.get(
    "status",
    "UNKNOWN"
)

return_code = execution.get(
    "return_code",
    -1
)

stdout = execution.get(
    "stdout",
    ""
)

stderr = execution.get(
    "stderr",
    ""
)

report = execution.get(
    "report",
    REPORT_PATH
)

# -------------------------------------------------------
# Summary
# -------------------------------------------------------

st.subheader("📈 Execution Summary")

col1, col2, col3 = st.columns(3)

with col1:

    if return_code == 0:
        st.success("🟢 PASSED")
    else:
        st.error("🔴 FAILED")

with col2:

    st.metric(
        "Return Code",
        return_code
    )

with col3:

    st.metric(
        "Status",
        status
    )

st.divider()

# -------------------------------------------------------
# Report Information
# -------------------------------------------------------

if report and os.path.exists(report):

    file_size = os.path.getsize(report) / 1024

    st.success("✅ HTML Report Generated Successfully")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Report Name",
            os.path.basename(report)
        )

    with col2:

        st.metric(
            "Size (KB)",
            f"{file_size:.2f}"
        )

    st.divider()

    # ----------------------------------------
    # Download Report
    # ----------------------------------------

    with open(report, "rb") as f:

        st.download_button(
            label="⬇ Download HTML Report",
            data=f,
            file_name="report.html",
            mime="text/html",
            use_container_width=True
        )

    st.divider()

    # ----------------------------------------
    # Preview Report
    # ----------------------------------------

    st.subheader("📄 HTML Report Preview")

    with open(
        report,
        "r",
        encoding="utf-8"
    ) as f:

        html = f.read()

    components.html(
        html,
        height=900,
        scrolling=True
    )

else:

    st.warning("⚠ HTML Report not found.")

    st.info(
        "Execute the Selenium tests to generate the report."
    )

# -------------------------------------------------------
# Console Output
# -------------------------------------------------------

st.divider()

with st.expander(
    "📜 Console Output",
    expanded=False
):

    if stdout:

        st.code(stdout)

    else:

        st.info("No console output available.")

# -------------------------------------------------------
# Error Log
# -------------------------------------------------------

with st.expander(
    "❌ Error Log",
    expanded=False
):

    if stderr:

        st.code(stderr)

    else:

        st.success("No errors reported.")