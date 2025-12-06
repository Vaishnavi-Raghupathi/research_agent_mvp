from agent.pdf_extraction import extract_pdf, extract_equations_from_text
from agent.summarizer import summarize_text
from agent.code_runner import run_code_agent_loop
from agent.notebook_packager import build_notebook
import os
import pathlib
from dotenv import load_dotenv

# Load environment variables at the start of the execution script
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

pdf_path = "data/sample_papers/blackbox_FMM (2).pdf"

print("\nRUNNING DAY 6 PIPELINE (IMPROVED)...\n")

# 1. Extract PDF with better equation handling
print("--- Extracting PDF ---")
pdf_result = extract_pdf(pdf_path)
text = pdf_result["text"]
print(f"Extracted {len(text)} characters")

# 2. Summarize
print("--- Summarizing ---")
summary = summarize_text(text)

# 3. Extract equations using the improved method
print("--- Extracting Equations (Improved) ---")
equations = extract_equations_from_text(text)
print(f"Found {len(equations)} high-confidence equation candidates.")

# Show top equations
if equations:
    print("\nTop 5 equations by confidence:")
    for i, eq in enumerate(equations[:5], 1):
        print(f"  {i}. [Score: {eq['confidence']}] {eq['cleaned'][:80]}...")

# 4. Agent loop to produce runnable Python
print("\n--- Generating & Fixing Code ---")
final_code = run_code_agent_loop(summary, equations)

if final_code is None:
    print("Pipeline failed: Could not generate runnable code after max iterations.")
    exit()

# 5. Package into notebook
print("--- Building Notebook ---")
nb_path = build_notebook(summary, equations, final_code)

print(f"\n✨ DAY 6 COMPLETE ✨")
print(f"Notebook saved at: {nb_path}")
print("\nNext steps:")
print("  1. Open the notebook and review the equations")
print("  2. Verify the code implementation")
print("  3. Test with your own data")