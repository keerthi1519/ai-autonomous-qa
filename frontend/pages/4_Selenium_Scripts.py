import requests
import streamlit as st

from config import BACKEND_URL

st.set_page_config(
    page_title="Selenium Scripts",
    page_icon="🤖"
)

st.title("🤖 Selenium Script Generator")

# --------------------------------------------------
# Validate Previous Steps
# --------------------------------------------------

if "test_cases" not in st.session_state:

    st.error("❌ Test Cases have not been generated.")
    st.info("Please complete the Test Cases page first.")
    st.stop()

if "application_url" not in st.session_state:

    st.error("❌ Application URL not found.")
    st.info("Please complete Requirement Analysis again.")
    st.stop()

test_cases = st.session_state["test_cases"]
application_url = st.session_state["application_url"]

st.info(f"🌐 Application URL: {application_url}")

payload = {
    "application_url": application_url,
    "test_cases": test_cases
}

# --------------------------------------------------
# Generate Selenium Scripts
# --------------------------------------------------

if st.button(
    "🚀 Generate Selenium Scripts",
    use_container_width=True
):

    with st.spinner("Generating Selenium Scripts..."):

        try:

            response = requests.post(
                f"{BACKEND_URL}/generate-selenium",
                json=payload,
                timeout=300
            )

            response.raise_for_status()

            result = response.json()

        except requests.exceptions.ConnectionError:

            st.error("❌ Cannot connect to Backend")
            st.code(BACKEND_URL)
            st.stop()

        except requests.exceptions.Timeout:

            st.error("❌ Backend request timed out.")
            st.stop()

        except requests.exceptions.HTTPError:

            st.error("❌ Backend returned an error.")

            try:
                st.json(response.json())
            except Exception:
                st.code(response.text)

            st.stop()

        except Exception as e:

            st.exception(e)
            st.stop()

    # --------------------------------------------
    # Store in Session State
    # --------------------------------------------

    st.session_state["selenium_scripts"] = result
    st.session_state["current_step"] = "selenium"

    st.success("✅ Selenium Scripts Generated Successfully")

# --------------------------------------------------
# Display Generated Scripts
# --------------------------------------------------

if "selenium_scripts" in st.session_state:

    scripts = st.session_state["selenium_scripts"]

    script_list = scripts.get("scripts", [])

    st.divider()

    st.subheader("📜 Generated Selenium Scripts")

    st.success(
        f"Total Selenium Scripts: {len(script_list)}"
    )

    for script in script_list:

        with st.expander(script.get("file_name", "Unknown")):

            st.write(f"**Test Case ID:** {script.get('test_case_id')}")

            st.code(
                script.get("code", ""),
                language="python"
            )

    st.divider()

    st.success(
        "➡ Proceed to the **Execute Tests** page."
    )