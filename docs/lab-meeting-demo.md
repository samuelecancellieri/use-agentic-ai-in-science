# Lab Meeting Live Demo Guide (15–20 Minutes)

Use this presenter playbook to demonstrate an **agent-native scientific research workflow** to your colleagues in a lab meeting. Every step below is reproducible, fast, and designed to answer the two biggest questions scientists ask about AI:
1. *"How do I stop the AI from hallucinating citations or p-hacking my data?"*
2. *"Where do my large datasets, PDFs, and unpublished manuscript drafts live?"*

---

## Pre-Meeting Checklist (2 Minutes)

- [ ] Open this repository in your AI coding workspace (Antigravity, Claude Code, Cursor, or Gemini CLI).
- [ ] Open your linked **Google Drive** folder (`use-agentic-ai-in-science/`) in a browser tab.
- [ ] (Optional) Open a **NotebookLM** notebook pre-loaded with the generated files from `example-study/05_notebooklm/packet/`.
- [ ] Confirm tests pass: `uv run pytest`.

---

## Demo Script (6 Segments)

### 1. The Architecture & Guardrails (2 min)
- Open [`AGENTS.md`](../AGENTS.md) and `.agents/skills/`.
- **Talking point**: *"Instead of pasting snippets into a chat window, we give the AI agent a strict scientific constitution (`AGENTS.md`) and modular skills (`hypothesis-generation`, `data-analysis`, `figure-design`, `manuscript-writing`, `research-ops`). Every stage has a Human-in-the-Loop checkpoint where the scientist—not the AI—makes the scientific call."*
- Show the **Git vs. Google Drive split**:
  - **GitHub (Public / Version-Controlled)**: Code, skills, Quarto manuscript source, verified BibTeX, SHA-256 data manifests.
  - **Google Drive (Private / Unpublished)**: Raw & processed datasets, literature PDFs, NotebookLM source packets, intermediate results, and working manuscript drafts.

### 2. Grounded Literature Search & Pre-Registered Hypotheses (3 min)
- Run live in the terminal:
  ```bash
  uv run python tools/lit_search.py \
    --query "MAPK PI3K dual inhibition melanoma" \
    --limit 5
  ```
- Show [`example-study/01_hypothesis/hypothesis_log.md`](../example-study/01_hypothesis/hypothesis_log.md).
- **Talking point**: *"The agent never relies on memory for citations. It queries Europe PMC live, records testable predictions and falsification criteria BEFORE running confirmatory statistics, and prevents silent HARKing."*

### 3. Reproducible Data Analysis & Provenance (3 min)
- Run live:
  ```bash
  uv run python example-study/02_data/generate_dataset.py
  uv run python example-study/03_analysis/run_analysis.py
  ```
- Open [`example-study/03_analysis/analysis_summary.md`](../example-study/03_analysis/analysis_summary.md).
- **Talking point**: *"One command runs QC (including housekeeping negative controls), PCA, Welch's t-tests with BH-FDR correction, pathway over-representation, 4-parameter Hill IC50 fits, and Bliss drug synergy—and writes an exact `analysis_summary.md` plus `provenance.json` with SHA-256 checksums of every input file."*

### 4. Publication-Grade Multi-Panel Figures + Automated QA (3 min)
- Run live:
  ```bash
  uv run python example-study/04_figures/make_figures.py
  uv run python tools/figure_qa.py example-study/04_figures/output
  ```
- Open `example-study/04_figures/output/fig1_transcriptomic_landscape.png` and `fig2_synergy_viability.png`.
- **Talking point**: *"Because the agent follows `figure-design/SKILL.md`, it uses colorblind-safe Okabe-Ito palettes, plots individual replicate points alongside fitted curves, exports both 300-DPI PNG and lossless SVG, and runs an automated QA gate."*

### 5. NotebookLM + Google Drive Integration (4 min)
- Run live:
  ```bash
  uv run python tools/notebooklm_prep.py \
    --study-dir example-study \
    --out-dir example-study/05_notebooklm/packet
  ```
- Switch to your **Google Drive** tab (`use-agentic-ai-in-science/`) showing the organized folders (`01_sources_and_literature`, `02_raw_and_processed_data`, `03_analysis_and_results`, `04_manuscript_drafts`).
- **Talking point**: *"Unpublished data, intermediate results, and working manuscript drafts stay in Google Drive—not Git. With one command we also package our hypotheses, analysis summary, and draft into clean Markdown files ready for NotebookLM to cross-check claims against PDFs or generate a 10-minute Audio Overview."*

### 6. Quarto Manuscript & Zero-Hallucination Citation Audit (3 min)
- Open [`example-study/06_manuscript/manuscript.qmd`](../example-study/06_manuscript/manuscript.qmd) and [`peer_review_checklist.md`](../example-study/06_manuscript/peer_review_checklist.md).
- Run live:
  ```bash
  uv run python tools/verify_citations.py \
    --bib example-study/06_manuscript/references.bib \
    --qmd example-study/06_manuscript/manuscript.qmd
  ```
- **Talking point**: *"Every single `@citekey` in the Quarto manuscript is verified against `references.bib` and resolved live against the CrossRef API—guaranteeing zero fabricated references. And before we submit, the agent runs an adversarial Reviewer 1 & Reviewer 2 simulation."*

---

## Live Prompts You Can Type During Q&A

If a colleague asks *"Can the agent actually modify the analysis on the fly?"*, try one of these live:
1. **Exploratory check**: *"Using `.agents/skills/data-analysis/SKILL.md`, run an exploratory check on `Oxidative_Phosphorylation` across all treatment arms and report mean log2FC and BH-FDR without altering the pre-registered results."*
2. **Figure tweak**: *"Update Figure 2B to also annotate the mean mid-range Bliss excess (`+0.341`), re-render PNG+SVG, and run `tools/figure_qa.py`."*
3. **Reviewer prep**: *"Read `example-study/06_manuscript/manuscript.qmd` and draft a concise point-by-point rebuttal to Reviewer 2's comment on negative-binomial GLMs."*
