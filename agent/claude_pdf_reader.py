"""
Use Claude's vision API to extract equations from PDF images.
This is the PROPER way to handle research PDFs with complex math.
"""
import fitz  # PyMuPDF
import base64
import requests
import os
from io import BytesIO

def pdf_pages_to_images(pdf_path, dpi=150):
    """
    Convert PDF pages to images for vision API.
    """
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Render page to image
        mat = fitz.Matrix(dpi/72, dpi/72)  # Zoom factor
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PNG bytes
        img_bytes = pix.tobytes("png")
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        images.append({
            "page": page_num + 1,
            "base64": img_base64,
            "width": pix.width,
            "height": pix.height
        })
    
    doc.close()
    return images


def extract_equations_with_claude(pdf_path, api_key=None, max_pages=5):
    """
    Use Claude's vision API to extract equations from PDF.
    This actually SEES the equations as they appear.
    """
    if api_key is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found. Set it in .env file.")
    
    print(f"Converting PDF pages to images...")
    images = pdf_pages_to_images(pdf_path)
    
    # Limit pages to avoid high costs
    images = images[:max_pages]
    print(f"Processing {len(images)} pages with Claude Vision API...")
    
    all_equations = []
    
    for img_data in images:
        page_num = img_data["page"]
        print(f"  Analyzing page {page_num}...")
        
        # Call Claude with the image
        equations = analyze_page_with_claude(
            img_data["base64"], 
            page_num, 
            api_key
        )
        
        all_equations.extend(equations)
        print(f"    Found {len(equations)} equations")
    
    return all_equations


def analyze_page_with_claude(image_base64, page_num, api_key):
    """
    Send page image to Claude and ask it to extract equations.
    """
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 2000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": """Extract ALL mathematical equations from this page.

For each equation, provide:
1. The equation in LaTeX format
2. A brief description (what it represents)

Format your response EXACTLY like this (one equation per block):

EQUATION:
LaTeX: [the equation in LaTeX]
Description: [brief description]

EQUATION:
LaTeX: [next equation]
Description: [brief description]

Focus on complete, meaningful equations. Skip equation fragments or variable definitions unless they're important."""
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result["content"][0]["text"]
        
        # Parse the response
        equations = parse_claude_equation_response(content, page_num)
        
        return equations
        
    except Exception as e:
        print(f"    Error analyzing page {page_num}: {e}")
        return []


def parse_claude_equation_response(text, page_num):
    """
    Parse Claude's structured response into equation dicts.
    """
    equations = []
    
    # Split by EQUATION: markers
    blocks = text.split("EQUATION:")
    
    for block in blocks[1:]:  # Skip first empty split
        lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
        
        latex = ""
        description = ""
        
        for line in lines:
            if line.startswith("LaTeX:"):
                latex = line.replace("LaTeX:", "").strip()
            elif line.startswith("Description:"):
                description = line.replace("Description:", "").strip()
        
        if latex:
            equations.append({
                "page": page_num,
                "latex": latex,
                "description": description,
                "confidence": 10,  # Claude's extraction is high quality
                "cleaned": latex
            })
    
    return equations


def extract_with_fallback(pdf_path):
    """
    Try Claude vision first, fall back to text extraction if it fails.
    """
    try:
        # Try Claude vision
        print("\n=== Attempting Claude Vision Extraction ===")
        equations = extract_equations_with_claude(pdf_path, max_pages=3)
        
        if equations:
            print(f"✓ Successfully extracted {len(equations)} equations with vision API")
            return equations
        else:
            print("⚠️ Vision API returned no equations")
    
    except Exception as e:
        print(f"⚠️ Claude vision extraction failed: {e}")
    
    # Fallback to text-based extraction
    print("\n=== Falling back to text-based extraction ===")
    from agent.pdf_extraction import extract_pdf, extract_equations_from_text
    
    result = extract_pdf(pdf_path)
    equations = extract_equations_from_text(result["text"])
    
    print(f"✓ Extracted {len(equations)} equations (text-based, lower quality)")
    return equations


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python claude_pdf_reader.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    equations = extract_with_fallback(pdf_path)
    
    print(f"\n=== Results ===")
    print(f"Total equations: {len(equations)}")
    
    print(f"\n=== Sample Equations ===")
    for i, eq in enumerate(equations[:5], 1):
        print(f"\n{i}. [Page {eq.get('page', '?')}] Confidence: {eq.get('confidence', 0)}/10")
        print(f"   LaTeX: {eq.get('latex', eq.get('cleaned', ''))[:100]}")
        if 'description' in eq:
            print(f"   Description: {eq['description']}")