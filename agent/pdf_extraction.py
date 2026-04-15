"""
Professional PDF extraction with multiple strategies.
Uses PyMuPDF for text, but also tries to preserve structure.
"""
import os
import fitz  # PyMuPDF
import re
from collections import defaultdict

def extract_pdf(path):
    """
    Multi-strategy PDF extraction.
    Returns plain text extracted from the PDF.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file '{path}' does not exist.")

    if not os.access(path, os.R_OK):
        raise PermissionError(f"The file '{path}' cannot be read. Check file permissions.")

    try:
        doc = fitz.open(path)
    except Exception:
        raise ValueError(f"Could not open PDF: {path}")

    plain_text = ""

    for page in doc:
        plain_text += page.get_text() + "\n"

    doc.close()
    return plain_text


def is_equation_block(text):
    """
    Heuristic to detect if a text block might be an equation.
    """
    # Count math indicators
    math_score = 0
    
    # Heavy on symbols
    math_symbols = ['=', '∑', '∫', '∂', '∇', '±', '×', '÷', '≈', '≤', '≥',
                    'α', 'β', 'γ', 'δ', 'θ', 'λ', 'μ', 'σ', 'π', 'ω']
    math_score += sum(3 for s in math_symbols if s in text)
    
    # Has subscripts/superscripts patterns
    if re.search(r'[a-zA-Z]_[a-zA-Z0-9]', text):
        math_score += 2
    if re.search(r'[a-zA-Z]\^[a-zA-Z0-9]', text):
        math_score += 2
    
    # Has function notation
    if re.search(r'[a-zA-Z]\([^)]+\)', text):
        math_score += 1
    
    # Short and symbol-dense
    if len(text) < 100 and len(text.split()) < 15:
        math_score += 2
    
    # Has fraction-like patterns
    if '/' in text or 'frac' in text.lower():
        math_score += 2
    
    # Penalty for prose
    words = re.findall(r'\b[A-Za-z]{5,}\b', text)
    math_score -= len(words)
    
    return math_score >= 5


def extract_equation_blocks(pages):
    """
    Extract equation candidates from structured page blocks.
    """
    equation_candidates = []
    
    for page in pages:
        for block in page["blocks"]:
            if block["type"] == "equation_candidate":
                # Try to clean and format
                cleaned = clean_equation_block(block["text"])
                
                if cleaned and len(cleaned) > 5:
                    equation_candidates.append({
                        "page": page["number"],
                        "text": block["text"],
                        "cleaned": cleaned,
                        "bbox": block["bbox"],
                        "confidence": calculate_equation_confidence(cleaned)
                    })
    
    # Sort by confidence
    equation_candidates.sort(key=lambda x: x["confidence"], reverse=True)
    
    return equation_candidates[:20]  # Top 20


def clean_equation_block(text):
    """
    Clean up equation text.
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common artifacts
    text = re.sub(r'\s*\|\s*\{z\}\s*', '', text)
    text = re.sub(r'\b\d+\s*$', '', text)  # Page numbers at end
    
    # Try to fix broken subscripts/superscripts
    text = re.sub(r'\s+([_^])\s+', r'\1', text)
    
    return text.strip()


def calculate_equation_confidence(text):
    """
    Score equation quality (0-10).
    """
    score = 0
    
    # Has equals sign
    if '=' in text:
        score += 3
    
    # Has summation or integral
    if '∑' in text or '∫' in text or 'sum' in text.lower():
        score += 3
    
    # Has Greek letters
    greek = ['α', 'β', 'γ', 'δ', 'θ', 'λ', 'μ', 'σ', 'π', 'Σ', 'Π']
    score += min(3, sum(1 for letter in greek if letter in text))
    
    # Has subscripts/superscripts
    if '_' in text or '^' in text:
        score += 2
    
    # Has fractions
    if '/' in text or 'frac' in text:
        score += 1
    
    # Reasonable length
    if 10 < len(text) < 150:
        score += 2
    
    # Penalty for too many English words
    words = re.findall(r'\b[A-Za-z]{5,}\b', text)
    score -= min(5, len(words))
    
    return max(0, min(10, score))


def extract_equations_from_text(text):
    """
    Fallback: Extract equations from plain text using patterns.
    More robust than before.
    """
    equations = []
    
    # Pattern 1: Lines with equations (= sign surrounded by math)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip very short or very long
        if len(line) < 10 or len(line) > 300:
            continue
        
        # Must have math content
        if not has_math_content(line):
            continue
        
        # Score it
        confidence = calculate_equation_confidence(line)
        
        if confidence >= 4:  # Threshold
            # Try to get context (line before and after)
            context_before = lines[i-1].strip() if i > 0 else ""
            context_after = lines[i+1].strip() if i < len(lines)-1 else ""
            
            cleaned = clean_equation_block(line)
            
            equations.append({
                "raw": line,
                "cleaned": cleaned,
                "confidence": confidence,
                "context_before": context_before[:50],
                "context_after": context_after[:50]
            })
    
    # Deduplicate
    seen = set()
    unique = []
    for eq in equations:
        key = eq['cleaned']
        if key not in seen and len(key) > 5:
            seen.add(key)
            unique.append(eq)
    
    # Sort by confidence
    unique.sort(key=lambda x: x['confidence'], reverse=True)
    
    return unique[:15]


def has_math_content(text):
    """
    Check if text has mathematical content.
    """
    # Math symbols
    math_symbols = ['=', '∑', '∫', '∂', '∇', '±', '×', '÷', '≈', '≤', '≥']
    if any(s in text for s in math_symbols):
        return True
    
    # Greek letters
    greek = ['α', 'β', 'γ', 'δ', 'θ', 'λ', 'μ', 'σ', 'π']
    if any(letter in text for letter in greek):
        return True
    
    # Function notation with subscripts
    if re.search(r'[a-zA-Z]_[a-zA-Z0-9]', text):
        return True
    
    # Simple equation pattern
    if re.search(r'\b[a-zA-Z]\s*=\s*[^=]', text):
        return True
    
    return False


# Backward compatibility
def extract_pdf_text_only(path):
    """Simple text extraction (legacy)."""
    result = extract_pdf(path)
    return result["text"]


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        result = extract_pdf(pdf_path)
        
        print(f"\n=== PDF Extraction Results ===")
        print(f"Pages: {len(result['pages'])}")
        print(f"Total text: {len(result['text'])} characters")
        print(f"Equation blocks found: {len(result['equation_blocks'])}")
        
        print(f"\n=== Top 5 Equation Blocks ===")
        for i, eq in enumerate(result['equation_blocks'][:5], 1):
            print(f"\n{i}. [Confidence: {eq['confidence']}/10] Page {eq['page']}")
            print(f"   Text: {eq['cleaned'][:100]}...")
        
        print(f"\n=== Text-based Equation Extraction ===")
        text_equations = extract_equations_from_text(result['text'])
        print(f"Found: {len(text_equations)} equations")
        
        for i, eq in enumerate(text_equations[:5], 1):
            print(f"\n{i}. [Confidence: {eq['confidence']}/10]")
            print(f"   {eq['cleaned'][:100]}...")