# Use Agentic AI in Science 🧬🤖

An **open-source teaching repository & reference workspace** demonstrating how to conduct rigorous, reproducible scientific research with **agentic AI**—from pre-registered hypothesis generation and literature synthesis to statistical analysis, publication-grade figure design, NotebookLM cross-checking, Google Drive data management, and Quarto manuscript writing.

Designed to work seamlessly with any AI coding agent (**Antigravity**, **Claude Code**, **Cursor**, **Gemini CLI**, **Codex**) and ready to present in a **15–20 minute lab meeting demo** (see [`docs/lab-meeting-demo.md`](./docs/lab-meeting-demo.md)).

---

## Why This Architecture?

Most scientists start using AI by pasting text into a chat box—which quickly leads to hallucinated citations, untracked data transformations, and irreproducible plots. This repository demonstrates an **agent-native scientific workspace** built on four principles:

1. **Scientific Constitution ([`AGENTS.md`](./AGENTS.md))**: Explicit guardrails prohibiting fabricated citations, silent p-hacking, or unverified numbers, with mandatory **Human-in-the-Loop (HITL)** sign-off gates.
2. **Modular Research Skills ([`.agents/skills/`](./.agents/skills/))**: Reusable playbooks for hypothesis generation, statistical analysis, publication figure design, Quarto manuscript writing, and research operations.
3. **Deterministic Helper Tools ([`tools/`](./tools/))**: Standalone Python CLIs that ground the agent in real APIs (Europe PMC, CrossRef), enforce figure QA (≥ 300 DPI + vector SVG), package sources for **NotebookLM**, and sync unpublished files with **Google Drive**.
4. **Clean Git vs. Google Drive Separation**:
   - **Published in Git**: Code, agent skills, Quarto manuscript source, verified BibTeX, documentation, and SHA-256 data manifests.
   - **Stored in Google Drive (Unpublished)**: Raw/processed datasets, primary literature PDFs, NotebookLM source packets, intermediate analysis results, and saved collaborator manuscript drafts.
5. **Mnemosyne Scientific Memory ([`scientific-memory`](.agents/skills/scientific-memory/SKILL.md) + [`tools/memory_store.py`](tools/memory_store.py))**: Local-first SQLite + FTS5 memory across sessions with mandatory evidence pointers, trust tiers (`verified_data`, `peer_reviewed`, `pi_decision`, `exploratory`), and dependency-cascading `supersede` so agents never repeat stale conclusions.

```mermaid
flowchart LR
    A["1. Hypothesis & Literature\nlit_search.py + NotebookLM"] --> B["2. Data & QC\nGoogle Drive + SHA-256 Manifest"]
    B --> C["3. Statistical Analysis\nBH-FDR + ORA + Bliss Synergy"]
    C --> D["4. Publication Figures\n300 DPI PNG + SVG + figure_qa.py"]
    D --> E["5. NotebookLM Audit\nClaim Check + Audio Overview"]
    E --> F["6. Quarto Manuscript\nverify_citations.py + Peer Review"]
```

---

## Worked Example: Dual MAPK/PI3K Inhibition in Melanoma ([`example-study/`](./example-study/))

To make this immediately teachable in a lab meeting, [`example-study/`](./example-study/) walks through a complete, deterministic bioinformatics study (*16 RNA-seq samples across 4 treatment arms + 7-point dose-response viability curves*):

- **H1 (Adaptive Feedback)**: Single-agent `MEKi` suppresses `MAPK_ERK_Signaling` (mean $\log_2\text{FC} = -2.01$, $\text{FDR} = 1.64 \times 10^{-16}$) while triggering compensatory `PI3K_AKT_mTOR_Signaling` upregulation (mean $\log_2\text{FC} = +1.34$, $\text{FDR} = 1.25 \times 10^{-19}$).
- **H2 (Dual-Blockade Synergy)**: Combined `MEKi + PI3Ki` (`Combo`) extinguishes adaptive PI3K signaling, drives coordinated `Cell_Cycle_Proliferation` arrest (mean $\log_2\text{FC} = -2.41$) and `Apoptosis_Stress_Response` induction (mean $\log_2\text{FC} = +2.34$), shifts $IC_{50}$ by `6.4x` (`0.138 µM` vs. `0.878 µM`), and achieves `+0.423` peak Bliss excess synergy.

| Figure 1: Transcriptomic Landscape | Figure 2: Dose-Response & Bliss Synergy |
| :---: | :---: |
| ![Figure 1](example-study/04_figures/output/fig1_transcriptomic_landscape.png) | ![Figure 2](example-study/04_figures/output/fig2_synergy_viability.png) |

---

## Worked Example 2: Single-Cell RNA-seq Immune Remodeling ([`example-study-scrna/`](./example-study-scrna/))

Applies the exact same 6-stage architecture to **single-cell RNA-seq** (*1,200 cells across 8 biological donors: 4 `Control`, 4 `AntiPD1`; 5 immune lineages*):

- **Cell-Level QC & Atlas**: Filters `83` low-UMI / high-`%MT` outliers, retaining `1,117` cells (`93.1%`), validated via canonical marker dot plots (`CD3D`, `CD8A`, `GZMB`, `TOX`, `CD4`, `CD68`, `MS4A1`).
- **H1 (Donor-Level Composition)**: `AntiPD1` expands `CD8+ Effector` T cells (`11.5% → 36.6%`, BH-FDR $= 0.0028$) and contracts `CD8+ Exhausted` T cells (`27.3% → 10.9%`, BH-FDR $= 0.0003$).
- **H2 (Pseudobulk DE vs. Pseudoreplication)**: Donor-level pseudobulk detects cytotoxic activation (`GZMB`, `IFNG`) and exhaustion repression (`TOX`, `LAG3`) while keeping null background FPR at **`0.23%`** vs. **`21.82%`** under naive cell-level testing.

