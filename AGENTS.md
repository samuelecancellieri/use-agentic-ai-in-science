# AGENTS.md — Scientific Research Agent Constitution

This repository is an **agent-native scientific research workspace**. Any AI coding agent operating in this repository (Antigravity, Claude Code, Cursor, Gemini CLI, Codex, etc.) must follow these rules to preserve **scientific integrity, statistical rigor, and full reproducibility**.

---

## 1. Core Scientific Guardrails (Non-Negotiable)

1. **Zero Hallucinated Citations**: Never invent a DOI, PMID, author list, journal, or year. Every citation added to `references.bib` or a manuscript must be retrieved via `tools/lit_search.py` (or provided by the user) and verified with `tools/verify_citations.py`.
2. **Zero Fabricated Numbers**: Every statistic, p-value, fold change, confidence interval, and sample size reported in a manuscript or summary must be programmatically computed from data in `02_data/` by scripts in `03_analysis/` and traceable to `02_data/processed/provenance.json`.
3. **No HARKing or Silent p-Hacking**: Record hypotheses and falsification criteria in `01_hypothesis/hypothesis_log.md` *before* running confirmatory tests. Label any post-hoc analyses explicitly as **exploratory**.
4. **Multiple-Testing Correction**: Whenever testing multiple genes, pathways, or endpoints, always apply and report adjusted p-values (e.g., Benjamini-Hochberg FDR) alongside effect sizes.
5. **Human-in-the-Loop Checkpoints**: Stop and ask the principal investigator (user) for sign-off at major scientific decision gates:
   - Gate 1: Hypothesis & experimental design sign-off
   - Gate 2: QC & statistical model sign-off
   - Gate 3: Figure design & visual narrative sign-off
   - Gate 4: Manuscript claims & citation verification sign-off
6. **Data & Privacy Hygiene**: Never commit raw patient data (PHI/PII), credentials (`credentials.json`, `.env`), or multi-gigabyte sequencing files to Git. Store large datasets in Google Drive (via `tools/gdrive_sync.py`) or institutional storage, and track checksums/manifests in Git.

---

## 2. Modular Agent Skills

Before starting a specialized research stage, read the corresponding skill in `.agents/skills/`:

| Stage | Skill File | When to Use |
|---|---|---|
| 1. Hypothesis & Literature | `.agents/skills/hypothesis-generation/SKILL.md` | Formulating testable hypotheses, literature matrices, and falsification criteria |
| 2. Data Analysis & QC | `.agents/skills/data-analysis/SKILL.md` | Exploratory analysis, normalization, differential testing, enrichment, provenance |
| 3. Plots & Figure Design | `.agents/skills/figure-design/SKILL.md` | Designing publication-ready multi-panel figures (300 DPI PNG + vector SVG) |
| 4. Manuscript Writing | `.agents/skills/manuscript-writing/SKILL.md` | Drafting Quarto (`.qmd`) IMRaD manuscripts, claim checking, simulated peer review |
| 5. Research Ops | `.agents/skills/research-ops/SKILL.md` | Google Drive sync, NotebookLM source packet curation, citation auditing |
| 6. Scientific Memory | `.agents/skills/scientific-memory/SKILL.md` | Mnemosyne-inspired local-first SQLite memory (evidence-backed recall, superseding, audit) |

---

## 3. Available Helper Tools (`tools/`)

Run all Python commands through `uv run python ...` (or the active virtual environment):

- `tools/lit_search.py` — Query Europe PMC & OpenAlex for peer-reviewed literature; export structured JSON/Markdown & BibTeX.
- `tools/verify_citations.py` — Audit `.bib` and `.qmd` files against CrossRef / Europe PMC APIs to guarantee every citation exists.
- `tools/notebooklm_prep.py` — Compile literature notes, hypothesis logs, analysis summaries, and manuscript drafts into clean NotebookLM source packets.
- `tools/gdrive_sync.py` — Sync raw datasets, figures, and rendered manuscripts with Google Drive (`rclone`, `gdrive` CLI, or Google Drive API) with `--dry-run` safety.
- `tools/figure_qa.py` — Verify figure resolution (≥300 DPI), dimensions, vector counterparts (`.svg`/`.pdf`), and non-empty rendering.
- `tools/memory_store.py` — Mnemosyne-inspired local SQLite + FTS5 scientific memory store with trust tiers, evidence links, dependency-cascading superseding, and Markdown export.

---

## 4. Reproducing the Worked Example

```bash
uv sync --extra dev
uv run python example-study/02_data/generate_dataset.py
uv run python example-study/03_analysis/run_analysis.py
uv run python example-study/04_figures/make_figures.py
uv run python tools/figure_qa.py example-study/04_figures/output
uv run python tools/notebooklm_prep.py --study-dir example-study --out-dir example-study/05_notebooklm/packet
uv run pytest
```
