import requests
import streamlit as st
import streamlit.components.v1 as components

from config import BACKEND_URL

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

st.divider()


def call_backend(endpoint: str, spinner_text: str, timeout: int = 900):
    """POST to the backend and handle every failure mode."""

    with st.spinner(spinner_text):
        try:
            response = requests.post(
                f"{BACKEND_URL}{endpoint}",
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend.")
            st.code(BACKEND_URL)
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out.")
        except requests.exceptions.HTTPError:
            st.error(f"❌ Backend error ({response.status_code}).")
            try:
                st.json(response.json())
            except Exception:
                st.code(response.text)
        except Exception as e:
            st.exception(e)

    st.stop()


# --------------------------------------------------
# Execute
# --------------------------------------------------

st.info(
    "Click the button below to execute all generated "
    "Selenium test scripts."
)

if st.button("▶ Execute Tests", use_container_width=True, type="primary"):
    result = call_backend("/execute", "Running Selenium tests...")
    st.session_state["execution_result"] = result
    st.rerun()

# --------------------------------------------------
# Results
# --------------------------------------------------

if "execution_result" in st.session_state:

    result = st.session_state["execution_result"]

    return_code = result.get("return_code", -1)
    passed = result.get("passed", 0)
    failed = result.get("failed", 0)
    skipped = result.get("skipped", 0)
    duration = result.get("duration_seconds", 0)

    st.divider()
    st.subheader("📊 Execution Summary")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        if return_code == 0:
            st.success("🟢 PASSED")
        else:
            st.error("🔴 FAILED")

    c2.metric("Passed", passed)
    c3.metric("Failed", failed)
    c4.metric("Skipped", skipped)
    c5.metric("Duration", f"{duration:.0f}s")

    # ----------------------------------------------
    # Self-healing (shown only when something failed)
    # ----------------------------------------------

    if return_code != 0 and result.get("failed_files"):

        st.divider()
        st.subheader("🩹 Self-Healing")

        st.write(
            "Failing tests: "
            + ", ".join(f"`{f}`" for f in result["failed_files"])
        )

        st.info(
            "Auto-Heal sends each failing script together with its "
            "runtime error to the AI, applies the corrected version, "
            "and re-runs the whole suite."
        )

        if st.button("🩹 Auto-Heal Failed Tests", use_container_width=True):
            healed_result = call_backend(
                "/heal", "Healing failed tests and re-running..."
            )
            st.session_state["execution_result"] = healed_result
            st.rerun()

    # ----------------------------------------------
    # Healing outcome (present after a /heal run)
    # ----------------------------------------------

    if result.get("healed_files"):
        st.success(
            "🩹 Healed: " + ", ".join(result["healed_files"])
        )

    if result.get("unhealed_files"):
        for item in result["unhealed_files"]:
            st.warning(
                f"Could not heal {item['file']}: {item['reason']}"
            )

    # ----------------------------------------------
    # HTML report
    # ----------------------------------------------

    st.divider()
    st.subheader("📄 HTML Report")

    try:
        report_resp = requests.get(f"{BACKEND_URL}/report", timeout=30)
    except requests.exceptions.RequestException:
        report_resp = None

    if report_resp is not None and report_resp.status_code == 200:

        html = report_resp.text

        st.download_button(
            "⬇ Download HTML Report",
            data=html,
            file_name="report.html",
            mime="text/html",
            use_container_width=True
        )

        components.html(html, height=800, scrolling=True)

    else:
        st.warning("HTML Report not found.")

    # ----------------------------------------------
    # Console output
    # ----------------------------------------------

    with st.expander("📜 Console Output"):
        if result.get("stdout"):
            st.code(result["stdout"])
        else:
            st.info("No console output.")

    with st.expander("❌ Error Log"):
        if result.get("stderr"):
            st.code(result["stderr"])
        else:
            st.success("No errors reported.")
