import requests
import streamlit as st

from config import BACKEND_URL

st.set_page_config(
    page_title="AI QA Pipeline",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI QA Pipeline")
st.caption(
    "Run the whole pipeline in one click: "
    "analysis → scenarios → test cases → Selenium scripts."
)

st.divider()

uploaded_file = st.file_uploader(
    "Upload Requirement Document",
    type=["txt", "pdf", "docx"]
)

application_url = st.text_input(
    "Application URL",
    placeholder="https://www.saucedemo.com/"
)


def call_backend(step_name, method, endpoint, **kwargs):
    """Call the backend and stop with a clear message on any failure."""
    try:
        response = requests.request(
            method,
            f"{BACKEND_URL}{endpoint}",
            timeout=600,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        st.error(f"❌ {step_name}: cannot connect to backend.")
        st.code(BACKEND_URL)
    except requests.exceptions.Timeout:
        st.error(f"❌ {step_name}: request timed out.")
    except requests.exceptions.HTTPError:
        st.error(f"❌ {step_name}: backend returned an error.")
        try:
            st.json(response.json())
        except Exception:
            st.code(response.text)
    except Exception as e:
        st.exception(e)

    st.stop()


if st.button("▶ Run Full Pipeline", use_container_width=True, type="primary"):

    if uploaded_file is None:
        st.warning("⚠ Please upload a requirement document.")
        st.stop()

    if not application_url.strip():
        st.warning("⚠ Please enter the application URL.")
        st.stop()

    url = application_url.strip()

    # Reset previous run
    for key in [
        "analysis", "test_scenarios", "test_cases",
        "selenium_scripts", "execution_result"
    ]:
        st.session_state.pop(key, None)

    progress = st.progress(0, text="Step 1/4 — Analyzing requirement...")

    # ---------- Step 1: Requirement Analysis ----------
    result = call_backend(
        "Requirement Analysis", "post", "/upload",
        files={"file": (uploaded_file.name, uploaded_file.getvalue())},
        data={"application_url": url},
    )
    st.session_state["analysis"] = result["analysis"]
    st.session_state["application_url"] = url
    progress.progress(25, text="Step 2/4 — Generating test scenarios...")

    # ---------- Step 2: Test Scenarios ----------
    scenarios = call_backend(
        "Test Scenarios", "post", "/generate-scenarios",
        json=st.session_state["analysis"],
    )
    st.session_state["test_scenarios"] = scenarios
    progress.progress(50, text="Step 3/4 — Generating test cases...")

    # ---------- Step 3: Test Cases ----------
    cases = call_backend(
        "Test Cases", "post", "/generate-testcases",
        json=scenarios,
    )
    st.session_state["test_cases"] = cases
    progress.progress(75, text="Step 4/4 — Generating Selenium scripts...")

    # ---------- Step 4: Selenium Scripts ----------
    scripts = call_backend(
        "Selenium Scripts", "post", "/generate-selenium",
        json={"application_url": url, "test_cases": cases},
    )
    st.session_state["selenium_scripts"] = scripts
    progress.progress(100, text="Pipeline completed!")

    st.success("✅ Pipeline completed successfully.")

    # ---------- Summary ----------
    st.divider()
    st.subheader("📊 Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Scenarios",
        len(scenarios.get("test_scenarios", []))
    )
    c2.metric(
        "Test Cases",
        len(cases.get("test_cases", []))
    )
    c3.metric(
        "Selenium Scripts",
        len(scripts.get("scripts", []))
    )

    st.info(
        "➡ Open **Execute Tests** in the sidebar to run the "
        "generated scripts and view the HTML report."
    )

    with st.expander("View generated scripts"):
        for script in scripts.get("scripts", []):
            st.markdown(f"**{script.get('file_name', 'unknown')}**")
            st.code(script.get("code", ""), language="python")
