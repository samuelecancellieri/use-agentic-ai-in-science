---
name: research-ops
description: Manage Google Drive data/manuscript syncing, NotebookLM source packet preparation, and research provenance hygiene.
---

# Research Operations Skill (Google Drive, NotebookLM & Provenance)

Use this skill to connect your local Git-managed scientific codebase with collaborative research platforms (**Google Drive / Docs / Sheets** and **NotebookLM**).

## 1. Google Drive Integration

Follow the **Code in Git, Heavy Data & Co-Author Drafts in Drive** pattern:
- **Pull raw datasets** from Google Drive into `02_data/raw/` before running analysis.
- **Push publication figures & rendered DOCX/PDF manuscripts** to a shared Google Drive folder for PI and co-author review.
- Always run with `--dry-run` first to verify paths:
  ```bash
  uv run python tools/gdrive_sync.py push \
    --local example-study/04_figures/output \
    --remote gdrive:science-projects/mapk-pi3k-study/figures \
    --dry-run
  ```
- See `docs/google-drive-integration.md` for configuring `rclone`, the `gdrive` CLI, Google Workspace MCP servers, or the Python Google Drive API.

## 2. NotebookLM Workflow

Use **NotebookLM** as a grounded, source-constrained research companion for:
- Deep literature synthesis across 10–50 PDFs without hallucination.
- Cross-checking manuscript claims against your actual analysis summary and cited papers.
- Generating **Audio Overviews** to critique your study narrative while commuting or preparing talks.

Prepare a clean, structured source packet with one command:
```bash
uv run python tools/notebooklm_prep.py \
  --study-dir example-study \
  --out-dir example-study/05_notebooklm/packet
```
Then upload the generated Markdown/PDF files (along with full-text literature PDFs) into a dedicated NotebookLM notebook. See `docs/notebooklm-workflow.md` for curated prompts.

## 3. Provenance & Citation Hygiene

- Before any milestone or manuscript submission, run:
  1. `uv run python tools/verify_citations.py --bib example-study/06_manuscript/references.bib --qmd example-study/06_manuscript/manuscript.qmd`
  2. `uv run python tools/figure_qa.py example-study/04_figures/output`
  3. `uv run pytest`
