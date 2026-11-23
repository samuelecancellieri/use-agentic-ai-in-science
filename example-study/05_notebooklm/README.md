# NotebookLM Source Packet & Research Prompts

This folder connects the local Git/Python research workflow with **Google NotebookLM**.

## 1. Generate the Source Packet

Run the helper CLI to compile your hypothesis log, literature synthesis, statistical analysis summary, provenance metadata, and clean manuscript draft into NotebookLM-optimized Markdown files:

```bash
uv run python tools/notebooklm_prep.py \
  --study-dir example-study \
  --out-dir example-study/05_notebooklm/packet
```

The generated `packet/` directory is gitignored (so you can regenerate it anytime or archive it to Google Drive) and contains:
- `01_hypothesis_and_literature.md`
- `02_analysis_and_provenance.md`
- `03_manuscript_draft.md`
- `04_notebooklm_prompts.md`
- `notebooklm_manifest.json`

## 2. Upload to NotebookLM

1. Create a new notebook in [NotebookLM](https://notebooklm.google.com/) (e.g., `MAPK-PI3K Dual Inhibition Study`).
2. Upload the generated `01_*.md`, `02_*.md`, and `03_*.md` files (or select them directly from your synced Google Drive folder!).
3. Upload full-text PDFs of the cited primary papers (`Villanueva 2010`, `Sos 2009`, `Posch 2013`, `Shi 2014`).
4. Paste prompts from `04_notebooklm_prompts.md` to audit claims, detect literature contradictions, simulate Reviewer 2, or generate an Audio Overview for seminar prep.

See [`docs/notebooklm-workflow.md`](../../docs/notebooklm-workflow.md) for the complete guide.
