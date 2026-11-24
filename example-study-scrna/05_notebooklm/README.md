# NotebookLM Source Packet (Single-Cell RNA-seq Example)

Compile your single-cell hypothesis log, literature synthesis, QC/pseudobulk analysis summary, provenance metadata, and Quarto manuscript draft into NotebookLM-ready Markdown files:

```bash
uv run python tools/notebooklm_prep.py \
  --study-dir example-study-scrna \
  --out-dir example-study-scrna/05_notebooklm/packet
```

Upload the generated `01_*.md`–`03_*.md` files alongside primary scRNA-seq PDFs (`Sade-Feldman 2018`, `Luecken & Theis 2019`, `Squair 2021`) into a NotebookLM notebook to audit claims, check statistical assumptions, or generate an Audio Overview.
