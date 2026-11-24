# Simulated Peer-Review & Reporting Checklist (scRNA-seq Example)

## Automated Pre-Submission Audit

- [x] All statistics in `manuscript.qmd` match `03_analysis/analysis_summary.md` verbatim.
- [x] Every `@citekey` in `manuscript.qmd` verified in `references.bib` and resolved live via CrossRef (`tools/verify_citations.py`).
- [x] Both multi-panel figures verified for ≥ 300 DPI and vector `.svg` pairs (`tools/figure_qa.py`).
- [x] Donor-level pseudobulk used for DE to prevent single-cell pseudoreplication (Squair et al., 2021).

## Simulated Reviewer Comments & Resolutions

1. **Reviewer 1 (Single-Cell Immunology)**: *Clarify how the lightweight PCA embedding maps to standard Scanpy/Seurat UMAP + Leiden workflows.*
   - **Resolution**: Explicitly addressed in *Discussion — Limitations and Scaling to Real Wet-Lab Data*.
2. **Reviewer 2 (Biostatistics)**: *Proportions are simplex-constrained (sum to 1); note compositional alternatives like scCODA or CLR.*
   - **Resolution**: Added explicit note on `scCODA` / CLR transforms in *Discussion*.