| scRNA Figure 1: QC, Atlas, Dot Plot & Composition | scRNA Figure 2: Pseudobulk DE & Pseudoreplication Audit |
| :---: | :---: |
| ![scRNA Figure 1](example-study-scrna/04_figures/output/fig1_scrna_qc_and_atlas.png) | ![scRNA Figure 2](example-study-scrna/04_figures/output/fig2_pseudobulk_reprogramming.png) |

---

## Quickstart (Reproduce Everything in < 30 Seconds)

Choose your preferred scientific environment manager (**`uv`**, **`conda`/`mamba`**, or **`pixi`**):

- **Option A — `uv` (Recommended, fastest Python lockfile):**
  ```bash
  uv sync --extra dev
  uv run pytest -v
  ```
- **Option B — `conda` / `mamba` (familiar in bioinformatics/HPC):**
  ```bash
  conda env create -f environment.yml   # or: mamba env create -f environment.yml
  conda activate agentic-science
  pytest -v
  ```
- **Option C — `pixi` (fast conda-forge + PyPI lockfile):**
  ```bash
  pixi install
  pixi run reproduce
  pixi run test
  ```

### Run the Full Pipeline (with `uv run`, `pixi run`, or inside `conda activate agentic-science`)

```bash
# 1. Generate deterministic benchmark dataset + SHA-256 manifest
uv run python example-study/02_data/generate_dataset.py

# 3. Run QC, PCA, differential expression (BH-FDR), pathway ORA, Hill IC50 & Bliss synergy
uv run python example-study/03_analysis/run_analysis.py

# 4. Generate publication-grade figures (300 DPI PNG + vector SVG) and run automated QA
uv run python example-study/04_figures/make_figures.py
uv run python tools/figure_qa.py example-study/04_figures/output

# 5. Build a NotebookLM source packet (ready to upload or sync to Google Drive)
uv run python tools/notebooklm_prep.py \
  --study-dir example-study \
  --out-dir example-study/05_notebooklm/packet

# 6. Verify all manuscript citations against references.bib & CrossRef API
uv run python tools/verify_citations.py \
  --bib example-study/06_manuscript/references.bib \
  --qmd example-study/06_manuscript/manuscript.qmd

# 7. (Optional) Initialize local Mnemosyne scientific memory & recall findings
uv run python tools/memory_store.py init
uv run python tools/memory_store.py recall --query "pseudobulk"

# 8. Run automated test suite (covers both Bulk RNA-seq, scRNA-seq & Memory)
uv run pytest -v
```

To render the Quarto manuscript (requires [Quarto](https://quarto.org/)):
```bash
quarto render example-study/06_manuscript/manuscript.qmd --to html
quarto render example-study/06_manuscript/manuscript.qmd --to docx
```

---

## Repository Structure

```text
use-agentic-ai-in-science/
├── AGENTS.md                         # Scientific guardrails & HITL checkpoints for any AI agent
├── CLAUDE.md                         # Companion entrypoint for Claude Code
├── .agents/skills/                   # Modular research skills (hypothesis, analysis, figures, writing, ops)
├── docs/
│   ├── lab-meeting-demo.md           # 15-20 min presenter playbook & live prompts for lab meetings
│   ├── workflow.md                   # 6-stage agentic research lifecycle
│   ├── mnemosyne-memory.md           # Mnemosyne-inspired local-first SQLite scientific memory
│   ├── google-drive-integration.md   # Keeping unpublished data, results & drafts in Google Drive
│   ├── notebooklm-workflow.md        # Literature synthesis, claim auditing & Audio Overviews
│   └── helper-tools-guide.md         # CLI reference for all 6 scientific helper tools
├── tools/
│   ├── lit_search.py                 # Live Europe PMC literature search -> JSON / Markdown / BibTeX
│   ├── verify_citations.py           # CrossRef DOI & Quarto @citekey anti-hallucination auditor
│   ├── notebooklm_prep.py            # Compile clean source packets & prompt banks for NotebookLM
│   ├── gdrive_sync.py                # Google Drive sync (gdrive CLI / rclone) + SHA-256 manifests
│   ├── figure_qa.py                  # Automated DPI, dimension & vector-pair figure QA
│   └── memory_store.py               # Mnemosyne-inspired SQLite + FTS5 auditable scientific memory
├── example-study/                    # Worked Example 1: Bulk RNA-seq + Drug Synergy
├── example-study-scrna/              # Worked Example 2: Single-Cell RNA-seq + Pseudobulk DE
└── tests/test_pipeline.py            # Automated pytest verification suite
```

---

## Guides & Presentations

- **Presenting to your lab?** Start with [`docs/lab-meeting-demo.md`](./docs/lab-meeting-demo.md).
- **Persistent cross-session memory?** See [`docs/mnemosyne-memory.md`](./docs/mnemosyne-memory.md).
- **Setting up Google Drive for unpublished data & drafts?** See [`docs/google-drive-integration.md`](./docs/google-drive-integration.md).
- **Integrating NotebookLM?** See [`docs/notebooklm-workflow.md`](./docs/notebooklm-workflow.md).
- **Exploring the helper CLIs?** See [`docs/helper-tools-guide.md`](./docs/helper-tools-guide.md).
