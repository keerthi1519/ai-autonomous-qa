import streamlit as st
import requests

from config import BACKEND_URL

st.set_page_config(page_title="Requirement Analysis", page_icon="📄")

st.title("📄 Requirement Analysis")

st.write(
    "Upload the requirement document and provide the application URL."
)

uploaded_file = st.file_uploader(
    "Upload Requirement Document",
    type=["txt", "pdf", "docx"]
)

application_url = st.text_input(
    "Application URL",
    placeholder="https://opensource-demo.orangehrmlive.com/"
)


def clear_pipeline():
    keys = [
        "analysis",
        "analysis_data",
        "scenarios",
        "testcases",
        "selenium_scripts",
        "execution_result",
        "report"
    ]

    for key in keys:
        st.session_state.pop(key, None)


if st.button(
    "🔍 Analyze Requirement",
    use_container_width=True
):

    if uploaded_file is None:
        st.warning("⚠ Please upload a requirement document.")
        st.stop()

    if not application_url.strip():
        st.warning("⚠ Please enter the Application URL.")
        st.stop()

    clear_pipeline()

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue()
        )
    }

    data = {
        "application_url": application_url.strip()
    }

    with st.spinner("Analyzing Requirement..."):

        try:

            response = requests.post(
                f"{BACKEND_URL}/upload",
                files=files,
                data=data,
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

    if "analysis" not in result:
        st.error("Backend response does not contain requirement analysis.")
        st.json(result)
        st.stop()

    analysis = result["analysis"]

    # --------------------------
    # Save everything for the pipeline
    # --------------------------

    st.session_state["analysis"] = analysis
    st.session_state["analysis_data"] = result
    st.session_state["application_url"] = application_url.strip()
    st.session_state["uploaded_file_name"] = uploaded_file.name
    st.session_state["pipeline_started"] = True

    st.success("✅ Requirement Analysis Completed Successfully")

    st.divider()

    st.subheader("📋 Functional Requirements")

    for item in analysis.get("functional_requirements", []):
        st.write(f"• {item}")

    st.subheader("⚡ Non Functional Requirements")

    for item in analysis.get("non_functional_requirements", []):
        st.write(f"• {item}")

    st.subheader("⚠ Edge Cases")

    for item in analysis.get("edge_cases", []):
        st.write(f"• {item}")

    st.subheader("🔴 Risks")

    for item in analysis.get("risks", []):
        st.write(f"• {item}")

    st.divider()

    st.info("✅ Requirement Analysis completed successfully.")

    st.success(
        "➡ Now open the **Test Scenarios** page from the left sidebar."
    )