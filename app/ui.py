import streamlit as st

st.title("Research Automation MVP")

uploaded_file = st.file_uploader("Upload a research paper (PDF)", type=["pdf"])

if uploaded_file:
    st.write("File uploaded!")
    # TODO: Send file to backend for processing
