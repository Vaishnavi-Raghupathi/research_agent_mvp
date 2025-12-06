"""
Day 7 Pipeline - Perplexity API Only Version
Text-based equation extraction (no Claude Vision needed)
"""
import os
import pathlib
from dotenv import load_dotenv

# Load environment
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

print("\n" + "="*70)
print("RESEARCH PAPER → CODE PIPELINE (PERPLEXITY VERSION)")
print("="*70 + "\n")

pdf_path = "data/sample_papers/blackbox_FMM (2).pdf"

try:
    # Step 1: Extract PDF with text-based method
    print("--- Step 1/6: Extracting PDF Content ---")
    from agent.pdf_extraction import extract_pdf, extract_equations_from_text
    
    pdf_result = extract_pdf(pdf_path)
    text = pdf_result["text"]
    
    print(f"✓ Extracted {len(text)} characters from PDF")
    print(f"✓ Processed {len(pdf_result.get('pages', []))} pages")

    # Step 2: Extract equations using text-based method
    print("\n--- Step 2/6: Extracting Equations (Text-Based) ---")
    equations = extract_equations_from_text(text)
    
    print(f"✓ Found {len(equations)} equation candidates")
    
    if equations:
        print("\n📐 Top 5 equations by confidence:")
        for i, eq in enumerate(equations[:5], 1):
            conf = eq.get('confidence', 0)
            cleaned = eq.get('cleaned', '')[:70]
            print(f"  {i}. [Score: {conf}/10] {cleaned}...")
    else:
        print("⚠️ No equations extracted - PDF may have complex formatting")

    # Step 3: Generate summary
    print("\n--- Step 3/6: Generating Summary ---")
    from agent.summarizer import summarize_text
    
    summary = summarize_text(text)
    print(f"✓ Summary generated ({len(summary)} characters)")

    # Step 4: Generate implementation code
    print("\n--- Step 4/6: Generating Code Implementation ---")
    from agent.code_runner import run_code_agent_loop
    
    final_code = run_code_agent_loop(summary, equations, max_iters=5)
    
    if final_code is None:
        print("⚠️ Code generation failed - using placeholder")
        final_code = """# Code generation failed
# Please review the summary and equations, then implement manually

import numpy as np

# TODO: Implement core algorithms based on paper
"""
    else:
        print("✓ Code generated and validated")

    # Step 5: Generate visualization code
    print("\n--- Step 5/6: Generating Visualizations ---")
    from agent.plot_suggester import suggest_plots
    
    try:
        plot_code = suggest_plots(summary, equations)
        print("✓ Visualization code generated")
    except Exception as e:
        print(f"⚠️ Plot generation failed: {e}")
        print("  Using fallback plots...")
        plot_code = """
import matplotlib.pyplot as plt
import numpy as np

# Fallback: Complexity comparison plot
plt.figure(figsize=(10, 6))
N = np.logspace(1, 5, 50)
plt.loglog(N, N, label='O(N) - FMM', linewidth=2, color='green')
plt.loglog(N, N * np.log(N), label='O(N log N)', linewidth=2, linestyle='--', color='orange')
plt.loglog(N, N**2, label='O(N²) - Direct', linewidth=2, linestyle=':', color='red')
plt.xlabel('Number of Particles (N)', fontsize=12)
plt.ylabel('Computational Cost', fontsize=12)
plt.title('Algorithm Complexity Comparison', fontsize=14, fontweight='bold')
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
"""

    # Step 6: Execute plots
    print("\n--- Step 6/6: Rendering Plots ---")
    from agent.plot_executor import execute_multiple_plots
    
    plot_paths = execute_multiple_plots(plot_code)
    
    if plot_paths:
        print(f"✓ Generated {len(plot_paths)} plot(s):")
        for path in plot_paths:
            print(f"  - {os.path.basename(path)}")
    else:
        print("⚠️ No plots were successfully generated")

    # Build final notebook
    print("\n--- Building Final Notebook ---")
    from agent.notebook_packager import build_notebook
    
    nb_path = build_notebook(summary, equations, final_code, plot_paths)
    print(f"✓ Notebook created: {nb_path}")

    # Generate markdown report
    print("\n--- Generating Report ---")
    report_path = "generated_notebooks/pipeline_report.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Pipeline Execution Report\n\n")
        f.write(f"**Date:** {pathlib.Path(nb_path).stem.split('_')[-2:]}\n\n")
        f.write(f"## Input\n")
        f.write(f"- PDF: `{pdf_path}`\n")
        f.write(f"- Pages: {len(pdf_result.get('pages', []))}\n")
        f.write(f"- Extraction method: Text-based (Perplexity API)\n\n")
        
        f.write(f"## Results\n")
        f.write(f"- Equations extracted: {len(equations)}\n")
        f.write(f"- Average confidence: {sum(eq.get('confidence', 0) for eq in equations) / max(len(equations), 1):.1f}/10\n")
        f.write(f"- Code generated: {'✓ Yes' if final_code and len(final_code) > 100 else '✗ No'}\n")
        f.write(f"- Visualizations: {len(plot_paths)}\n\n")
        
        f.write(f"## Extracted Equations\n\n")
        for i, eq in enumerate(equations[:10], 1):
            conf = eq.get('confidence', 0)
            cleaned = eq.get('cleaned', '')
            f.write(f"### {i}. Confidence: {conf}/10\n")
            f.write(f"```\n{cleaned}\n```\n\n")
        
        f.write(f"## Output Files\n")
        f.write(f"- Notebook: `{nb_path}`\n")
        f.write(f"- Plots: {len(plot_paths)} files in `generated_plots/`\n\n")
        
        f.write(f"## Notes\n")
        if len(equations) < 5:
            f.write(f"- ⚠️ Low equation count - consider using Claude Vision API for better extraction\n")
        if any(eq.get('confidence', 0) < 5 for eq in equations):
            f.write(f"- ⚠️ Some low-confidence equations detected\n")
        f.write(f"- 💡 To improve: Add `ANTHROPIC_API_KEY` to `.env` for vision-based extraction\n")
    
    print(f"✓ Report saved: {report_path}")

    # Final summary
    print("\n" + "="*70)
    print("✨ PIPELINE COMPLETE ✨")
    print("="*70)
    
    print(f"\n📊 Summary:")
    print(f"  ├─ Extraction: Text-based (Perplexity API)")
    print(f"  ├─ Equations: {len(equations)} found")
    print(f"  ├─ Code: {'✓ Generated' if final_code and len(final_code) > 100 else '✗ Failed'}")
    print(f"  └─ Plots: {len(plot_paths)} created")
    
    print(f"\n📁 Output:")
    print(f"  ├─ Notebook: {os.path.basename(nb_path)}")
    print(f"  ├─ Report: {os.path.basename(report_path)}")
    print(f"  └─ Plots: generated_plots/")
    
    print(f"\n🎯 Next Steps:")
    print(f"  1. Open notebook: jupyter notebook {nb_path}")
    print(f"  2. Review report: cat {report_path}")
    print(f"  3. Check equations quality")
    print(f"  4. Test generated code")
    
    if len(equations) < 5:
        print(f"\n💡 Tip: For better equation extraction, add Claude API:")
        print(f"   ANTHROPIC_API_KEY=sk-ant-xxx to .env")
        print(f"   Then run: python app/test_pipeline_day7_ultimate.py")

except FileNotFoundError:
    print(f"\n❌ Error: PDF not found at {pdf_path}")
    print("Check the file path and try again.")
    
except Exception as e:
    print(f"\n❌ Pipeline failed: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    
    print(f"\n💡 Troubleshooting:")
    print(f"  1. Check .env has PERPLEXITY_API_KEY")
    print(f"  2. Verify all agent/ files are present")
    print(f"  3. Check PDF path is correct")
    print(f"  4. Try: pip install --upgrade pymupdf nbformat requests")