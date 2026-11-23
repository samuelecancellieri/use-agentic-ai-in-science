#!/usr/bin/env python3
"""Bundle scientific study artifacts into clean, NotebookLM-ready source packets.

NotebookLM excels when given well-structured, self-contained source documents
(Markdown, TXT, or PDF) with explicit provenance headers. This tool compiles:
  1. 01_hypothesis_and_literature.md  (Hypothesis card + literature synthesis)
  2. 02_analysis_and_provenance.md    (Statistical results + software/data provenance)
  3. 03_manuscript_draft.md           (Clean Quarto prose stripped of YAML frontmatter)
  4. 04_notebooklm_prompts.md         (Ready-to-paste NotebookLM research prompts)
  5. notebooklm_manifest.json         (File inventory and SHA-256 checksums)

Usage:
    uv run python tools/notebooklm_prep.py \
        --study-dir example-study \
        --out-dir example-study/05_notebooklm/packet
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


PROMPT_BANK = """# Curated NotebookLM Prompts for Scientific Research

Upload the generated `01_*.md`, `02_*.md`, and `03_*.md` packet files—along with your
full-text literature PDFs—into a single NotebookLM notebook, then use these prompts:

## 1. Literature Gap & Contradiction Audit
> Compare the mechanisms proposed in our Hypothesis Card (`01_hypothesis_and_literature.md`)
> against the uploaded primary literature PDFs. Where do published studies contradict our
> predicted direction of effect, and what experimental confounders could explain those discrepancies?

## 2. Claim-to-Evidence Verification (Anti-Hallucination Check)
> Audit every numerical claim and statistical statement in `03_manuscript_draft.md` against
> `02_analysis_and_provenance.md`. List any discrepancy in sample size, fold change, FDR,
> IC50, or pathway enrichment score, citing exact source passages.

## 3. Reviewer 2 Adversarial Simulation
> Act as a skeptical peer reviewer for *Nature Communications* or *eLife*. Based solely on
> the uploaded sources, identify the top 5 methodological weaknesses, missing control
> experiments, or over-interpretations in our manuscript draft.

## 4. Audio Overview / Conference Talk Prep
> Generate a 10-minute Audio Overview focused on: (a) why dual MAPK/PI3K inhibition matters
> clinically, (b) the core transcriptomic and synergy evidence from our analysis, and
> (c) the key limitations we must be prepared to defend during Q&A.
"""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def strip_yaml_frontmatter(text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n+", "", text, count=1, flags=re.DOTALL)


def build_packet(study_dir: Path, out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()

    # 1. Hypothesis & Literature bundle
    hyp_parts = [
        f"# Source Packet 01: Hypothesis & Literature Synthesis\n\n_Generated: {generated_at}_\n",
        read_if_exists(study_dir / "01_hypothesis" / "hypothesis_log.md"),
        "\n---\n",
        read_if_exists(study_dir / "01_hypothesis" / "literature_synthesis.md"),
    ]
    file_01 = out_dir / "01_hypothesis_and_literature.md"
    text_01 = "\n".join(p for p in hyp_parts if p).strip() + "\n"
    file_01.write_text(text_01, encoding="utf-8")

    # 2. Analysis & Provenance bundle
    prov_path = study_dir / "02_data" / "processed" / "provenance.json"
    prov_block = ""
    if prov_path.exists():
        prov_block = f"\n## Computational Provenance\n\n```json\n{prov_path.read_text(encoding='utf-8').strip()}\n```\n"

    ana_parts = [
        f"# Source Packet 02: Statistical Analysis & Provenance\n\n_Generated: {generated_at}_\n",
        read_if_exists(study_dir / "03_analysis" / "analysis_summary.md"),
        prov_block,
    ]
    file_02 = out_dir / "02_analysis_and_provenance.md"
    text_02 = "\n".join(p for p in ana_parts if p).strip() + "\n"
    file_02.write_text(text_02, encoding="utf-8")

    # 3. Clean manuscript draft
    qmd_raw = read_if_exists(study_dir / "06_manuscript" / "manuscript.qmd")
    file_03 = out_dir / "03_manuscript_draft.md"
    text_03 = (
        f"# Source Packet 03: Manuscript Draft\n\n_Generated: {generated_at}_\n\n"
        + strip_yaml_frontmatter(qmd_raw).strip()
        + "\n"
    )
    file_03.write_text(text_03, encoding="utf-8")

    # 4. Curated NotebookLM prompt bank
    file_04 = out_dir / "04_notebooklm_prompts.md"
    file_04.write_text(PROMPT_BANK.strip() + "\n", encoding="utf-8")

    files = [file_01, file_02, file_03, file_04]
    manifest = {
        "generated_at_utc": generated_at,
        "study_dir": str(study_dir),
        "packet_files": [
            {
                "name": f.name,
                "bytes": f.stat().st_size,
                "sha256": sha256_text(f.read_text(encoding="utf-8")),
            }
            for f in files
        ],
    }
    (out_dir / "notebooklm_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build NotebookLM-ready source packets from a study directory.")
    parser.add_argument("--study-dir", type=Path, required=True, help="Path to study directory (e.g., example-study).")
    parser.add_argument("--out-dir", type=Path, required=True, help="Destination directory for NotebookLM packet.")
    args = parser.parse_args()

    manifest = build_packet(args.study_dir, args.out_dir)
    print(f"Built NotebookLM source packet in {args.out_dir} ({len(manifest['packet_files'])} files):")
    for item in manifest["packet_files"]:  # type: ignore[index]
        print(f"  - {item['name']} ({item['bytes']:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
