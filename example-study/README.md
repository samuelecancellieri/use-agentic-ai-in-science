# Worked Example: Transcriptomic Reprogramming Under Dual MAPK/PI3K Inhibition

This directory demonstrates a complete, reproducible **end-to-end bioinformatics research workflow** powered by agentic AI, Quarto, Google Drive, and NotebookLM.

> **Transparency Note**: To keep this repository lightweight, self-contained, and free of patient-privacy restrictions, the RNA-seq count matrix and dose-response viability measurements are deterministically generated (`seed=42`) by [`02_data/generate_dataset.py`](./02_data/generate_dataset.py) with realistic negative-binomial overdispersion and pathway-level co-regulation. Replace the raw CSVs with your own experimental data (pulled from Google Drive via `tools/gdrive_sync.py`) to adapt this template to a real wet-lab or clinical study.

## Directory Map

| Stage | Folder | Purpose | Published in Git? |
|---|---|---|---|
| 1. Hypothesis | `01_hypothesis/` | Pre-registered hypothesis card & literature synthesis matrix | Yes |
| 2. Data | `02_data/` | Deterministic data generator, SHA-256 manifest, raw & processed CSVs | Scripts & manifest in Git; raw/processed CSVs in Google Drive |
| 3. Analysis | `03_analysis/` | Reproducible QC, log2-CPM normalization, PCA, DE (BH-FDR), ORA, Bliss synergy | Yes (script + summary) |
| 4. Figures | `04_figures/` | Publication-grade multi-panel figures (300 DPI PNG + vector SVG) | Yes (script + figures; also archived to Drive) |
| 5. NotebookLM | `05_notebooklm/` | Curated prompt guide & NotebookLM source packet builder | Guide in Git; generated packet synced to Drive |
| 6. Manuscript | `06_manuscript/` | Quarto (`.qmd`) IMRaD manuscript, verified `references.bib`, peer-review log | Source in Git; rendered DOCX/PDF drafts in Drive |

## Quick Reproduction

```bash
uv run python example-study/02_data/generate_dataset.py
uv run python example-study/03_analysis/run_analysis.py
uv run python example-study/04_figures/make_figures.py
uv run python tools/figure_qa.py example-study/04_figures/output
uv run python tools/notebooklm_prep.py --study-dir example-study --out-dir example-study/05_notebooklm/packet
```
