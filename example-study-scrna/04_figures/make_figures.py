#!/usr/bin/env python3
"""Generate publication-grade multi-panel scRNA-seq figures (300 DPI PNG + vector SVG).

Figure 1 (fig1_scrna_qc_and_atlas):
  A. Cell-level QC scatter (Total UMIs vs. %MT reads, Pass vs. Fail thresholds)
  B. 2D HVG-PCA cell-state atlas colored by annotated immune lineage
  C. Canonical marker-gene dot plot (% expressing cells & mean expression)
  D. Donor-level CD8+ T-cell compositional remodeling (individual donor points, n=4/arm)

Figure 2 (fig2_pseudobulk_reprogramming):
  A. Donor-level pseudobulk volcano plot (AntiPD1 vs. Control in CD8+ T cells)
  B. Pseudoreplication audit: donor-level pseudobulk vs. naive cell-level null FPR
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

STUDY_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = STUDY_DIR / "02_data" / "processed"
OUT_DIR = STUDY_DIR / "04_figures" / "output"

# Colorblind-safe Okabe-Ito palette
LINEAGE_COLORS = {
    "CD8_T_Effector": "#D55E00",   # Vermilion
    "CD8_T_Exhausted": "#0072B2",  # Blue
    "CD4_T_Helper": "#009E73",     # Teal
    "Macrophage_TAM": "#E69F00",   # Orange
    "B_Cell": "#CC79A7",           # Reddish purple
}

PRETTY_LINEAGE = {
    "CD8_T_Effector": "CD8+ Effector",
    "CD8_T_Exhausted": "CD8+ Exhausted",
    "CD4_T_Helper": "CD4+ Helper",
    "Macrophage_TAM": "Macrophage TAM",
    "B_Cell": "B Cell",
}


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
            "font.size": 9,
            "axes.titlesize": 10.5,
            "axes.titleweight": "bold",
            "axes.labelsize": 9.5,
            "xtick.labelsize": 8.2,
            "ytick.labelsize": 8.2,
            "legend.fontsize": 8.0,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.9,
            "savefig.dpi": 300,
            "svg.fonttype": "none",
        }
    )


def add_panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.14,
        1.07,
        label,
        transform=ax.transAxes,
        fontsize=13,
        fontweight="bold",
        va="top",
        ha="left",
    )


def make_figure_1() -> None:
    qc_all = pd.read_csv(PROC_DIR / "cell_qc_metrics.csv")
    emb = pd.read_csv(PROC_DIR / "cells_embedded.csv")
    dot = pd.read_csv(PROC_DIR / "marker_dotplot.csv")
    props = pd.read_csv(PROC_DIR / "donor_proportions.csv")
    comp = pd.read_csv(PROC_DIR / "composition_stats.csv").set_index("cell_type")
    prov = json.loads((PROC_DIR / "provenance.json").read_text(encoding="utf-8"))
    var_exp = prov["pca_var_explained"]

    fig, axes = plt.subplots(2, 2, figsize=(11.4, 8.8), constrained_layout=True)

    # Panel A: Single-cell QC scatter
    ax_a = axes[0, 0]
    pass_df = qc_all[qc_all["pass_qc"]]
    fail_df = qc_all[~qc_all["pass_qc"]]
    ax_a.scatter(
        pass_df["total_umis"], pass_df["pct_mt"],
        c="#0072B2", s=12, alpha=0.45, edgecolors="none",
        label=f"Pass QC (n={len(pass_df):,})",
    )
    ax_a.scatter(
        fail_df["total_umis"], fail_df["pct_mt"],
        c="#D55E00", s=16, alpha=0.75, marker="x",
        label=f"Filtered (n={len(fail_df)})",
    )
    ax_a.axhline(15.0, color="#444444", linestyle="--", linewidth=0.9)
    ax_a.axvline(500.0, color="#444444", linestyle="--", linewidth=0.9)
    ax_a.set_xlabel("Total UMI Counts per Cell")
    ax_a.set_ylabel("Mitochondrial Reads (%MT)")
    ax_a.set_title("Single-Cell Quality Control Filtering", pad=8)
    ax_a.legend(frameon=False, loc="upper right")
    add_panel_label(ax_a, "A")

    # Panel B: 2D PCA Cell-State Atlas
    ax_b = axes[0, 1]
    for ct in ["CD8_T_Effector", "CD8_T_Exhausted", "CD4_T_Helper", "Macrophage_TAM", "B_Cell"]:
        sub = emb[emb["true_cell_type"] == ct]
        ax_b.scatter(
            sub["PC1"], sub["PC2"],
            c=LINEAGE_COLORS[ct], s=14, alpha=0.72, edgecolors="none",
            label=f"{PRETTY_LINEAGE[ct]} (n={len(sub)})",
        )
    ax_b.set_xlabel(f"HVG-PC1 ({var_exp[0]*100:.1f}% variance)")
    ax_b.set_ylabel(f"HVG-PC2 ({var_exp[1]*100:.1f}% variance)")
    ax_b.set_title("Tumor-Infiltrating Immune Cell Atlas", pad=8)
    ax_b.legend(frameon=False, loc="best", markerscale=1.4)
    add_panel_label(ax_b, "B")

    # Panel C: Canonical Marker Dot Plot
    ax_c = axes[1, 0]
    lineage_order = ["CD8_T_Effector", "CD8_T_Exhausted", "CD4_T_Helper", "Macrophage_TAM", "B_Cell"]
    gene_order = [
        "CD3D", "CD8A", "GZMB", "IFNG", "PDCD1", "TOX", "LAG3",
        "CD4", "IL7R", "CD68", "C1QA", "MS4A1", "CD79A",
    ]
    dot_sub = dot[dot["gene"].isin(gene_order)].copy()
    # Scale mean expression per gene to [0, 1] for crisp visual contrast
    dot_sub["scaled_expr"] = dot_sub.groupby("gene")["mean_expr"].transform(
        lambda s: (s - s.min()) / max(s.max() - s.min(), 1e-6)
    )
    x_map = {g: i for i, g in enumerate(gene_order)}
    y_map = {ct: i for i, ct in enumerate(lineage_order)}
    xs = dot_sub["gene"].map(x_map).values
    ys = dot_sub["cell_type"].map(y_map).values
    sizes = np.clip(dot_sub["pct_expressed"].values * 1.45, 8.0, 150.0)

    sc = ax_c.scatter(
        xs, ys, s=sizes, c=dot_sub["scaled_expr"].values,
        cmap="viridis", vmin=0.0, vmax=1.0, edgecolors="#333333", linewidths=0.4,
    )
    ax_c.set_xticks(range(len(gene_order)))
    ax_c.set_xticklabels(gene_order, rotation=45, ha="right")
    ax_c.set_yticks(range(len(lineage_order)))
    ax_c.set_yticklabels([PRETTY_LINEAGE[ct] for ct in lineage_order])
    ax_c.set_title("Canonical Lineage Marker Dot Plot", pad=8)
    cbar = fig.colorbar(sc, ax=ax_c, fraction=0.045, pad=0.03)
    cbar.set_label("Scaled Mean Expr.", fontsize=8)
    add_panel_label(ax_c, "C")

    # Panel D: Donor-level compositional comparison (individual donor dots, n=4/arm)
    ax_d = axes[1, 1]
    show_types = ["CD8_T_Effector", "CD8_T_Exhausted", "B_Cell"]
    x_pos = np.arange(len(show_types))
    width = 0.34
    rng = np.random.default_rng(7)

    for offset, cond, col in [(-width / 2, "Control", "#7F7F7F"), (width / 2, "AntiPD1", "#D55E00")]:
        means = [props.loc[props["condition"] == cond, ct].mean() * 100.0 for ct in show_types]
        ax_d.bar(x_pos + offset, means, width=width, color=col, alpha=0.35, edgecolor=col, linewidth=1.1, label=f"{cond} (n=4 donors)")
        for idx, ct in enumerate(show_types):
            vals = props.loc[props["condition"] == cond, ct].values * 100.0
            jitter = rng.uniform(-0.06, 0.06, size=len(vals))
            ax_d.scatter(
                np.full(len(vals), x_pos[idx] + offset) + jitter,
                vals,
                color=col, s=36, edgecolors="white", linewidth=0.6, zorder=4,
            )

    for idx, ct in enumerate(show_types):
        fdr = comp.loc[ct, "fdr"]
        top_y = max(props[ct].max() * 100.0 + 3.5, 18.0)
        lbl = f"FDR={fdr:.4f}" if fdr < 0.05 else "NS"
        ax_d.text(x_pos[idx], top_y, lbl, ha="center", va="bottom", fontsize=8, fontweight="bold", color="#222222")

    ax_d.set_xticks(x_pos)
    ax_d.set_xticklabels([PRETTY_LINEAGE[ct] for ct in show_types])
    ax_d.set_ylim(0, 50)
    ax_d.set_ylabel("Donor Cell-Type Proportion (%)")
    ax_d.set_title("Donor-Level Immune Compositional Shift (H1)", pad=8)
    ax_d.legend(frameon=False, loc="upper right")
    add_panel_label(ax_d, "D")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig1_scrna_qc_and_atlas.png", dpi=300)
    fig.savefig(OUT_DIR / "fig1_scrna_qc_and_atlas.svg")
    plt.close(fig)


def make_figure_2() -> None:
    pb_df = pd.read_csv(PROC_DIR / "pseudobulk_de_cd8.csv")
    cell_df = pd.read_csv(PROC_DIR / "naive_cell_de_cd8.csv")

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(10.6, 4.5), constrained_layout=True)

    # Panel A: Donor-level pseudobulk volcano plot in CD8+ T cells
    pb_df["neg_log10_fdr"] = -np.log10(np.clip(pb_df["fdr"].values, 1e-12, 1.0))
    colors = {"NS": "#CCCCCC", "Down": "#0072B2", "Up": "#D55E00"}
    for direction, alpha, sz in [("NS", 0.45, 14), ("Down", 0.9, 26), ("Up", 0.9, 26)]:
        sub = pb_df[pb_df["direction"] == direction]
        ax_a.scatter(
            sub["log2FC"], sub["neg_log10_fdr"],
            c=colors[direction], s=sz, alpha=alpha, edgecolors="none",
            label=f"{direction} (n={len(sub)})",
        )

    ax_a.axvline(-1.0, color="#555555", linestyle="--", linewidth=0.8, alpha=0.7)
    ax_a.axvline(1.0, color="#555555", linestyle="--", linewidth=0.8, alpha=0.7)
    ax_a.axhline(-np.log10(0.05), color="#555555", linestyle="--", linewidth=0.8, alpha=0.7)

    label_specs = [
        ("GZMB", (10, -12)),
        ("IFNG", (-42, 10)),
        ("PRF1", (10, 8)),
        ("TOX", (-36, 8)),
        ("LAG3", (8, 8)),
        ("HAVCR2", (-48, -12)),
    ]
    for gene, (dx, dy) in label_specs:
        match = pb_df[pb_df["gene"] == gene]
        if len(match) == 1:
            row = match.iloc[0]
            ax_a.annotate(
                gene,
                xy=(row["log2FC"], row["neg_log10_fdr"]),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=7.8,
                fontweight="bold",
                color="#222222",
                arrowprops={"arrowstyle": "-", "color": "#666666", "lw": 0.6},
            )

    ax_a.set_ylim(-0.1, float(pb_df["neg_log10_fdr"].max()) * 1.18)
    ax_a.set_xlabel(r"Pseudobulk $\log_2$ Fold Change (AntiPD1 vs. Control)")
    ax_a.set_ylabel(r"$-\log_{10}(\mathrm{BH\text{-}FDR})$")
    ax_a.set_title("CD8+ T-Cell Pseudobulk DE (H2)", pad=8)
    ax_a.legend(frameon=False, loc="upper center")
    add_panel_label(ax_a, "A")

    # Panel B: Pseudoreplication audit on 440 null background genes
    bg_pb = pb_df[pb_df["module"] == "Background"]
    bg_cell = cell_df[cell_df["module"] == "Background"]
    fpr_pb = float((bg_pb["fdr"] < 0.05).mean()) * 100.0
    fpr_cell = float((bg_cell["fdr"] < 0.05).mean()) * 100.0

    methods = ["Donor Pseudobulk\n(n = 8 donors)", "Naive Cell-Level\n(Pseudoreplication)"]
    vals = [fpr_pb, fpr_cell]
    bar_cols = ["#009E73", "#D55E00"]

    bars = ax_b.bar(methods, vals, width=0.52, color=bar_cols, alpha=0.85, edgecolor="#222222", linewidth=0.8)
    ax_b.axhline(5.0, color="#444444", linestyle="--", linewidth=1.0, label="Nominal 5% FDR target")

    for bar, v in zip(bars, vals):
        ax_b.text(
            bar.get_x() + bar.get_width() / 2.0,
            v + 0.8,
            f"{v:.2f}%",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#111111",
        )

    ax_b.set_ylim(0, max(vals) * 1.25)
    ax_b.set_ylabel("False-Positive Rate on Null Genes (%)")
    ax_b.set_title("Pseudoreplication Audit (440 Background Genes)", pad=8)
    ax_b.legend(frameon=False, loc="upper left")
    add_panel_label(ax_b, "B")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig2_pseudobulk_reprogramming.png", dpi=300)
    fig.savefig(OUT_DIR / "fig2_pseudobulk_reprogramming.svg")
    plt.close(fig)


def main() -> int:
    configure_style()
    make_figure_1()
    make_figure_2()
    print(f"Generated scRNA-seq publication figures (PNG + SVG) in {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
