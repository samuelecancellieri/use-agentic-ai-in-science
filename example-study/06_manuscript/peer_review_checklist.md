# Simulated Peer-Review & Reporting Checklist

This log demonstrates **Stage 4 (Adversarial Peer-Review Simulation)** from `.agents/skills/manuscript-writing/SKILL.md`.

## Automated Pre-Submission Audit

- [x] Every numerical value in `manuscript.qmd` cross-checked against `03_analysis/analysis_summary.md`.
- [x] Every `@citekey` in `manuscript.qmd` verified in `references.bib` and resolved against CrossRef (`tools/verify_citations.py`).
- [x] Every figure verified for ≥ 300 DPI, readable dimensions, and vector `.svg` counterpart (`tools/figure_qa.py`).
- [x] Hypotheses pre-registered prior to confirmatory analysis (`01_hypothesis/hypothesis_log.md`).
- [x] Computational provenance logged with SHA-256 input checksums (`02_data/processed/provenance.json`).

---

## Simulated Reviewer 1 (Cancer Biology & Signaling Specialist)

1. **Major Comment — Cell-Line Diversity & In Vivo Validation**:
   - *Critique*: Findings are demonstrated in a single synthetic melanoma model. Biological generalizability requires testing across multiple BRAF- and NRAS-mutant cell lines plus orthogonal protein-level validation (p-ERK, p-AKT, cleaved PARP).
   - *Resolution*: Explicitly acknowledged in the *Limitations and Next Steps* section of `manuscript.qmd`.
2. **Minor Comment — Pro-Apoptotic Effector Specificity**:
   - *Critique*: Specify canonical BH3-only genes (`BCL2L11`/BIM, `BBC3`/PUMA, `PMAIP1`/NOXA) in Results rather than only reporting pathway totals.
   - *Resolution*: Added explicit gene-level callouts in Results and labeled them directly on Figure 1C.

---

## Simulated Reviewer 2 (Biostatistics & Reproducibility Reviewer)

1. **Major Comment — Count Modeling vs. log2-CPM Welch t-test**:
   - *Critique*: While Welch's $t$-test on $\log_2(\text{CPM}+1)$ with BH-FDR is transparent and fast for a lightweight Python benchmark, real low-count RNA-seq experiments should use negative-binomial GLMs (`DESeq2`/`edgeR`) with shrinkage estimators and explicit batch covariates.
   - *Resolution*: Documented clearly in *Methods* and *Limitations*; batch structure is preserved in `sample_metadata.csv` for users swapping in `pydeseq2` or R/`DESeq2`.
2. **Minor Comment — Synergy Metric Robustness**:
   - *Critique*: Bliss independence assumes independent drug mechanisms; reporting a full dose-response matrix with ZIP or Loewe synergy would strengthen pharmacological claims.
   - *Resolution*: Added as a concrete next step in *Discussion*.
