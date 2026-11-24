#!/usr/bin/env python3
"""Generate a deterministic, biologically grounded single-cell RNA-seq benchmark dataset.

Creates files under example-study-scrna/02_data/raw/:
  - cell_metadata.csv     (1,200 cells across 6 donors: 3 Control, 3 AntiPD1; includes ~5% low-QC cells)
  - scrna_umi_counts.csv  (1,200 cells x 500 genes sparse-like UMI count matrix)
  - gene_annotations.csv  (Canonical lineage markers, cytotoxic/exhaustion modules, MT-* genes, background)

Also writes a SHA-256 manifest at example-study-scrna/02_data/raw_manifest.json.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 101
STUDY_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = STUDY_DIR / "02_data" / "raw"
MANIFEST_PATH = STUDY_DIR / "02_data" / "raw_manifest.json"

GENE_MODULES: dict[str, list[str]] = {
    "MT_QC": [
        "MT-CO1", "MT-CO2", "MT-CO3", "MT-ND1", "MT-ND2",
        "MT-ND4", "MT-CYB", "MT-ATP6", "MT-ATP8", "MT-ND3",
    ],
    "T_Lineage": ["CD3D", "CD3E", "CD2", "TRAC"],
    "CD8_Effector": ["CD8A", "CD8B", "GZMB", "PRF1", "IFNG", "NKG7", "CCL5", "CXCR3", "GZMA", "CST7"],
    "CD8_Exhausted": ["PDCD1", "LAG3", "HAVCR2", "TIGIT", "TOX", "ENTPD1", "CTLA4", "LAYN", "CXCL13", "BATF"],
    "CD4_Helper": ["CD4", "IL7R", "CCR7", "LTB", "TCF7", "LEF1", "MAL", "SELL"],
    "Macrophage_TAM": ["CD68", "CD14", "C1QA", "C1QB", "APOE", "TREM2", "SPP1", "LYZ", "CXCL9", "CXCL10"],
    "B_Cell": ["MS4A1", "CD79A", "CD79B", "CD19", "BANK1", "CD74", "HLA-DRA", "BLK"],
}

CELL_TYPES = ["CD8_T_Effector", "CD8_T_Exhausted", "CD4_T_Helper", "Macrophage_TAM", "B_Cell"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_gene_table() -> pd.DataFrame:
    rows = []
    seen = set()
    for mod, glist in GENE_MODULES.items():
        for g in glist:
            if g not in seen:
                rows.append({"gene": g, "module": mod})
                seen.add(g)
    n_bg = 500 - len(rows)
    for i in range(1, n_bg + 1):
        rows.append({"gene": f"BG_{i:04d}", "module": "Background"})
    return pd.DataFrame(rows)


def main() -> int:
    rng = np.random.default_rng(SEED)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    gene_df = build_gene_table()
    genes = gene_df["gene"].tolist()
    modules = gene_df["module"].tolist()
    n_genes = len(genes)

    # Donor design: 4 Control, 4 AntiPD1, 150 cells per donor = 1,200 cells
    donors = [
        ("Ctrl_D1", "Control"),
        ("Ctrl_D2", "Control"),
        ("Ctrl_D3", "Control"),
        ("Ctrl_D4", "Control"),
        ("PD1_D1", "AntiPD1"),
        ("PD1_D2", "AntiPD1"),
        ("PD1_D3", "AntiPD1"),
        ("PD1_D4", "AntiPD1"),
    ]

    # True cell-type proportions per condition (encodes H1: CD8_T_Effector expands, CD8_T_Exhausted contracts)
    base_props = {
        "Control": np.array([0.14, 0.28, 0.22, 0.24, 0.12]),
        "AntiPD1": np.array([0.36, 0.11, 0.21, 0.20, 0.12]),
    }

    # Baseline expression rate (UMIs per cell before library scaling) per module
    # Normal cells have ~4-6% MT reads and ~280-380 detected genes; damaged cells exceed 15% MT
    base_rate = np.full(n_genes, 1.6, dtype=float)
    for i, m in enumerate(modules):
        if m == "MT_QC":
            base_rate[i] = 4.5
        elif m != "Background":
            base_rate[i] = 0.6

    # Lineage-specific enrichment multipliers
    lineage_mult: dict[str, dict[str, float]] = {
        "CD8_T_Effector": {"T_Lineage": 14.0, "CD8_Effector": 22.0, "CD8_Exhausted": 2.0},
        "CD8_T_Exhausted": {"T_Lineage": 14.0, "CD8_Effector": 5.0, "CD8_Exhausted": 24.0},
        "CD4_T_Helper": {"T_Lineage": 14.0, "CD4_Helper": 20.0},
        "Macrophage_TAM": {"Macrophage_TAM": 25.0},
        "B_Cell": {"B_Cell": 24.0},
    }

    # Donor-level random effects on background genes (creates realistic inter-donor variation
    # that makes naive cell-level DE overconfident while pseudobulk remains calibrated!)
    donor_bg_effects = {
        d: np.exp(rng.normal(0.0, 0.22, size=n_genes))
        for d, _ in donors
    }

    cell_rows = []
    count_rows = []

    cell_idx = 0
    for donor_id, cond in donors:
        # Slight donor-to-donor compositional jitter
        probs = base_props[cond] + rng.normal(0.0, 0.015, size=len(CELL_TYPES))
        probs = np.clip(probs, 0.04, 0.80)
        probs = probs / probs.sum()

        n_cells_donor = 150
        assigned_types = rng.choice(CELL_TYPES, size=n_cells_donor, p=probs)

        for ct in assigned_types:
            cell_idx += 1
            cell_id = f"{donor_id}_C{cell_idx:04d}"

            # Inject ~5% low-quality / damaged cells (high %MT or very low capture)
            qc_roll = rng.random()
            is_high_mt = qc_roll < 0.035
            is_low_umi = 0.035 <= qc_roll < 0.055

            rates = base_rate.copy()
            # Apply lineage expression
            for i, m in enumerate(modules):
                if m in lineage_mult[ct]:
                    rates[i] *= lineage_mult[ct][m]
                elif m == "Background":
                    rates[i] *= donor_bg_effects[donor_id][i]

            # Apply AntiPD1 treatment reprogramming within CD8 T cells (H2)
            if cond == "AntiPD1" and ct in ("CD8_T_Effector", "CD8_T_Exhausted"):
                for i, m in enumerate(modules):
                    if m == "CD8_Effector":
                        rates[i] *= 2.8
                    elif m == "CD8_Exhausted":
                        rates[i] *= 0.34

            # Apply AntiPD1 M1/chemokine activation in Macrophages
            if cond == "AntiPD1" and ct == "Macrophage_TAM":
                for i, g in enumerate(genes):
                    if g in ("CXCL9", "CXCL10"):
                        rates[i] *= 3.2

            # Library size scaling per cell
            lib_scale = rng.lognormal(mean=0.0, sigma=0.22)
            if is_low_umi:
                lib_scale *= 0.12
            rates *= lib_scale

            if is_high_mt:
                for i, m in enumerate(modules):
                    if m == "MT_QC":
                        rates[i] *= 9.0
                    else:
                        rates[i] *= 0.45

            # Sample UMI counts (Negative Binomial overdispersion)
            disp = 0.25
            r = 1.0 / disp
            p = r / (r + np.clip(rates, 1e-4, None))
            umis = rng.negative_binomial(r, p)

            cell_rows.append(
                {
                    "cell_id": cell_id,
                    "donor_id": donor_id,
                    "condition": cond,
                    "true_cell_type": ct,
                }
            )
            count_rows.append(umis)

    meta_df = pd.DataFrame(cell_rows)
    counts_df = pd.DataFrame(count_rows, index=meta_df["cell_id"], columns=genes)
    counts_df.index.name = "cell_id"

    meta_df.to_csv(RAW_DIR / "cell_metadata.csv", index=False)
    counts_df.to_csv(RAW_DIR / "scrna_umi_counts.csv")
    gene_df.to_csv(RAW_DIR / "gene_annotations.csv", index=False)

    raw_files = sorted(RAW_DIR.glob("*.csv"))
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "generator": "example-study-scrna/02_data/generate_dataset.py",
        "seed": SEED,
        "files": [
            {"name": f.name, "bytes": f.stat().st_size, "sha256": sha256_file(f)}
            for f in raw_files
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Generated {len(raw_files)} scRNA-seq raw files ({len(meta_df)} cells x {n_genes} genes) in {RAW_DIR}")
    print(f"Wrote cryptographic manifest -> {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
