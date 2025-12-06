import sys, os

# Make sure Python can find the 'agent' package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.pdf_extraction import extract_pdf
from agent.summarizer import summarize_text
from agent.eq_extractor import structure_equations

print("RUNNING DAY 3 PIPELINE...\n")

# Path to your sample PDF
pdf_path = "data/sample_papers/blackbox_FMM (2).pdf"

# STEP 1 — Extract PDF
print("--- STEP 1: Extract PDF ---\n")
pdf = extract_pdf(pdf_path)

text = pdf["text"]
raw_eqs = pdf["equations"]

print("Extracted text length:", len(text))
print("Equation candidates found:", len(raw_eqs))
print("\nTEXT PREVIEW:\n", text[:500])

# STEP 2 — Summarize
print("\n--- STEP 2: Summary ---\n")
summary = summarize_text(text)
print(summary)

# STEP 3 — Structure equations
print("\n--- STEP 3: Structured Equations ---\n")
structured = structure_equations(raw_eqs)

for eq in structured[:5]:
    print(eq)
