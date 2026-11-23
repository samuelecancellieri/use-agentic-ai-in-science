# NotebookLM Workflow for Scientific Research

**Google NotebookLM** is uniquely valuable in scientific research because its answers are **strictly grounded in the sources you upload**, with inline passage citations. Pairing a local coding agent (for code, statistics, and plotting) with NotebookLM (for deep literature synthesis and cross-source auditing) gives researchers the best of both worlds.

---

## 1. Build a Clean Source Packet

Run `tools/notebooklm_prep.py` to compile your local research workspace into clean, NotebookLM-optimized Markdown documents:

```bash
uv run python tools/notebooklm_prep.py \
  --study-dir example-study \
  --out-dir example-study/05_notebooklm/packet
```

This creates:
- `01_hypothesis_and_literature.md` — Your pre-registered hypotheses and literature matrix.
- `02_analysis_and_provenance.md` — Exact statistical outputs and software/checksum provenance.
- `03_manuscript_draft.md` — Clean manuscript prose stripped of Quarto YAML syntax.
- `04_notebooklm_prompts.md` — Ready-to-paste scientific audit prompts.
- `notebooklm_manifest.json` — Inventory and SHA-256 checksums.

---

## 2. Four High-Impact Scientific Uses of NotebookLM

1. **Literature Synthesis Across 10–50 PDFs**:
   Upload full-text PDFs from Zotero/Paperpile alongside `01_hypothesis_and_literature.md` to map consensus mechanisms, conflicting protocols, and unresolved experimental gaps.
2. **Claim-to-Evidence Auditing**:
   Ask NotebookLM to cross-check every numerical claim in `03_manuscript_draft.md` against `02_analysis_and_provenance.md` and flag any mismatch.
3. **Adversarial Peer-Review Prep**:
   Prompt NotebookLM to act as a skeptical domain reviewer and identify missing controls or over-claims supported strictly by the uploaded papers.
4. **Audio Overviews for Lab Meetings & Seminars**:
   Generate a focused Audio Overview summarizing your study narrative, key statistical findings, and limitations to rehearse Q&A before presenting.

---

## 3. Keeping NotebookLM Synced with Google Drive

Because NotebookLM imports directly from **Google Drive**, syncing `example-study/05_notebooklm/packet/` to your Drive folder (`01_sources_and_literature/`) lets you refresh NotebookLM sources with one click whenever your analysis or manuscript updates.
