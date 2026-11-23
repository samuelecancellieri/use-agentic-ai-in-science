---
name: hypothesis-generation
description: Formulate falsifiable, literature-grounded scientific hypotheses, experimental designs, and pre-analysis plans before touching confirmatory data.
---

# Hypothesis Generation & Literature Synthesis Skill

Use this skill at **Stage 1** of a scientific project to move from a broad research question to falsifiable, testable hypotheses grounded in peer-reviewed literature.

## Workflow

1. **Scope the Research Question**
   - Define the biological/scientific system, perturbation or exposure, primary outcome, and expected mechanism.
   - Use structured frameworks where applicable (e.g., **PICO** for clinical/translational studies, **Perturbation-Readout-Mechanism** for molecular biology).

2. **Grounded Literature Retrieval (No Memory-Only Citations)**
   - Run `uv run python tools/lit_search.py --query "<your query>" --limit 15 --out 01_hypothesis/lit_results.json` to retrieve real papers from Europe PMC / OpenAlex.
   - Optionally export PDFs or abstracts into a NotebookLM notebook using `tools/notebooklm_prep.py` to interrogate contradictions, methodological gaps, and consensus mechanisms across papers.

3. **Build a Literature Synthesis Matrix**
   - Document in `01_hypothesis/literature_synthesis.md`:
     - Study (Author, Year, DOI)
     - Model system & sample size
     - Key finding
     - Methodological limitation or unresolved gap

4. **Draft a Structured Hypothesis Card (`01_hypothesis/hypothesis_log.md`)**
   For each hypothesis (`H1`, `H2`, ...), explicitly state:
   - **Rationale**: Mechanism supported by cited literature.
   - **Testable Prediction**: Quantitative direction and measurable endpoint (e.g., `|log2FC| >= 1.0`, `FDR < 0.05`).
   - **Null Hypothesis ($H_0$)**: What the data look like if the mechanism is absent.
   - **Falsification Criterion**: Exact empirical result that would refute the hypothesis.
   - **Confounders & Controls**: Batch effects, vehicle controls, off-target toxicity, biological replicates.
   - **Status**: `Pre-registered` (before analysis) vs. `Exploratory` (post-hoc).

5. **Human-in-the-Loop Checkpoint (Gate 1)**
   - Present the hypothesis card and literature gaps to the researcher.
   - Do **not** proceed to confirmatory statistical testing until the researcher confirms or refines the hypotheses.
