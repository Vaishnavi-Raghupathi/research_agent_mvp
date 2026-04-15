import os
import pathlib
import sys

# Make sure `agent/` is importable when running from app/
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from agent.pdf_extraction import extract_pdf
from agent.summarizer import summarize_paper
from agent.codegen import generate_code, fix_code
from agent.notebook_packager import build_notebook


def run_pipeline(pdf_path: str) -> dict:
    result = {
        "text": "",
        "summary": "",
        "equations": [],
        "code": "",
        "notebook_path": None,
        "errors": []
    }

    # Step 1: Extract PDF
    try:
        extracted = extract_pdf(pdf_path)
        result["text"] = extracted["text"]
        result["equations"] = extracted["equations"]
    except Exception as e:
        result["errors"].append(f"PDF extraction failed: {e}")
        return result

    # Step 2: Summarize
    try:
        result["summary"] = summarize_paper(result["text"])
    except Exception as e:
        result["errors"].append(f"Summarization failed: {e}")

    # Step 3: Generate code
    try:
        result["code"] = generate_code(
            summary=result["summary"],
            equations=result["equations"],
            text=result["text"]
        )
    except Exception as e:
        result["errors"].append(f"Code generation failed: {e}")

    # Step 4: Package notebook
    try:
        result["notebook_path"] = build_notebook(
            summary=result["summary"],
            equations=result["equations"],
            final_code=result["code"]
        )
    except Exception as e:
        result["errors"].append(f"Notebook packaging failed: {e}")

    return result