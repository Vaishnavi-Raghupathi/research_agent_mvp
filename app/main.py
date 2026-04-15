import sys
import os
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.pdf_extraction import extract_pdf
from agent.eq_extractor import extract_equations
from agent.summarizer import summarize_text
from agent.codegen import generate_code
from agent.code_runner import execute_code_in_sandbox
from agent.plot_executor import execute_plot_code
from agent.notebook_packager import build_notebook

def retry_summarization(text):
    return summarize_text(text)  # Pass the extracted text instead of the file path

def run_pipeline(pdf_path: str) -> dict:
    errors = []
    warnings = []  # New list for non-critical issues
    summary = ""
    equations = []
    plot_paths = []
    notebook_path = ""

    try:
        text = extract_pdf(pdf_path)
        if isinstance(text, dict):
            text = text.get('text', '') or text.get('content', '') or str(text)
        text = str(text) if text else ""
        if not text:
            errors.append("PDF extraction returned no text.")
    except RuntimeError as e:
        errors.append(str(e))
        return {"summary": summary, "equations": equations, "notebook_path": notebook_path, "plot_paths": plot_paths, "errors": errors, "warnings": warnings}

    try:
        equations = extract_equations(text)
    except Exception as e:
        warnings.append(f"Equation extraction failed: {e}")  # Changed to warning

    try:
        summary = retry_summarization(text)
        if summary is None:
            warnings.append("Summarization failed.")  # Changed to warning
    except Exception as e:
        warnings.append(f"Summarization failed: {e}")  # Changed to warning

    try:
        code = generate_code(summary, equations, text)  # Pass the full text as an additional parameter
    except Exception as e:
        errors.append(f"Code generation failed: {e}")
        return {"summary": summary, "equations": equations, "notebook_path": notebook_path, "plot_paths": plot_paths, "errors": errors, "warnings": warnings}

    try:
        success, output = execute_code_in_sandbox(code)
        if not success:
            warnings.append(f"Code execution failed: {output}")  # Changed to warning
    except Exception as e:
        warnings.append(f"Code execution error: {e}")  # Changed to warning

    try:
        plot_code = ""  # Replace with actual plot code extraction logic
        plot_path, error = execute_plot_code(plot_code)
        if error:
            warnings.append(f"Plot execution failed: {error}")  # Changed to warning
        else:
            plot_paths.append(plot_path)
    except Exception as e:
        warnings.append(f"Plot execution error: {e}")  # Changed to warning

    try:
        notebook_path = os.path.abspath("output_notebook.ipynb")
        build_notebook(summary, equations, code, plot_paths)
    except Exception as e:
        errors.append(f"Notebook packaging failed: {e}")

    return {"summary": summary, "equations": equations, "code": code, "notebook_path": notebook_path, "plot_paths": plot_paths, "errors": errors, "warnings": warnings, "text": text}
