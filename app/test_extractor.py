import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.pdf_extraction import extract_pdf

pdf_path = "data/sample_papers/blackbox_FMM (2).pdf"

result = extract_pdf(pdf_path)

print("\n--- CLEANED TEXT (first 500 chars) ---\n")
print(result["text"][:500])

print("\n--- EQUATION CANDIDATES ---\n")
for eq in result["equations"]:
    print(eq)
