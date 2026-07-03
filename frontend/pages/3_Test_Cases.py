import streamlit as st
import requests

from config import BACKEND_URL

st.set_page_config(
    page_title="Test Cases",
    page_icon="📝"
)

st.title("📝 Test Cases")

# --------------------------------------------------
# Validate Previous Step
# --------------------------------------------------

if "test_scenarios" not in st.session_state:

    st.error("❌ Test Scenarios have not been generated.")

    st.info("Please complete the Test Scenarios page first.")

    st.stop()

scenarios = st.session_state["test_scenarios"]

application_url = st.session_state.get(
    "application_url",
    ""
)

st.info(f"🌐 Application URL: {application_url}")

# --------------------------------------------------
# Generate Test Cases
# --------------------------------------------------

if st.button(
    "🚀 Generate Test Cases",
    use_container_width=True
):

    with st.spinner("Generating Test Cases..."):

        try:

            response = requests.post(
                f"{BACKEND_URL}/generate-testcases",
                json=scenarios,
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

    # --------------------------------------------------
    # Save Pipeline Data
    # --------------------------------------------------

    st.session_state["test_cases"] = result
    st.session_state["current_step"] = "test_cases"

    st.success("✅ Test Cases Generated Successfully")

# --------------------------------------------------
# Display Test Cases
# --------------------------------------------------

if "test_cases" in st.session_state:

    cases = st.session_state["test_cases"]

    case_list = cases.get(
        "test_cases",
        []
    )

    st.divider()

    st.subheader("📋 Generated Test Cases")

    st.success(
        f"Total Test Cases: {len(case_list)}"
    )

    for case in case_list:

        case_id = (
            case.get("id")
            or case.get("test_case_id")
            or case.get("testcase_id")
            or "N/A"
        )

        title = case.get(
            "title",
            "Untitled Test Case"
        )

        priority = case.get(
            "priority",
            "N/A"
        )

        with st.expander(f"{case_id} - {title}"):

            st.write(f"**Test Case ID:** {case_id}")

            st.write(f"**Title:** {title}")

            st.write(f"**Priority:** {priority}")

            if "description" in case:

                st.write(
                    f"**Description:** {case.get('description')}"
                )

            st.write("### Test Steps")

            steps = case.get("steps", [])

            if steps:

                for index, step in enumerate(steps, start=1):

                    st.write(f"{index}. {step}")

            else:

                st.warning("No test steps available.")

            st.write("### Expected Result")

            st.success(
                case.get(
                    "expected_result",
                    "Not Available"
                )
            )

            if "preconditions" in case:

                st.write("### Preconditions")

                for item in case["preconditions"]:

                    st.write(f"• {item}")

    st.divider()

    st.success(
        "➡ Proceed to the **Selenium Scripts** page."
    )