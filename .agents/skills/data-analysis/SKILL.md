---
name: data-analysis
description: Execute reproducible, statistically rigorous exploratory and confirmatory data analysis with automated QC, multiple-testing correction, and provenance logging.
---

# Data Analysis & Statistical Rigor Skill

Use this skill at **Stage 2** to inspect raw data, run quality control, execute pre-specified statistical tests, and emit machine-readable provenance artifacts.

## Non-Negotiable Rules

1. **Deterministic & Scripted**: Every transformation and statistical test must live in a version-controlled script (`03_analysis/`) with fixed random seeds. Never rely on undocumented manual spreadsheet edits.
2. **QC Before Inference**: Always inspect sample-level QC first:
   - Missing values, library sizes / total counts, zero-inflation, duplicate IDs.
   - Unsupervised structure (PCA / hierarchical clustering) to detect outliers or batch effects.
3. **Appropriate Statistical Models**:
   - Report **effect sizes** (e.g., `log2FC`, Cohen's $d$, Bliss excess synergy, $IC_{50}$) alongside **uncertainty** (95% CI or SD/SEM) and **exact p-values**.
   - Always apply multiple-testing correction (Benjamini-Hochberg FDR) when testing families of hypotheses (e.g., genes, pathways).
   - Distinguish clearly between **pre-registered confirmatory tests** and **exploratory analyses**.
4. **Sensitivity & Sanity Checks**:
   - Verify positive controls (known marker genes or reference compounds) behave as expected.
   - Check whether conclusions hold under alternative thresholds or non-parametric tests.
5. **Emit Provenance & Summary**:
   - Write `02_data/processed/provenance.json` containing script path, UTC timestamp, input SHA-256 checksums, package versions, and key parameters.
   - Write `03_analysis/analysis_summary.md` with exact numbers so `06_manuscript/manuscript.qmd` and NotebookLM packets cite identical, verified figures.

## Human-in-the-Loop Checkpoint (Gate 2)

- Pause after QC and primary modeling to review outlier decisions, normalization choices, and statistical assumptions with the researcher before generating final publication figures.
