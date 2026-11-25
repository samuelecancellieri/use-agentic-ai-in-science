---
name: scientific-memory
description: Maintain auditable, local-first, evidence-grounded long-term scientific memory across sessions using a Mnemosyne-inspired SQLite memory system (working, episodic, semantic, and procedural tiers with dependency-aware superseding).
---

# Scientific Memory Skill (Mnemosyne Architecture)

AI coding sessions normally start from a blank slate: yesterday's QC outlier decision, batch-correction rationale, or failed assay gets forgotten tomorrow. This skill equips the agent with a **Mnemosyne-inspired, local-first, auditable memory layer** (`tools/memory_store.py`) stored in a single local SQLite database (`.memory/mnemosyne.db`)—with zero cloud dependencies and full provenance on every memory.

---

## 1. The Four Scientific Memory Tiers

| Tier | What Belongs Here | Example |
|---|---|---|
| `working` | Active session state, current run parameters, open questions | *"Testing BH-FDR < 0.05 and |log2FC| >= 1.0 on example-study-scrna."* |
| `episodic` | Timestamped lab decisions, failed experiments, reviewer critiques | *"Gate 2 PI sign-off: excluded 83 cells with %MT >= 15% or UMIs < 500."* |
| `semantic` | Durable, evidence-backed scientific findings & literature facts | *"Donor-level pseudobulk reduces null FPR to 0.23% vs 21.82% naive cell-level."* |
| `procedural` | Reusable lab SOPs, HPC/environment quirks, plotting defaults | *"Always export 300 DPI PNG + vector SVG using Okabe-Ito colorblind-safe palette."* |

---

## 2. Mandatory Evidence & Trust Tiers (Scientific Veracity)

Every stored memory MUST declare a `--trust` level and an `--evidence` pointer (file path, DOI, commit hash, or PI decision gate) so no unverified assumption ever masquerades as a confirmed result:

- `verified_data` — Directly computed from a versioned script & provenance log (e.g., `example-study/03_analysis/analysis_summary.md`).
- `peer_reviewed` — Grounded in a verified DOI (e.g., `doi:10.1038/s41467-021-25960-2`).
- `pi_decision` — Explicit researcher / PI sign-off at a Human-in-the-Loop gate.
- `exploratory` — Post-hoc observation or tentative hypothesis; never cite as confirmatory without re-testing.

---

## 3. Session Lifecycle Protocol

1. **Session Start — Recall Before Acting**:
   ```bash
   uv run python tools/memory_store.py recall --query "pseudobulk QC" --limit 5
   ```
   Check active `procedural`, `episodic`, and `semantic` memories before modifying pipelines or drafting text.

2. **Record Key Decisions & Findings**:
   ```bash
   uv run python tools/memory_store.py add \
     --tier semantic \
     --trust verified_data \
     --evidence "example-study-scrna/03_analysis/analysis_summary.md" \
     --tags "scrna,pseudobulk,h2" \
     --content "Donor-level pseudobulk DE in CD8+ T cells keeps null FPR at 0.23% vs 21.82% for naive cell-level testing."
   ```

3. **Supersede & Cascade When Evidence Changes (Never Silently Overwrite)**:
   When a hypothesis is falsified, a dataset is re-sequenced, or a parameter changes, **supersede** the outdated memory instead of deleting it. Use `--cascade` to automatically flag dependent memories as `needs_review`:
   ```bash
   uv run python tools/memory_store.py supersede \
     --id 1 \
     --new-content "Updated donor cohort to n=8 (4 Control, 4 AntiPD1); pseudobulk FPR=0.23%." \
     --evidence "example-study-scrna/02_data/processed/provenance.json" \
     --cascade
   ```

4. **Audit & Export to NotebookLM / Google Drive**:
   ```bash
   uv run python tools/memory_store.py audit
   uv run python tools/memory_store.py export-md --out .memory/memory_digest.md
   ```

---

## 4. Optional Upstream Mnemosyne Integration

For teams wanting vector embeddings, automatic session hooks, or an MCP server across Claude Code / Cursor / Codex, see [`docs/mnemosyne-memory.md`](../../../docs/mnemosyne-memory.md) for connecting the upstream **Mnemosyne** (`mnemosyne-memory` / `mnemosy-ai` MCP) server.
