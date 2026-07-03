import streamlit as st
import requests

from config import BACKEND_URL

st.set_page_config(
    page_title="Test Scenarios",
    page_icon="🧪"
)

st.title("🧪 Test Scenarios")

# --------------------------------------------------
# Validate Previous Step
# --------------------------------------------------

if "analysis" not in st.session_state:

    st.error("❌ Requirement Analysis has not been completed.")

    st.info("Please complete the Requirement Analysis page first.")

    st.stop()

analysis = st.session_state["analysis"]

application_url = st.session_state.get(
    "application_url",
    ""
)

# --------------------------------------------------
# Display Information
# --------------------------------------------------

st.info(f"🌐 Application URL: {application_url}")

# --------------------------------------------------
# Generate Test Scenarios
# --------------------------------------------------

if st.button(
    "🚀 Generate Test Scenarios",
    use_container_width=True
):

    with st.spinner("Generating Test Scenarios..."):

        try:

            response = requests.post(
                f"{BACKEND_URL}/generate-scenarios",
                json=analysis,
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

    # ---------------------------------------
    # Save Pipeline Data
    # ---------------------------------------

    st.session_state["test_scenarios"] = result
    st.session_state["current_step"] = "test_scenarios"

    st.success("✅ Test Scenarios Generated Successfully")

# --------------------------------------------------
# Display Scenarios
# --------------------------------------------------

if "test_scenarios" in st.session_state:

    scenarios = st.session_state["test_scenarios"]

    scenario_list = scenarios.get(
        "test_scenarios",
        []
    )

    st.divider()

    st.subheader("📋 Generated Test Scenarios")

    st.success(
        f"Total Test Scenarios: {len(scenario_list)}"
    )

    for scenario in scenario_list:

        with st.expander(
            f"{scenario.get('id')} - {scenario.get('title')}"
        ):

            st.write(
                f"**Scenario ID:** {scenario.get('id')}"
            )

            st.write(
                f"**Title:** {scenario.get('title')}"
            )

            st.write(
                f"**Category:** {scenario.get('category')}"
            )

            st.write(
                f"**Priority:** {scenario.get('priority')}"
            )

            if "description" in scenario:

                st.write(
                    f"**Description:** {scenario.get('description')}"
                )

            if "preconditions" in scenario:

                st.write("**Preconditions:**")

                for item in scenario["preconditions"]:
                    st.write(f"• {item}")

            if "expected_result" in scenario:

                st.write(
                    f"**Expected Result:** {scenario.get('expected_result')}"
                )

    st.divider()

    st.success(
        "➡ Proceed to the **Test Cases** page."
    )