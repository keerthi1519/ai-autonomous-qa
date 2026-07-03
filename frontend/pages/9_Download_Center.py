import os
import streamlit as st

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

DOWNLOADS = [

    {
        "title": "📄 Uploaded Requirement Documents",
        "path": "uploads"
    },

    {
        "title": "🤖 Generated Selenium Scripts",
        "path": "generated_tests"
    },

    {
        "title": "📊 HTML Test Report",
        "path": "reports/report.html"
    },

    {
        "title": "📜 Execution History",
        "path": "reports/history.json"
    }

]

for item in DOWNLOADS:

    st.subheader(item["title"])

    path = item["path"]

    # ----------------------------------------------------
    # Folder Downloads
    # ----------------------------------------------------

    if os.path.isdir(path):

        files = sorted(os.listdir(path))

        files = [

            file

            for file in files

            if os.path.isfile(
                os.path.join(path, file)
            )

            and not file.endswith(".pyc")

            and "__pycache__" not in file

        ]

        if not files:

            st.info("No files available.")

            st.divider()

            continue

        for file in files:

            filepath = os.path.join(path, file)

            with open(
                filepath,
                "rb"
            ) as f:

                st.download_button(

                    label=f"⬇ Download {file}",

                    data=f.read(),

                    file_name=file,

                    use_container_width=True,

                    key=f"{path}_{file}"

                )

    # ----------------------------------------------------
    # Single File Download
    # ----------------------------------------------------

    elif os.path.isfile(path):

        with open(
            path,
            "rb"
        ) as f:

            st.download_button(

                label=f"⬇ Download {os.path.basename(path)}",

                data=f.read(),

                file_name=os.path.basename(path),

                use_container_width=True,

                key=path

            )

    # ----------------------------------------------------
    # File Not Found
    # ----------------------------------------------------

    else:

        st.warning(f"{path} not found.")

    st.divider()

# ----------------------------------------------------
# Project Summary
# ----------------------------------------------------

st.subheader("📦 Project Artifacts")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Requirement Files",
        len(os.listdir("uploads"))
        if os.path.exists("uploads")
        else 0
    )

with col2:

    st.metric(
        "Generated Tests",
        len(os.listdir("generated_tests"))
        if os.path.exists("generated_tests")
        else 0
    )

with col3:

    st.metric(
        "Reports",
        len(os.listdir("reports"))
        if os.path.exists("reports")
        else 0
    )