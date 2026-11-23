---
name: manuscript-writing
description: Draft, refine, and audit IMRaD scientific manuscripts in Quarto (.qmd) with verified BibTeX citations, claim-to-evidence traceability, and simulated peer review.
---

# Scientific Manuscript Writing & Peer-Review Skill

Use this skill at **Stage 4** to draft a clear, accurate, publication-ready scientific manuscript in Quarto (`.qmd`).

## Workflow

1. **Claim-to-Evidence Table First**:
   - Before writing prose, map every major claim to its exact source: a figure panel (`Figure 1B`), a processed data table (`02_data/processed/de_results.csv`), or a verified citation (`@key`).
   - Read `03_analysis/analysis_summary.md` so every number in the manuscript matches computed outputs verbatim.

2. **Structured IMRaD Drafting (`06_manuscript/manuscript.qmd`)**:
   - **Title & Abstract**: Concise, specific, structured (Background, Methods, Results with key effect sizes, Conclusions).
   - **Introduction**: Known context → specific knowledge gap → explicit study aim and hypotheses (`H1`, `H2`).
   - **Methods**: Sufficiently detailed for independent replication (study design, sample sizes, normalization, statistical tests, multiple-testing correction, software versions, code/data availability).
   - **Results**: Objective reporting of findings in logical order, tied directly to figures and tables, with exact effect sizes, uncertainty, and adjusted p-values. Do not over-interpret in Results.
   - **Discussion**: Interpretation in context of prior literature, mechanistic implications, **explicit limitations** (including synthetic/model constraints), and concrete next experiments.

3. **Citation Verification Gate (Mandatory)**:
   - Run `uv run python tools/verify_citations.py --bib 06_manuscript/references.bib --qmd 06_manuscript/manuscript.qmd`.
   - Fix any unverified DOI, missing citation key, or unused reference before proceeding.

4. **Simulated Adversarial Peer Review**:
   - Act as **Reviewer 1 (Domain Specialist)** and **Reviewer 2 (Statistical & Reproducibility Reviewer)**.
   - Log critiques in `06_manuscript/peer_review_checklist.md` (Major comments, Minor comments, Missing controls, Clarity issues) and address them transparently.

5. **Render & Export**:
   - Render via Quarto (`quarto render 06_manuscript/manuscript.qmd`) to HTML, PDF, or DOCX (which can be uploaded to Google Docs via `tools/gdrive_sync.py` for co-author commenting).

## Human-in-the-Loop Checkpoint (Gate 4)

- Deliver the manuscript draft, citation verification report, and peer-review checklist to the researcher for final scientific sign-off.
