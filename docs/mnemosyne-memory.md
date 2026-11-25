# Mnemosyne Scientific Memory System

AI coding agents lose session context the moment a chat closes—forgetting yesterday's QC filter rationale, why a donor was excluded, or which statistical model the PI signed off on.

Inspired by **Mnemosyne** (local-first, SQLite-backed, auditable agent memory), this repository ships a **zero-dependency scientific memory layer** ([`tools/memory_store.py`](../tools/memory_store.py)) paired with the [`scientific-memory`](../.agents/skills/scientific-memory/SKILL.md) skill.

---

## Why Mnemosyne Fits Scientific Research

1. **Local-First & Zero-Cloud**: Everything lives in a single SQLite file (`.memory/mnemosyne.db`, gitignored by default)—zero external servers, zero API keys, and sensitive unpublished lab notes never leave your machine.
2. **Tiered Memory**: Separates transient `working` notes, timestamped `episodic` decisions, durable `semantic` findings, and reusable `procedural` lab SOPs.
3. **Evidence & Veracity on Every Record**: `verified_data` and `peer_reviewed` memories **require** an explicit `--evidence` pointer (file path, DOI, or provenance hash) so unverified guesses never harden into "facts."
4. **Non-Destructive Superseding & Dependency Cascade**: When a hypothesis is falsified or a cohort is updated, `supersede --cascade` preserves the historical audit trail and flags dependent memories as `needs_review` so future agent sessions never repeat stale conclusions.

---

## Quickstart with Built-In `tools/memory_store.py`

```bash
# 1. Initialize local SQLite FTS5 memory store
uv run python tools/memory_store.py init

# 2. Record a verified scientific finding
uv run python tools/memory_store.py add \
  --tier semantic \
  --trust verified_data \
  --evidence "example-study-scrna/03_analysis/analysis_summary.md" \
  --tags "scrna,pseudobulk,h2" \
  --content "Donor-level pseudobulk DE in CD8+ T cells keeps null FPR at 0.23% vs 21.82% naive cell-level."

# 3. Record a dependent procedural rule
uv run python tools/memory_store.py add \
  --tier procedural \
  --trust pi_decision \
  --evidence "Gate 2 Lab Meeting Sign-off" \
  --tags "scrna,sop" \
  --depends-on "1" \
  --content "Always use donor-level pseudobulk aggregation for multi-donor scRNA-seq DE."

# 4. Recall memories in a future session
uv run python tools/memory_store.py recall --query "pseudobulk FPR"

# 5. Export active memories to Markdown for NotebookLM or Google Drive
uv run python tools/memory_store.py export-md --out .memory/memory_digest.md
```

---

## Upgrading to Upstream Mnemosyne (Optional MCP Server)

If your lab wants semantic vector embeddings, automatic session hooks, or a dedicated **MCP server** for Claude Code, Cursor, or Codex, you can connect the upstream open-source Mnemosyne projects alongside this workspace:

- **Python / Hermes / MCP (`mnemosyne-memory`)**:
  ```bash
  pip install mnemosyne-memory
  ```
- **TypeScript / Auditable Evidence Graph MCP (`28naem-del/mnemosyne` / `mnemosy-ai`)**:
  Supports evidence-linked dependency retirement and MCP integration for Claude Code, Cursor, and Codex.

Even without installing any external package, `tools/memory_store.py` gives every researcher in your lab an immediate, auditable, sub-millisecond Mnemosyne memory store out of the box.
