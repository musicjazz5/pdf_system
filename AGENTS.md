# Repository Guidelines

## Project Structure & Module Organization
This repository is intentionally small. Core logic lives in [pdf_report_generator.py](/Users/gg/claude_project/roe_analysis_system/pdf_system/pdf_report_generator.py), which contains CSS constants, HTML helper functions, PDF rendering utilities, and the `ReportBuilder` interface. A sample generated file, `示範報告_雙鴻分析.pdf`, shows expected output formatting. There is no dedicated `tests/` or `assets/` directory yet; add new modules beside `pdf_report_generator.py` only when the file becomes hard to maintain.

## Build, Test, and Development Commands
Install dependencies before running the generator:

```bash
python3 -m pip install weasyprint pypdf
python3 pdf_report_generator.py
```

The first command installs the PDF stack. The second builds the sample report through `build_sample_report()`. When developing new report sections, prefer importing `ReportBuilder` in a short local script or REPL session rather than editing the example block repeatedly.

## Coding Style & Naming Conventions
Use Python with 4-space indentation and keep functions focused on one rendering concern. Follow the existing naming pattern:

- `snake_case` for functions and variables, such as `build_html` and `merge_pdfs`
- `PascalCase` for classes, such as `ReportBuilder`
- Uppercase constants for shared styling, such as `BASE_CSS`

Keep HTML helpers pure when possible: accept data, return HTML strings, and avoid hidden filesystem side effects. Match the current tone of short docstrings and readable inline comments.

## Testing Guidelines
There is no automated test suite yet. For now, verify changes by generating a PDF locally and checking:

- the script runs without exceptions
- the output PDF opens correctly
- page counts, layout, and Chinese font rendering remain intact

If you add tests, use `pytest`, place them under `tests/`, and name files `test_*.py`.

## Commit & Pull Request Guidelines
Git history is not available in this workspace, so no repository-specific commit convention can be inferred. Use concise, imperative commit subjects such as `Add valuation summary helper` or `Refactor PDF merge flow`. Pull requests should include a short summary, the commands used for verification, and updated sample output or screenshots when layout changes affect the rendered report.

## Output & Configuration Notes
`build_sample_report()` writes to `/mnt/user-data/outputs` by default. Keep output paths configurable and avoid hard-coding environment-specific directories in new features unless they are exposed as function arguments.
