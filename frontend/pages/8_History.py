import json
import os

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Execution History",
    page_icon="📜",
    layout="wide"
)

st.title("📜 Execution History")

HISTORY_FILE = "reports/history.json"

st.divider()

# --------------------------------------------------------
# Check History File
# --------------------------------------------------------

if not os.path.exists(HISTORY_FILE):

    st.warning("⚠ No execution history found.")

    st.info(
        "Execute Selenium tests to create execution history."
    )

    st.stop()

# --------------------------------------------------------
# Load History
# --------------------------------------------------------

try:

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        history = json.load(f)

except Exception as e:

    st.error("Unable to read history.json")

    st.exception(e)

    st.stop()

# --------------------------------------------------------
# Empty History
# --------------------------------------------------------

if not history:

    st.info("No executions have been recorded yet.")

    st.stop()

# --------------------------------------------------------
# Display Summary
# --------------------------------------------------------

st.subheader("📈 Summary")

total_runs = len(history)

passed = sum(
    1
    for item in history
    if item.get("status") == "SUCCESS"
)

failed = total_runs - passed

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total Runs",
        total_runs
    )

with col2:

    st.metric(
        "Passed",
        passed
    )

with col3:

    st.metric(
        "Failed",
        failed
    )

st.divider()

# --------------------------------------------------------
# Display Table
# --------------------------------------------------------

df = pd.DataFrame(history)

st.subheader("📋 Execution History")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# --------------------------------------------------------
# Latest Execution
# --------------------------------------------------------

latest = history[-1]

st.subheader("🕒 Latest Execution")

st.json(latest)

# --------------------------------------------------------
# Download History
# --------------------------------------------------------

with open(
    HISTORY_FILE,
    "rb"
) as f:

    st.download_button(
        "⬇ Download History",
        data=f,
        file_name="history.json",
        mime="application/json",
        use_container_width=True
    )

# --------------------------------------------------------
# Clear Session Button
# --------------------------------------------------------

if st.button(
    "🧹 Clear Current Session",
    use_container_width=True
):

    keys = [
        "analysis",
        "analysis_data",
        "test_scenarios",
        "test_cases",
        "selenium_scripts",
        "execution_result",
        "report_path",
        "current_step"
    ]

    for key in keys:
        st.session_state.pop(key, None)

    st.success("Current session cleared.")