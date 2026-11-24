# Pre-Registered Hypothesis Log (Single-Cell RNA-seq Study)

- **Study Title**: Single-Cell Transcriptomic Profiling of Tumor-Infiltrating Immune Remodeling Under Anti-PD-1 Checkpoint Blockade
- **Stage**: Gate 1 — Pre-Analysis Registration (logged prior to confirmatory statistical testing)
- **Model System**: Synthetic tumor-infiltrating leukocyte scRNA-seq benchmark ($N = 8$ biological donors: 4 `Control`, 4 `AntiPD1`; 1,200 cells across 5 immune lineages; 500 profiled genes including 10 mitochondrial QC genes)

---

## Hypothesis H1 — Anti-PD-1 Expands Effector CD8+ T Cells and Contracts Exhausted CD8+ T Cells

- **Status**: `Pre-registered`
- **Biological Rationale**: Checkpoint blockade targeting PD-1 reinvigorates antitumor immunity by expanding cytotoxic effector/memory CD8+ T-cell states relative to terminally exhausted T cells (Sade-Feldman et al., 2018).
- **Testable Prediction**:
  1. Across biological donors ($n=4$ per arm), `CD8_T_Effector` cell proportion increases significantly under `AntiPD1` vs. `Control` (donor-level Welch's $t$-test, $p < 0.05$, mean increase $\ge 10$ percentage points).
  2. `CD8_T_Exhausted` proportion decreases correspondingly under `AntiPD1` vs. `Control` ($p < 0.05$).
- **Null Hypothesis ($H_{0,1}$)**: Donor-level proportions of `CD8_T_Effector` and `CD8_T_Exhausted` do not differ between `AntiPD1` and `Control` ($p \ge 0.05$).
- **Falsification Criterion**: H1 is refuted if `CD8_T_Effector` fails to expand or if compositional shifts occur only in a single outlier donor.

---

## Hypothesis H2 — Donor-Level Pseudobulk DE Captures Cytotoxic Reprogramming While Controlling False Discoveries

- **Status**: `Pre-registered`
- **Biological Rationale**: Treating individual cells from the same donor as independent replicates causes severe false-positive inflation (pseudoreplication; Squair et al., 2021). Aggregating UMI counts per donor × lineage (pseudobulk) preserves statistical calibration while detecting genuine transcriptional reprogramming.
- **Testable Prediction**:
  1. Donor-level pseudobulk DE (`AntiPD1` vs. `Control` within the `CD8_T` lineage) significantly upregulates cytotoxic/IFN-$\gamma$ effector genes (`GZMB`, `PRF1`, `IFNG`, `NKG7`; $\text{BH-FDR} < 0.05$, $\log_2\text{FC} \ge 1.0$) and downregulates exhaustion regulators (`TOX`, `LAG3`, `HAVCR2`; $\text{BH-FDR} < 0.05$, $\log_2\text{FC} \le -1.0$).
  2. On null background genes, donor-level pseudobulk maintains a controlled false-positive rate ($\le 5\%$ at $\text{BH-FDR} < 0.05$), whereas naive cell-level testing exhibits substantial false-positive inflation.
- **Null Hypothesis ($H_{0,2}$)**: Pseudobulk DE shows no significant cytotoxic upregulation or exhaustion downregulation in `CD8_T` cells ($\text{BH-FDR} \ge 0.05$).
- **Falsification Criterion**: H2 is refuted if cytotoxic markers fail to pass $\text{BH-FDR} < 0.05$ in pseudobulk analysis or if background null genes exhibit $> 5\%$ false positives under pseudobulk testing.

---

## Quality Control & Analytical Plan

- **Cell-Level QC Filters** (Luecken & Theis, 2019): Retain cells with $\ge 200$ detected genes, $\ge 500$ total UMIs, and $< 15\%$ mitochondrial (`MT-*`) UMI fraction.
- **Normalization & Embedding**: Library-size normalization to CP10K + $\log_1p$, followed by SVD/PCA embedding on highly variable genes.
- **Negative Controls**: `B_Cell` lineage proportion and background null genes monitored for stability across treatment arms.
