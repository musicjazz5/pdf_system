# PDF Report System

This repository contains a Python-based PDF report generator and a Streamlit dashboard for browsing and regenerating research reports.

## What Is Included

- `pdf_report_generator.py`
  Generates styled PDF reports with reusable report-builder components.
- `streamlit_app.py`
  Streamlit dashboard for browsing, filtering, previewing, and downloading reports.
- `requirements.txt`
  Runtime dependencies for the PDF generator and Streamlit app.

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate PDFs

Run the generator:

```bash
python3 pdf_report_generator.py
```

Generated PDFs are written to:

```bash
./outputs/
```

## Run The Streamlit Dashboard

Start the reports dashboard locally:

```bash
source .venv/bin/activate
streamlit run streamlit_app.py
```

If you want to use the same base path as production:

```bash
streamlit run streamlit_app.py --server.port 8503 --server.baseUrlPath reports
```

Then open:

- `http://localhost:8501/` for default Streamlit run
- `http://localhost:8503/reports` for the production-like path

## Current Report Coverage

The generator currently includes:

- Example report output
- U.S. stock comparison reports
- U.S. three-way comparison reports
- Taiwan silicon photonics testing theme report

Examples:

- `Coherent vs Lumentum`
- `Marvell vs Broadcom`
- `Broadcom vs NVIDIA networking`
- `Credo vs Astera Labs`
- `Coherent vs Lumentum vs AAOI`
- `矽光子測試族群個股整理`

## Notes

- `outputs/` is intentionally excluded from git.
- `.venv/` is intentionally excluded from git.
- On macOS, WeasyPrint may depend on system libraries. If Python import fails but the Homebrew `weasyprint` CLI is installed, the generator includes a CLI fallback.

## Repository Structure

```text
.
├── AGENTS.md
├── README.md
├── pdf_report_generator.py
├── requirements.txt
├── streamlit_app.py
└── outputs/
```
