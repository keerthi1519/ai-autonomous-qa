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

if not os.path.exists(HISTORY_FILE):
    st.warning("⚠ No execution history found.")
    st.info("Execute Selenium tests to create execution history.")
    st.stop()

try:
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
except Exception as e:
    st.error("Unable to read history.json")
    st.exception(e)
    st.stop()

if not history:
    st.info("No executions have been recorded yet.")
    st.stop()

# --------------------------------------------------------
# Summary metrics
# --------------------------------------------------------

st.subheader("📈 Summary")

total_runs = len(history)
green_runs = sum(1 for item in history if item.get("status") == "SUCCESS")
total_passed = sum(item.get("passed", 0) for item in history)
total_failed = sum(item.get("failed", 0) for item in history)
pass_rate = (
    100 * total_passed / (total_passed + total_failed)
    if (total_passed + total_failed) > 0
    else 0
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Runs", total_runs)
c2.metric("Green Runs", f"{green_runs}/{total_runs}")
c3.metric("Tests Passed", total_passed)
c4.metric("Overall Pass Rate", f"{pass_rate:.0f}%")

st.divider()

# --------------------------------------------------------
# Trend chart
# --------------------------------------------------------

df = pd.DataFrame(history)

if "passed" in df.columns and len(df) > 1:

    st.subheader("📊 Pass / Fail Trend")

    chart_df = df[["passed", "failed"]].copy()
    chart_df.index = range(1, len(chart_df) + 1)
    st.line_chart(chart_df, color=["#21c354", "#ff4b4b"])

    if "duration_seconds" in df.columns:
        st.subheader("⏱ Run Duration (seconds)")
        dur = df[["duration_seconds"]].copy()
        dur.index = range(1, len(dur) + 1)
        st.bar_chart(dur)

st.divider()

# --------------------------------------------------------
# Full table
# --------------------------------------------------------

st.subheader("📋 All Runs")

st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("🕒 Latest Execution")

st.json(history[-1])

with open(HISTORY_FILE, "rb") as f:
    st.download_button(
        "⬇ Download History (JSON)",
        data=f,
        file_name="history.json",
        mime="application/json",
        use_container_width=True
    )
