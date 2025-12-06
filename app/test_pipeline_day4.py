# --- FIX IMPORTS: make project root importable ---
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from agent.pdf_extraction import extract_pdf
from agent.summarizer import summarize_text
from agent.eq_extractor import extract_equations
from agent.codegen import generate_code

PDF_PATH = "data/sample_papers/blackbox_FMM (2).pdf"

print("\nRUNNING DAY 4 PIPELINE...\n")

# --- STEP 1: Extract PDF ---
print("--- STEP 1: Extract PDF ---")
text = extract_pdf(PDF_PATH)
print(f"Extracted text length: {len(text)}")

# --- STEP 2: Summary ---
print("\n--- STEP 2: Summary ---")
summary = summarize_text(text)
print(summary[:800], "...")

# --- STEP 3: Extract Equations ---
print("\n--- STEP 3: Equations ---")
equations = extract_equations(text)
print(f"Found {len(equations)} equations")

# --- STEP 4: Code Generation ---
print("\n--- STEP 4: Code Generation ---")
code = generate_code(summary, equations)
print(code[:1000], "...\n")

print("\nDAY 4 COMPLETE 🎉\n")
