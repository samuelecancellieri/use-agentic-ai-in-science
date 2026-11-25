# Scientific Helper Tools Reference (`tools/`)

All helper tools are lightweight, standalone Python CLIs designed to be invoked either directly by a researcher or autonomously by an AI coding agent.

| Tool | Purpose | Example Command |
|---|---|---|
| [`tools/lit_search.py`](../tools/lit_search.py) | Query Europe PMC (PubMed/PMC) REST API; export JSON, Markdown tables, and BibTeX | `uv run python tools/lit_search.py --query "BRAF melanoma PI3K" --limit 10 --bibtex refs.bib` |
| [`tools/verify_citations.py`](../tools/verify_citations.py) | Verify every `@citekey` in a `.qmd` manuscript exists in `.bib` and resolves via CrossRef API | `uv run python tools/verify_citations.py --bib example-study/06_manuscript/references.bib --qmd example-study/06_manuscript/manuscript.qmd` |
| [`tools/notebooklm_prep.py`](../tools/notebooklm_prep.py) | Bundle hypotheses, analysis summaries, provenance, and manuscript prose for NotebookLM | `uv run python tools/notebooklm_prep.py --study-dir example-study --out-dir example-study/05_notebooklm/packet` |
| [`tools/gdrive_sync.py`](../tools/gdrive_sync.py) | Compute SHA-256 data manifests and push/pull unpublished data, results, and drafts with Google Drive (`gdrive` CLI or `rclone`) | `uv run python tools/gdrive_sync.py manifest --local example-study/02_data/raw --out example-study/02_data/raw_manifest.json` |
| [`tools/figure_qa.py`](../tools/figure_qa.py) | Automated QA gate for publication figures (≥ 300 DPI, print dimensions, non-blank, `.svg`/`.pdf` vector pair) | `uv run python tools/figure_qa.py example-study/04_figures/output` |
| [`tools/memory_store.py`](../tools/memory_store.py) | Mnemosyne-inspired local SQLite + FTS5 scientific memory with evidence pointers, trust tiers & cascading superseding | `uv run python tools/memory_store.py recall --query "pseudobulk"` |
