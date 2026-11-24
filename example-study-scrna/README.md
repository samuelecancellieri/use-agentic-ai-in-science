# Worked Example 2: Single-Cell RNA-seq Immune Remodeling Under Anti-PD-1 Blockade

This directory applies the exact same **6-stage agentic AI scientific workflow** to **single-cell RNA-seq (scRNA-seq)**—highlighting best practices in cell-level QC, marker-based annotation, compositional testing, and **donor-level pseudobulk differential expression** (avoiding single-cell pseudoreplication; Squair et al., 2021).

> **Transparency Note**: As with Example 1, the 1,200-cell × 500-gene UMI count matrix is deterministically simulated (`seed=101`) by [`02_data/generate_dataset.py`](./02_data/generate_dataset.py) across 8 biological donors (4 `Control`, 4 `AntiPD1`) so the entire scRNA-seq pipeline runs in seconds with zero patient-privacy constraints.

## Directory Map

| Stage | Folder | Purpose |
|---|---|---|
| 1. Hypothesis | `01_hypothesis/` | Pre-registered scRNA-seq hypotheses (H1 composition, H2 pseudobulk DE) & verified literature matrix |
| 2. Data | `02_data/` | Deterministic UMI count matrix generator + SHA-256 manifest (`raw/` & `processed/` archived in Google Drive) |
| 3. Analysis | `03_analysis/` | Cell QC (`%MT`, UMI/gene filters), log1p-CP10K normalization, PCA embedding, k-means/marker validation, donor composition, pseudobulk DE vs. naive cell-level DE |
| 4. Figures | `04_figures/` | Publication-grade 300-DPI PNG + SVG figures (QC/Atlas/DotPlot/Composition + Pseudobulk Volcano & Pseudoreplication Audit) |
| 5. NotebookLM | `05_notebooklm/` | NotebookLM source packet builder & prompt guide |
| 6. Manuscript | `06_manuscript/` | Quarto (`.qmd`) IMRaD manuscript, CrossRef-verified `references.bib`, and peer-review checklist |

## Quick Reproduction

```bash
uv run python example-study-scrna/02_data/generate_dataset.py
uv run python example-study-scrna/03_analysis/run_analysis.py
uv run python example-study-scrna/04_figures/make_figures.py
uv run python tools/figure_qa.py example-study-scrna/04_figures/output
uv run python tools/notebooklm_prep.py --study-dir example-study-scrna --out-dir example-study-scrna/05_notebooklm/packet
uv run python tools/verify_citations.py --bib example-study-scrna/06_manuscript/references.bib --qmd example-study-scrna/06_manuscript/manuscript.qmd
```
