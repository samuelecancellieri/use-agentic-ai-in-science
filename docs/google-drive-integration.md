# Google Drive Integration Guide

Scientific research generates two fundamentally different kinds of files:
1. **Reproducible Code & Documentation** (scripts, skills, Quarto source, BibTeX, SHA-256 manifests) → **belongs in Git / GitHub**.
2. **Unpublished Data, Literature PDFs, Working Results & Co-Author Manuscript Drafts** (FASTQ/CSV datasets, NotebookLM source packets, intermediate results, rendered DOCX/PDF drafts) → **belongs in Google Drive**.

---

## Recommended Google Drive Folder Structure

```text
Google Drive / use-agentic-ai-in-science/
├── 01_sources_and_literature/    # Primary paper PDFs & NotebookLM source packets
├── 02_raw_and_processed_data/    # Raw & processed CSV/matrix files (gitignored)
├── 03_analysis_and_results/      # Full analysis summaries, provenance.json, high-res figures
└── 04_manuscript_drafts/         # Saved manuscript drafts & rendered DOCX/PDF for co-authors
```

---

## Option 1: Using the `gdrive` CLI (Agent-Native Plugin)

If your agent environment has the official **Google Drive plugin** connected (e.g., Antigravity):

```bash
# 1. Compute a local SHA-256 manifest to commit to Git
uv run python tools/gdrive_sync.py manifest \
  --local example-study/02_data/raw \
  --out example-study/02_data/raw_manifest.json

# 2. Preview upload (safe dry-run)
uv run python tools/gdrive_sync.py push \
  --backend gdrive \
  --local example-study/02_data/raw \
  --folder-id <YOUR_DRIVE_FOLDER_ID> \
  --dry-run

# 3. Upload files to Google Drive
uv run python tools/gdrive_sync.py push \
  --backend gdrive \
  --local example-study/02_data/raw \
  --folder-id <YOUR_DRIVE_FOLDER_ID>
```

---

## Option 2: Using `rclone` (Best for Large Datasets on HPC/Laptops)

1. Install [rclone](https://rclone.org/drive/) and configure a remote named `gdrive` (`rclone config`).
2. Sync folders bidirectionally with checksum verification:
   ```bash
   # Pull raw data from Google Drive
   uv run python tools/gdrive_sync.py pull \
     --backend rclone \
     --remote gdrive:use-agentic-ai-in-science/02_raw_and_processed_data \
     --local example-study/02_data/raw \
     --dry-run

   # Push figures or manuscript exports to Google Drive
   uv run python tools/gdrive_sync.py push \
     --backend rclone \
     --local example-study/04_figures/output \
     --remote gdrive:use-agentic-ai-in-science/03_analysis_and_results \
     --dry-run
   ```

---

## Data Governance & Security Rules

- **Never commit** `credentials.json`, `token.json`, or `.env` to Git.
- **Never upload** un-anonymized human clinical PHI/PII to personal Google Drive accounts; use institutional HIPAA/GDPR-compliant drives.
- Always commit `raw_manifest.json` (SHA-256 checksums) to Git so any collaborator pulling raw data from Google Drive can verify byte-for-byte integrity.
