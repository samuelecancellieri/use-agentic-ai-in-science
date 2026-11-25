"""End-to-end verification tests for the scientific pipeline and helper tools."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
STUDY = ROOT / "example-study"


def run_py(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )


def test_dataset_and_analysis_reproducibility() -> None:
    run_py("example-study/02_data/generate_dataset.py")
    run_py("example-study/03_analysis/run_analysis.py")

    proc_dir = STUDY / "02_data" / "processed"
    assert (proc_dir / "provenance.json").exists()
    assert (STUDY / "03_analysis" / "analysis_summary.md").exists()

    # Verify H1: adaptive PI3K/AKT upregulation under MEKi
    ora = pd.read_csv(proc_dir / "pathway_ora.csv")
    pi3k_up = ora[
        (ora["comparison"] == "MEKi_vs_Vehicle")
        & (ora["direction"] == "Up")
        & (ora["pathway"] == "PI3K_AKT_mTOR_Signaling")
    ]
    assert len(pi3k_up) == 1
    assert float(pi3k_up.iloc[0]["fdr"]) < 0.05
    assert float(pi3k_up.iloc[0]["mean_log2FC"]) > 1.0

    # Verify H2: Bliss synergy & potency shift under Combo
    fits = pd.read_csv(proc_dir / "dose_response_fits.csv").set_index("treatment")
    assert float(fits.loc["Combo", "ic50_uM"]) < float(fits.loc["MEKi", "ic50_uM"]) / 2.0

    bliss = pd.read_csv(proc_dir / "bliss_synergy.csv")
    mid_bliss = bliss[bliss["concentration_uM"].between(0.1, 1.0)]["bliss_excess"].mean()
    assert float(mid_bliss) > 0.10


def test_figures_and_qa_gate() -> None:
    run_py("example-study/04_figures/make_figures.py")
    res = run_py("tools/figure_qa.py", "example-study/04_figures/output")
    assert "Figure QA PASSED" in res.stdout


def test_citation_audit_offline() -> None:
    res = run_py(
        "tools/verify_citations.py",
        "--bib",
        "example-study/06_manuscript/references.bib",
        "--qmd",
        "example-study/06_manuscript/manuscript.qmd",
        "--offline",
    )
    assert "Citation audit PASSED" in res.stdout


def test_notebooklm_packet_builder(tmp_path: Path) -> None:
    out_dir = tmp_path / "packet"
    run_py(
        "tools/notebooklm_prep.py",
        "--study-dir",
        "example-study",
        "--out-dir",
        str(out_dir),
    )
    manifest = json.loads((out_dir / "notebooklm_manifest.json").read_text(encoding="utf-8"))
    names = {item["name"] for item in manifest["packet_files"]}
    assert {
        "01_hypothesis_and_literature.md",
        "02_analysis_and_provenance.md",
        "03_manuscript_draft.md",
        "04_notebooklm_prompts.md",
    }.issubset(names)


def test_gdrive_manifest_builder(tmp_path: Path) -> None:
    out_manifest = tmp_path / "manifest.json"
    run_py(
        "tools/gdrive_sync.py",
        "manifest",
        "--local",
        "example-study/02_data/raw",
        "--out",
        str(out_manifest),
    )
    data = json.loads(out_manifest.read_text(encoding="utf-8"))
    assert data["file_count"] == 4


def test_scrna_pipeline_and_pseudoreplication_audit() -> None:
    scrna_dir = ROOT / "example-study-scrna"
    run_py("example-study-scrna/02_data/generate_dataset.py")
    run_py("example-study-scrna/03_analysis/run_analysis.py")

    proc_dir = scrna_dir / "02_data" / "processed"
    assert (proc_dir / "provenance.json").exists()
    assert (scrna_dir / "03_analysis" / "analysis_summary.md").exists()

    # Verify H1: donor-level CD8+ Effector expansion and Exhausted contraction
    comp = pd.read_csv(proc_dir / "composition_stats.csv").set_index("cell_type")
    assert float(comp.loc["CD8_T_Effector", "fdr"]) < 0.05
    assert float(comp.loc["CD8_T_Effector", "diff_pp"]) > 10.0
    assert float(comp.loc["CD8_T_Exhausted", "fdr"]) < 0.05
    assert float(comp.loc["CD8_T_Exhausted", "diff_pp"]) < -10.0

    # Verify H2: pseudobulk keeps null FPR <= 5% while naive cell-level inflates > 10%
    pb = pd.read_csv(proc_dir / "pseudobulk_de_cd8.csv")
    cell = pd.read_csv(proc_dir / "naive_cell_de_cd8.csv")
    fpr_pb = float((pb[pb["module"] == "Background"]["fdr"] < 0.05).mean())
    fpr_cell = float((cell[cell["module"] == "Background"]["fdr"] < 0.05).mean())
    assert fpr_pb <= 0.05
    assert fpr_cell > 0.10


def test_scrna_figures_and_citations() -> None:
    run_py("example-study-scrna/04_figures/make_figures.py")
    qa = run_py("tools/figure_qa.py", "example-study-scrna/04_figures/output")
    assert "Figure QA PASSED" in qa.stdout

    cit = run_py(
        "tools/verify_citations.py",
        "--bib",
        "example-study-scrna/06_manuscript/references.bib",
        "--qmd",
        "example-study-scrna/06_manuscript/manuscript.qmd",
        "--offline",
    )
    assert "Citation audit PASSED" in cit.stdout


def test_mnemosyne_memory_lifecycle(tmp_path: Path) -> None:
    db = tmp_path / "mnemosyne.db"
    digest = tmp_path / "memory_digest.md"

    run_py("tools/memory_store.py", "--db", str(db), "init")
    run_py(
        "tools/memory_store.py", "--db", str(db), "add",
        "--tier", "semantic", "--trust", "verified_data",
        "--evidence", "example-study-scrna/03_analysis/analysis_summary.md",
        "--tags", "scrna,pseudobulk",
        "--content", "Initial cohort (n=6 donors) pseudobulk FPR is 0.00%.",
    )
    run_py(
        "tools/memory_store.py", "--db", str(db), "add",
        "--tier", "procedural", "--trust", "pi_decision",
        "--evidence", "Gate 2 Sign-off",
        "--depends-on", "1",
        "--tags", "scrna,sop",
        "--content", "Report n=6 donor pseudobulk table in Methods.",
    )

    rec = run_py("tools/memory_store.py", "--db", str(db), "recall", "--query", "pseudobulk", "--json")
    hits = json.loads(rec.stdout)
    assert len(hits) == 2

    # Supersede memory #1 with --cascade -> memory #2 should become needs_review
    sup = run_py(
        "tools/memory_store.py", "--db", str(db), "supersede",
        "--id", "1",
        "--new-content", "Expanded cohort (n=8 donors) pseudobulk FPR is 0.23%.",
        "--evidence", "example-study-scrna/03_analysis/analysis_summary.md",
        "--cascade",
    )
    assert "needs_review: [2]" in sup.stdout

    audit = run_py("tools/memory_store.py", "--db", str(db), "audit")
    report = json.loads(audit.stdout)
    assert report["by_status"]["superseded"] == 1
    assert report["by_status"]["needs_review"] == 1
    assert report["missing_evidence_ids"] == []

    run_py("tools/memory_store.py", "--db", str(db), "export-md", "--out", str(digest))
    md = digest.read_text(encoding="utf-8")
    assert "[NEEDS REVIEW]" in md
    assert "Expanded cohort (n=8 donors)" in md


