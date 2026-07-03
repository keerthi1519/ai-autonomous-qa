import streamlit as st
import os

st.set_page_config(page_title="AI Autonomous QA", layout="wide")

st.title("🤖 AI Autonomous QA Platform")

st.markdown("---")

st.subheader("Pipeline Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.success("✅ Requirement Analysis")
    st.success("✅ Test Scenarios")

with col2:
    st.success("✅ Test Cases")
    st.success("✅ Selenium Scripts")

with col3:
    st.success("✅ Test Execution")
    st.success("✅ HTML Report")

st.markdown("---")

st.subheader("Project Statistics")

requirements = 1

scenarios = len(st.session_state.get("scenarios", []))

testcases = len(st.session_state.get("testcases", []))

scripts = len(st.session_state.get("scripts", []))

c1, c2, c3, c4 = st.columns(4)

c1.metric("Requirements", requirements)
c2.metric("Scenarios", scenarios)
c3.metric("Test Cases", testcases)
c4.metric("Scripts", scripts)

st.markdown("---")

st.subheader("Latest Execution")

report_exists = os.path.exists("../reports/report.html") or os.path.exists("reports/report.html")

if report_exists:
    st.success("HTML Report Available")
else:
    st.warning("No Report Generated")

st.markdown("---")

st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📄 Requirement Analysis")

with col2:
    st.info("🧪 Execute Tests")

with col3:
    st.info("📊 View Reports")