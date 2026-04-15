# Research Agent MVP

Research Agent MVP is a Python-based application designed to assist researchers in processing academic papers. The tool extracts equations, summarizes content, generates runnable Python code, and creates Jupyter Notebooks for further exploration. It supports both PDF uploads and arXiv URLs.

---

## Features

- **PDF and arXiv URL Support**: Process research papers from uploaded PDFs or directly from arXiv links.
- **Text Extraction**: Extracts text and equations from research papers.
- **Summarization**: Generates concise summaries of the paper's content.
- **Code Generation**: Produces Python code based on the paper's methodology and equations.
- **Notebook Packaging**: Creates Jupyter Notebooks with summaries, equations, and generated code.
- **Interactive Q&A**: Allows users to ask questions about the paper's content.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Vaishnavi-Raghupathi/research_agent_mvp.git
   cd research_agent_mvp
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the project root.
   - Add your API keys for Groq and Gemini:
     ```env
     GROQ_API_KEY=your_groq_api_key
     GEMINI_API_KEY=your_gemini_api_key
     ```

---

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app/ui.py
   ```

2. Open the app in your browser (default: `http://localhost:8501`).

3. Upload a PDF or paste an arXiv URL to process a research paper.

4. Explore the generated summary, code, and notebook. Use the Q&A feature to ask questions about the paper.

---

## File Structure

```
research_agent_mvp/
├── agent/
│   ├── arxiv_fetcher.py       # Fetches PDFs from arXiv URLs
│   ├── pdf_extraction.py      # Extracts text and equations from PDFs
│   ├── summarizer.py          # Summarizes paper content
│   ├── codegen.py             # Generates Python code
│   ├── notebook_packager.py   # Creates Jupyter Notebooks
│   └── ...                    # Other utility modules
├── app/
│   ├── ui.py                  # Streamlit app interface
│   └── main.py                # Pipeline orchestration
├── data/                      # Sample data for testing
├── generated_notebooks/       # Auto-generated Jupyter Notebooks
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not included in repo)
├── LICENSE                    # Project license
└── README.md                  # Project documentation
```

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push to your fork.
4. Submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Live Demo

Check out the live demo of the Research Agent MVP:

[Research Agent MVP - Streamlit App](https://researchagentmvp-byc6h2frcyhtctrrrvjxxr.streamlit.app/)
