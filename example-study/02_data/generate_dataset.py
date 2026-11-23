#!/usr/bin/env python3
"""Generate a deterministic, biologically grounded RNA-seq + drug-response benchmark dataset.

Creates three files under example-study/02_data/raw/:
  - sample_metadata.csv     (16 samples: 4 treatment arms x 4 biological replicates)
  - rnaseq_counts.csv       (1,200 genes x 16 samples, negative-binomial overdispersed counts)
  - gene_pathways.csv       (Curated pathway annotations for over-representation analysis)
  - dose_response.csv       (7-point viability curves x 4 replicates for MEKi, PI3Ki, Combo)

Also writes a SHA-256 manifest at example-study/02_data/raw_manifest.json so the dataset
can be stored in Google Drive while maintaining cryptographic provenance in Git.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
STUDY_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = STUDY_DIR / "02_data" / "raw"
MANIFEST_PATH = STUDY_DIR / "02_data" / "raw_manifest.json"

PATHWAY_GENES: dict[str, list[str]] = {
    "MAPK_ERK_Signaling": [
        "DUSP6", "SPRY2", "SPRY4", "ETV4", "ETV5", "FOSL1", "MYC", "EGR1",
        "PHLDA1", "IER3", "DUSP4", "SPRED1", "SPRED2", "MAFF", "FOS", "JUNB",
        "CCND1", "HMGA2", "SERPINB2", "LIF", "IL8", "AREG", "EREG", "HBEGF", "TGFA",
    ],
    "PI3K_AKT_mTOR_Signaling": [
        "AKT3", "SGK1", "RPS6KB1", "EIF4EBP1", "SLC2A1", "HK2", "LDHA", "PFKFB3",
        "PIK3CA", "PIK3R1", "PDK1", "MTOR", "RPTOR", "RICTOR", "TSC2", "RHEB",
        "IRS2", "IGF1R", "ERBB3", "FGFR3", "VEGFA", "HIF1A", "SREBF1", "FASN", "ACLY",
    ],
    "Cell_Cycle_Proliferation": [
        "MKI67", "TOP2A", "CDK1", "CCNB1", "CCNB2", "AURKA", "AURKB", "BIRC5",
        "PCNA", "MCM2", "MCM4", "MCM6", "E2F1", "FOXM1", "CDC20", "PLK1",
        "BUB1", "BUB1B", "NDC80", "KIF11", "KIF23", "RRM2", "TYMS", "CHEK1",
        "UBE2C", "PTTG1", "CENPA", "CENPE", "NUSAP1", "TPX2",
    ],
    "Apoptosis_Stress_Response": [
        "BCL2L11", "BBC3", "PMAIP1", "BAX", "CDKN1A", "DDIT3", "ATF4", "GADD45A",
        "CASP3", "TNFRSF10B", "FAS", "TP53INP1", "SESN2", "TXNIP", "BNIP3", "BNIP3L",
        "TRIB3", "CHAC1", "HSPA5", "XBP1", "BTG2", "MDM2", "PPP1R15A", "SQSTM1", "NOXA1",
    ],
    "Oxidative_Phosphorylation": [
        "NDUFA1", "NDUFB8", "COX5A", "COX6C", "ATP5F1A", "ATP5MC1", "UQCRC1", "UQCRB",
        "SDHB", "SDHC", "PPARGC1A", "TFAM", "CYCS", "VDAC1", "CS", "IDH2",
        "MDH2", "FH", "ACO2", "OGDH", "PDHA1", "CPT1A", "ACADM", "HADHA", "ETFA",
    ],
}

HOUSEKEEPING = ["ACTB", "GAPDH", "RPLP0", "TBP"]


def generate_rnaseq(rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    treatments = ["Vehicle", "MEKi", "PI3Ki", "Combo"]
    replicates = [1, 2, 3, 4]

    meta_rows = []
    for trt in treatments:
        for rep in replicates:
            meta_rows.append(
                {
                    "sample_id": f"{trt}_R{rep}",
                    "treatment": trt,
                    "replicate": rep,
                    "batch": "Batch1" if rep <= 2 else "Batch2",
                }
            )
    metadata = pd.DataFrame(meta_rows)

    # Assemble gene list (1,200 total genes)
    pathway_rows = []
    genes = []
    for pw, glist in PATHWAY_GENES.items():
        for g in glist:
            genes.append(g)
            pathway_rows.append({"gene": g, "pathway": pw})
    for g in HOUSEKEEPING:
        genes.append(g)
        pathway_rows.append({"gene": g, "pathway": "Housekeeping"})

    n_background = 1200 - len(genes)
    for idx in range(1, n_background + 1):
        g = f"GENE_{idx:04d}"
        genes.append(g)
        pathway_rows.append({"gene": g, "pathway": "Background"})

    gene_pathways = pd.DataFrame(pathway_rows)

    # Baseline log2 expression means per gene
    base_mu = rng.lognormal(mean=5.6, sigma=1.1, size=len(genes))
    base_mu = np.clip(base_mu, 20.0, 25000.0)

    # True log2 fold changes per pathway x treatment arm
    # Encodes H1 (adaptive PI3K feedback under MEKi) and H2 (synergistic Combo arrest + apoptosis)
    pathway_lfc: dict[str, dict[str, float]] = {
        "MAPK_ERK_Signaling": {"Vehicle": 0.0, "MEKi": -2.1, "PI3Ki": -0.25, "Combo": -2.5},
        "PI3K_AKT_mTOR_Signaling": {"Vehicle": 0.0, "MEKi": 1.35, "PI3Ki": -1.75, "Combo": -2.05},
        "Cell_Cycle_Proliferation": {"Vehicle": 0.0, "MEKi": -0.85, "PI3Ki": -0.55, "Combo": -2.45},
        "Apoptosis_Stress_Response": {"Vehicle": 0.0, "MEKi": 0.65, "PI3Ki": 0.45, "Combo": 2.25},
        "Oxidative_Phosphorylation": {"Vehicle": 0.0, "MEKi": 0.45, "PI3Ki": -0.15, "Combo": 0.30},
        "Housekeeping": {"Vehicle": 0.0, "MEKi": 0.0, "PI3Ki": 0.0, "Combo": 0.0},
        "Background": {"Vehicle": 0.0, "MEKi": 0.0, "PI3Ki": 0.0, "Combo": 0.0},
    }

    # Per-gene effect heterogeneity around pathway mean
    gene_scale = rng.uniform(0.70, 1.30, size=len(genes))
    # Library size scaling factors per sample
    lib_factors = rng.uniform(0.88, 1.14, size=len(metadata))

    counts = np.zeros((len(genes), len(metadata)), dtype=int)
    dispersion = 0.06  # Realistic biological CV (~25%)

    for j, row in metadata.iterrows():
        trt = row["treatment"]
        batch_effect = 1.04 if row["batch"] == "Batch2" else 0.96
        for i, pw in enumerate(gene_pathways["pathway"]):
            lfc = pathway_lfc[pw][trt]
            if pw not in ("Background", "Housekeeping"):
                lfc = lfc * gene_scale[i]
            gene_mu = 6000.0 if pw == "Housekeeping" else base_mu[i]
            gene_disp = 0.008 if pw == "Housekeeping" else dispersion
            mu = gene_mu * (2.0 ** lfc) * lib_factors[j] * batch_effect
            # Negative binomial via Gamma-Poisson mixture
            r = 1.0 / gene_disp
            p = r / (r + mu)
            counts[i, j] = int(rng.negative_binomial(r, p))

    counts_df = pd.DataFrame(counts, index=genes, columns=metadata["sample_id"])
    counts_df.index.name = "gene"
    return metadata, counts_df, gene_pathways


def hill_viability(conc: np.ndarray, ic50: float, hill: float, bottom: float) -> np.ndarray:
    """4-parameter log-logistic viability curve (top=1.0)."""
    return bottom + (1.0 - bottom) / (1.0 + (conc / ic50) ** hill)


def generate_dose_response(rng: np.random.Generator) -> pd.DataFrame:
    concs = np.array([0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0])
    # Combo exhibits genuine Bliss synergy (lower IC50 and lower bottom plateau)
    params = {
        "MEKi": (0.85, 1.15, 0.24),
        "PI3Ki": (1.60, 1.05, 0.32),
        "Combo": (0.14, 1.35, 0.06),
    }
    rows = []
    for trt, (ic50, hill, bottom) in params.items():
        mean_viab = hill_viability(concs, ic50, hill, bottom)
        for conc, mv in zip(concs, mean_viab):
            for rep in range(1, 5):
                obs = float(np.clip(mv + rng.normal(0.0, 0.028), 0.01, 1.05))
                rows.append(
                    {
                        "treatment": trt,
                        "concentration_uM": float(conc),
                        "replicate": rep,
                        "viability": round(obs, 4),
                    }
                )
    return pd.DataFrame(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    rng = np.random.default_rng(SEED)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    metadata, counts_df, gene_pathways = generate_rnaseq(rng)
    dose_df = generate_dose_response(rng)

    metadata.to_csv(RAW_DIR / "sample_metadata.csv", index=False)
    counts_df.to_csv(RAW_DIR / "rnaseq_counts.csv")
    gene_pathways.to_csv(RAW_DIR / "gene_pathways.csv", index=False)
    dose_df.to_csv(RAW_DIR / "dose_response.csv", index=False)

    raw_files = sorted(RAW_DIR.glob("*.csv"))
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "generator": "example-study/02_data/generate_dataset.py",
        "seed": SEED,
        "files": [
            {"name": f.name, "bytes": f.stat().st_size, "sha256": sha256_file(f)}
            for f in raw_files
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Generated {len(raw_files)} raw dataset files in {RAW_DIR}")
    print(f"Wrote cryptographic data manifest -> {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
