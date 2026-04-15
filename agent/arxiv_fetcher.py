def fetch_arxiv_pdf(url: str) -> str:
    import requests
    import tempfile
    import re

    arxiv_id = re.search(r'arxiv\.org/(abs|pdf)/([0-9]+\.[0-9]+)', url)
    if not arxiv_id:
        raise ValueError("Invalid arxiv URL. Use format: https://arxiv.org/abs/XXXX.XXXXX")

    paper_id = arxiv_id.group(2)
    pdf_url = f"https://arxiv.org/pdf/{paper_id}"

    response = requests.get(pdf_url, timeout=30)
    if response.status_code != 200:
        raise ValueError(f"Could not download paper: {response.status_code}")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(response.content)
        return f.name