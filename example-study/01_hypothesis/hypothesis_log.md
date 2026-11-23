# Pre-Registered Hypothesis Log

- **Study Title**: Transcriptomic Reprogramming and Synergistic Growth Suppression Under Dual MAPK/PI3K Pathway Inhibition in BRAF-Mutant Melanoma Models
- **Stage**: Gate 1 — Pre-Analysis Registration (logged prior to confirmatory statistical testing)
- **Model System**: Synthetic BRAF-mutant melanoma cell-line benchmark ($n = 4$ biological replicates per arm; 4 arms: `Vehicle`, `MEKi`, `PI3Ki`, `Combo`)

---

## Hypothesis H1 — Adaptive PI3K/AKT Feedback Under Single-Agent MEK Inhibition

- **Status**: `Pre-registered`
- **Biological Rationale**: Single-agent MAPK pathway blockade (`MEKi`) suppresses canonical ERK transcriptional output (`DUSP6`, `SPRY2`, `ETV4`, `ETV5`), but relieves negative feedback loops on receptor tyrosine kinases, triggering compensatory PI3K/AKT/mTOR transcriptional activation (Villanueva et al., 2010; Shi et al., 2014).
- **Testable Prediction**:
  1. `MEKi` vs. `Vehicle` significantly downregulates `MAPK_ERK_Signaling` genes (mean $\log_2\text{FC} \le -1.0$, pathway over-representation $\text{FDR} < 0.05$).
  2. `MEKi` vs. `Vehicle` induces compensatory upregulation of `PI3K_AKT_mTOR_Signaling` transcripts (positive mean $\log_2\text{FC}$, enriched among upregulated DEGs at $\text{FDR} < 0.05$).
- **Null Hypothesis ($H_{0,1}$)**: Single-agent `MEKi` produces no statistically significant enrichment of `PI3K_AKT_mTOR_Signaling` genes among upregulated transcripts ($\text{FDR} \ge 0.05$).
- **Falsification Criterion**: H1 is refuted if `PI3K_AKT_mTOR_Signaling` shows no significant upregulation or shows net downregulation under `MEKi` vs. `Vehicle`.

---

## Hypothesis H2 — Dual MAPK/PI3K Blockade Produces Synergistic Proliferation Arrest and Apoptosis

- **Status**: `Pre-registered`
- **Biological Rationale**: Co-inhibiting PI3K alongside MEK should extinguish adaptive AKT survival signaling, driving deeper suppression of E2F/G2-M cell-cycle regulators (`MKI67`, `CDK1`, `TOP2A`) and activating pro-apoptotic BH3-only effectors (`BCL2L11`/BIM, `BBC3`/PUMA), yielding greater-than-Bliss-additive viability loss (Sos et al., 2009; Posch et al., 2013).
- **Testable Prediction**:
  1. `Combo` vs. `Vehicle` yields strong coordinated downregulation of `Cell_Cycle_Proliferation` and upregulation of `Apoptosis_Stress_Response` ($\text{FDR} < 0.05$).
  2. In viability dose-response assays, `Combo` reduces $IC_{50}$ by $\ge 2$-fold relative to the more potent single agent and achieves positive Bliss excess synergy ($> 0.10$) across mid-range concentrations ($0.1$–$1.0\ \mu\text{M}$).
- **Null Hypothesis ($H_{0,2}$)**: `Combo` viability suppression is equal to or less than Bliss independence (Bliss excess $\le 0$) and does not exceed single-agent `MEKi` suppression of cell-cycle transcripts.
- **Falsification Criterion**: H2 is refuted if mean mid-range Bliss excess $\le 0.05$ or if `Combo` fails to significantly suppress `Cell_Cycle_Proliferation` relative to `MEKi` alone.

---

## Confounders, Controls & Analytical Plan

- **Negative Controls**: DMSO `Vehicle` arm ($n=4$); housekeeping genes (`ACTB`, `GAPDH`, `RPLP0`, `TBP`) monitored for stable expression ($|\log_2\text{FC}| < 0.3$).
- **Quality Control**: Verify library size uniformity, zero missing counts, and clear treatment-arm separation on PCA before running differential expression.
- **Statistical Controls**: Two-sided Welch's $t$-test on $\log_2(\text{CPM} + 1)$ normalized expression with Benjamini-Hochberg FDR correction ($\text{FDR} < 0.05$ and $|\log_2\text{FC}| \ge 1.0$); Fisher's exact test with BH-FDR for pathway over-representation; 4-parameter log-logistic Hill fits for $IC_{50}$.
