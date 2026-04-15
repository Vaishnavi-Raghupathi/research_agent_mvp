import os
import streamlit as st
from main import run_pipeline
from agent.summarizer import ask_question

st.set_page_config(page_title="Research Agent", layout="wide")

st.title("Research Agent")

uploaded_file = st.file_uploader("Upload a research paper (PDF)", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    temp_file_path = os.path.join("/tmp", uploaded_file.name)
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with st.spinner("Processing..."):
        try:
            result = run_pipeline(temp_file_path)

            if result["errors"]:
                st.error(str(result["errors"]))
            else:
                st.success("Pipeline executed successfully!")

                # Display the notebook download button
                if result.get("notebook_path") and os.path.exists(result["notebook_path"]):
                    with open(result["notebook_path"], "rb") as f:
                        st.download_button(
                            label="Download Generated Notebook",
                            data=f,
                            file_name="output_notebook.ipynb",
                            mime="application/octet-stream"
                        )
                else:
                    # Create a simple .ipynb file with summary and code
                    import json
                    notebook_content = {
                        "cells": [
                            {
                                "cell_type": "markdown",
                                "metadata": {},
                                "source": ["# Summary\n", result.get("summary", "No summary available.")]
                            },
                            {
                                "cell_type": "code",
                                "execution_count": None,
                                "metadata": {},
                                "outputs": [],
                                "source": [result.get("code", "# No code generated.")]
                            }
                        ],
                        "metadata": {},
                        "nbformat": 4,
                        "nbformat_minor": 5
                    }
                    notebook_path = "/tmp/generated_notebook.ipynb"
                    with open(notebook_path, "w") as f:
                        json.dump(notebook_content, f)
                    with open(notebook_path, "rb") as f:
                        st.download_button(
                            label="Download Simple Notebook",
                            data=f,
                            file_name="generated_notebook.ipynb",
                            mime="application/octet-stream"
                        )

                # Display the summary
                if result.get("summary"):
                    st.subheader("Summary")
                    st.write(result["summary"])

                # Display the generated code in a code block
                if result.get("code"):
                    st.subheader("Generated Code")
                    st.code(result["code"], language="python")

                # Add 'Ask a Question' feature
                question = st.text_input("Ask a question about the paper")
                if st.button("Get Answer"):
                    if question:
                        try:
                            answer = ask_question(result["text"], question)
                            st.subheader("Answer")
                            st.write(answer)
                        except Exception as e:
                            st.error(str(e))
        except Exception as e:
            st.error(str(e))
