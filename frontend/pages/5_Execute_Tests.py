import os
import requests
import streamlit as st
import streamlit.components.v1 as components

from config import BACKEND_URL

REPORT_PATH = "reports/report.html"

st.set_page_config(
    page_title="Execute Tests",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Execute Selenium Tests")

# --------------------------------------------------
# Validation
# --------------------------------------------------

if "selenium_scripts" not in st.session_state:

    st.error("❌ Selenium Scripts not found.")

    st.info("Please generate Selenium Scripts first.")

    st.stop()

st.markdown("---")

st.info(
    "Click the button below to execute all generated Selenium test scripts."
)

# --------------------------------------------------
# Execute
# --------------------------------------------------

if st.button(
    "▶ Execute Tests",
    use_container_width=True
):

    progress = st.progress(0)

    status = st.empty()

    try:

        status.info("🚀 Starting Selenium Execution...")

        progress.progress(20)

        response = requests.post(
            f"{BACKEND_URL}/execute",
            timeout=600
        )

        response.raise_for_status()

        progress.progress(70)

        result = response.json()

        progress.progress(100)

        status.success("✅ Execution Finished Successfully")

        # -------------------------
        # Save Pipeline State
        # -------------------------

        st.session_state["execution_result"] = result
        st.session_state["current_step"] = "execution"

    except requests.exceptions.ConnectionError:

        st.error("❌ Cannot connect to FastAPI Backend.")

        st.info(f"Backend URL: {BACKEND_URL}")

        st.stop()

    except requests.exceptions.Timeout:

        st.error("❌ Test execution timed out.")

        st.stop()

    except requests.exceptions.HTTPError:

        st.error(
            f"Backend Error ({response.status_code})"
        )

        try:
            st.json(response.json())
        except Exception:
            st.code(response.text)

        st.stop()

    except Exception as e:

        st.exception(e)

        st.stop()

# --------------------------------------------------
# Display Result
# --------------------------------------------------

if "execution_result" in st.session_state:

    result = st.session_state["execution_result"]

    execution_status = result.get(
        "status",
        "UNKNOWN"
    )

    return_code = result.get(
        "return_code",
        -1
    )

    stdout = result.get(
        "stdout",
        ""
    )

    stderr = result.get(
        "stderr",
        ""
    )

    report = result.get(
        "report",
        REPORT_PATH
    )

    st.markdown("---")

    st.subheader("📊 Execution Summary")

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
            execution_status
        )

    st.markdown("---")

    # --------------------------------------------------
    # HTML REPORT
    # --------------------------------------------------

    st.subheader("📄 HTML Report")

    if report and os.path.exists(report):

        st.success("✅ HTML Report Generated")

        with open(
            report,
            "rb"
        ) as f:

            st.download_button(
                "⬇ Download HTML Report",
                data=f,
                file_name="report.html",
                mime="text/html",
                use_container_width=True
            )

        st.divider()

        with open(
            report,
            "r",
            encoding="utf-8"
        ) as f:

            html = f.read()

        components.html(
            html,
            height=800,
            scrolling=True
        )

    else:

        st.warning("HTML Report not found.")

    # --------------------------------------------------
    # Console Output
    # --------------------------------------------------

    with st.expander(
        "📜 Console Output"
    ):

        if stdout:

            st.code(stdout)

        else:

            st.info("No console output.")

    # --------------------------------------------------
    # Error Log
    # --------------------------------------------------

    with st.expander(
        "❌ Error Log"
    ):

        if stderr:

            st.code(stderr)

        else:

            st.success("No errors reported.")