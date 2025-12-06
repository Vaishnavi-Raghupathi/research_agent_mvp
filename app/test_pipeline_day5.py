import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from agent.pdf_extraction import extract_pdf
from agent.summarizer import summarize_text
from agent.eq_extractor import extract_equations
from agent.codegen import generate_code, fix_code
from agent.code_runner import run_code

PDF_PATH = "data/sample_papers/blackbox_FMM (2).pdf"

print("\nRUNNING DAY 5 PIPELINE...\n")

# --- STEP 1: Extract PDF ---
text = extract_pdf(PDF_PATH)

# --- STEP 2: Summary ---
summary = summarize_text(text)

# --- STEP 3: Equations ---
equations = extract_equations(text)

# --- STEP 4: Generate code ---
code = generate_code(summary, equations)
print("\n--- INITIAL GENERATED CODE ---\n")
print(code[:800], "...\n")

# --- STEP 5: Agentic Correction Loop ---
MAX_ITERS = 5
iteration = 0

while iteration < MAX_ITERS:
    print(f"\n\n### ITERATION {iteration+1} ###\n")
    success, output = run_code(code)

    if success:
        print("CODE RAN SUCCESSFULLY 🎉")
        print(output)
        break

    print("ERROR FOUND:\n", output)

    # Ask LLM to fix the code
    code = fix_code(code, output)
    print("\n--- FIXED CODE ---\n")
    print(code[:800], "...\n")

    iteration += 1

if not success:
    print("\nFAILED AFTER MAX ITERATIONS 💀")
