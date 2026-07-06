import json

import requests
import streamlit as st

from config import BACKEND_URL

st.set_page_config(
    page_title="Download Center",
    page_icon="📥",
    layout="wide"
)

st.title("📥 Download Center")

st.markdown(
    "Download all generated project artifacts from a single place."
)

st.divider()


def fetch(endpoint, as_json=True):
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=30)
        if response.status_code != 200:
            return None
        return response.json() if as_json else response.text
    except requests.exceptions.RequestException:
        return None


# ----------------------------------------------------
# Uploaded requirement documents
# ----------------------------------------------------

st.subheader("📄 Uploaded Requirement Documents")

uploads = fetch("/artifacts/uploads")

if uploads:
    for item in uploads:
        st.download_button(
            label=f"⬇ Download {item['name']}",
            data=item["content"],
            file_name=item["name"],
            use_container_width=True,
            key=f"upload_{item['name']}"
        )
else:
    st.info("No uploaded documents available.")

st.divider()

# ----------------------------------------------------
# Generated Selenium scripts
# ----------------------------------------------------

st.subheader("🤖 Generated Selenium Scripts")

tests = fetch("/artifacts/tests")

if tests:
    for item in tests:
        with st.expander(item["name"]):
            st.code(item["code"], language="python")
            st.download_button(
                label=f"⬇ Download {item['name']}",
                data=item["code"],
                file_name=item["name"],
                use_container_width=True,
                key=f"test_{item['name']}"
            )
else:
    st.info("No generated scripts available.")

st.divider()

# ----------------------------------------------------
# HTML test report
# ----------------------------------------------------

st.subheader("📊 HTML Test Report")

report_html = fetch("/report", as_json=False)

if report_html:
    st.download_button(
        label="⬇ Download report.html",
        data=report_html,
        file_name="report.html",
        mime="text/html",
        use_container_width=True,
        key="report"
    )
else:
    st.info("No report available. Execute the tests first.")

st.divider()

# ----------------------------------------------------
# Execution history
# ----------------------------------------------------

st.subheader("📜 Execution History")

history = fetch("/history")

if history:
    st.download_button(
        label="⬇ Download history.json",
        data=json.dumps(history, indent=2),
        file_name="history.json",
        mime="application/json",
        use_container_width=True,
        key="history"
    )
else:
    st.info("No execution history available.")

st.divider()

# ----------------------------------------------------
# Summary
# ----------------------------------------------------

st.subheader("📦 Artifact Summary")

c1, c2, c3 = st.columns(3)
c1.metric("Requirement Files", len(uploads) if uploads else 0)
c2.metric("Generated Tests", len(tests) if tests else 0)
c3.metric("Runs Recorded", len(history) if history else 0)
