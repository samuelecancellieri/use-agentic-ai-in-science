#!/usr/bin/env python3
"""Generate publication-grade multi-panel scientific figures (300 DPI PNG + vector SVG).

Adheres to .agents/skills/figure-design/SKILL.md:
  - Colorblind-safe Okabe-Ito palette + diverging RdBu_r colormap.
  - Despined axes, crisp typography, bold uppercase panel labels (A, B, C, D).
  - Individual replicate points plotted alongside fitted curves.
  - Dual export: 300 DPI PNG (review/HTML/DOCX) + lossless SVG (journal submission).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

STUDY_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = STUDY_DIR / "02_data" / "raw"
PROC_DIR = STUDY_DIR / "02_data" / "processed"
OUT_DIR = STUDY_DIR / "04_figures" / "output"

# Okabe-Ito colorblind-safe palette
OKABE_ITO = {
    "Vehicle": "#7F7F7F",  # Neutral gray
    "MEKi": "#0072B2",     # Blue
    "PI3Ki": "#E69F00",    # Orange
    "Combo": "#D55E00",    # Vermilion
    "Up": "#D55E00",       # Vermilion
    "Down": "#0072B2",     # Blue
    "NS": "#CCCCCC",       # Light gray
    "Teal": "#009E73",     # Bluish green
}

MARKERS = {"Vehicle": "o", "MEKi": "s", "PI3Ki": "^", "Combo": "D"}


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
            "font.size": 9,
            "axes.titlesize": 10.5,
            "axes.titleweight": "bold",
            "axes.labelsize": 9.5,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "legend.fontsize": 8.5,
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


def plot_volcano(
    ax: plt.Axes,
    de_df: pd.DataFrame,
    title: str,
    highlight_genes: list[str],
) -> None:
    df = de_df.copy()
    df["neg_log10_fdr"] = -np.log10(np.clip(df["fdr"].values, 1e-12, 1.0))

    for direction, alpha, size in [("NS", 0.45, 14), ("Down", 0.85, 22), ("Up", 0.85, 22)]:
        sub = df[df["direction"] == direction]
        ax.scatter(
            sub["log2FC"],
            sub["neg_log10_fdr"],
            c=OKABE_ITO[direction],
            s=size,
            alpha=alpha,
            edgecolors="none",
            label=f"{direction} (n={len(sub)})",
            rasterized=False,
        )

    ax.axvline(-1.0, color="#555555", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.axvline(1.0, color="#555555", linestyle="--", linewidth=0.8, alpha=0.7)
    ax.axhline(-np.log10(0.05), color="#555555", linestyle="--", linewidth=0.8, alpha=0.7)

    # Label top 3 significant Up and top 3 significant Down genes (preferring highlight_genes when significant)
    sig_up = df[df["direction"] == "Up"].sort_values("neg_log10_fdr", ascending=False)
    sig_dn = df[df["direction"] == "Down"].sort_values("neg_log10_fdr", ascending=False)

    def pick_genes(sig_df: pd.DataFrame, preferred: list[str], k: int = 3) -> pd.DataFrame:
        pref = sig_df[sig_df["gene"].isin(preferred)]
        rest = sig_df[~sig_df["gene"].isin(preferred)]
        return pd.concat([pref, rest], ignore_index=True).head(k)

    labeled_dn = pick_genes(sig_dn, highlight_genes, k=3).sort_values("log2FC")
    labeled_up = pick_genes(sig_up, highlight_genes, k=3).sort_values("log2FC")

    dn_offsets = [(-44, 10), (10, 12), (10, -14)]
    up_offsets = [(-48, 12), (10, -14), (10, 12)]

    for idx, (_, row) in enumerate(labeled_dn.iterrows()):
        dx, dy = dn_offsets[idx % len(dn_offsets)]
        ax.annotate(
            row["gene"],
            xy=(row["log2FC"], row["neg_log10_fdr"]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=7.5,
            fontweight="bold",
            color="#222222",
            arrowprops={"arrowstyle": "-", "color": "#666666", "lw": 0.6},
        )
    for idx, (_, row) in enumerate(labeled_up.iterrows()):
        dx, dy = up_offsets[idx % len(up_offsets)]
        ax.annotate(
            row["gene"],
            xy=(row["log2FC"], row["neg_log10_fdr"]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=7.5,
            fontweight="bold",
            color="#222222",
            arrowprops={"arrowstyle": "-", "color": "#666666", "lw": 0.6},
        )

    ymax = float(df["neg_log10_fdr"].max()) * 1.18
    ax.set_ylim(-0.05, max(ymax, 2.2))
    ax.set_title(title, pad=8)
    ax.set_xlabel(r"$\log_2$ Fold Change")
    ax.set_ylabel(r"$-\log_{10}(\mathrm{BH\text{-}FDR})$")
    ax.legend(frameon=False, loc="upper center", handletextpad=0.3, markerscale=1.1)


def make_figure_1() -> None:
    pca_df = pd.read_csv(PROC_DIR / "pca_coordinates.csv")
    prov = json.loads((PROC_DIR / "provenance.json").read_text(encoding="utf-8"))
    var_exp = prov["parameters"]["pca_var_explained"]

    de_meki = pd.read_csv(PROC_DIR / "de_MEKi_vs_Vehicle.csv")
    de_pi3k = pd.read_csv(PROC_DIR / "de_PI3Ki_vs_Vehicle.csv")
    de_combo = pd.read_csv(PROC_DIR / "de_Combo_vs_Vehicle.csv")

    fig, axes = plt.subplots(2, 2, figsize=(11.0, 8.6), constrained_layout=True)

    # Panel A: Unsupervised PCA
    ax_a = axes[0, 0]
    for trt in ["Vehicle", "MEKi", "PI3Ki", "Combo"]:
        sub = pca_df[pca_df["treatment"] == trt]
        ax_a.scatter(
            sub["PC1"],
            sub["PC2"],
            c=OKABE_ITO[trt],
            marker=MARKERS[trt],
            s=65,
            edgecolors="white",
            linewidth=0.7,
            label=f"{trt} (n={len(sub)})",
            zorder=3,
        )
    ax_a.axhline(0, color="#DDDDDD", linewidth=0.7, zorder=1)
    ax_a.axvline(0, color="#DDDDDD", linewidth=0.7, zorder=1)
    ax_a.set_title("Unsupervised Transcriptome PCA", pad=8)
    ax_a.set_xlabel(f"PC1 ({var_exp[0]*100:.1f}% variance)")
    ax_a.set_ylabel(f"PC2 ({var_exp[1]*100:.1f}% variance)")
    ax_a.legend(frameon=False, loc="best")
    add_panel_label(ax_a, "A")

    # Panel B: Volcano MEKi vs Vehicle (H1)
    ax_b = axes[0, 1]
    plot_volcano(
        ax_b,
        de_meki,
        "MEKi vs. Vehicle (Adaptive PI3K Feedback)",
        highlight_genes=["DUSP6", "SPRY2", "ETV4", "AKT3", "SGK1", "IGF1R"],
    )
    add_panel_label(ax_b, "B")

    # Panel C: Volcano Combo vs Vehicle (H2)
    ax_c = axes[1, 0]
    plot_volcano(
        ax_c,
        de_combo,
        "Combo vs. Vehicle (Arrest & Apoptosis)",
        highlight_genes=["MKI67", "CDK1", "TOP2A", "BCL2L11", "BBC3", "PMAIP1"],
    )
    add_panel_label(ax_c, "C")

    # Panel D: Pathway-level mean log2FC heatmap
    ax_d = axes[1, 1]
    pathway_order = [
        "MAPK_ERK_Signaling",
        "PI3K_AKT_mTOR_Signaling",
        "Cell_Cycle_Proliferation",
        "Apoptosis_Stress_Response",
        "Oxidative_Phosphorylation",
        "Housekeeping",
    ]
    pretty_labels = [
        "MAPK / ERK",
        "PI3K / AKT / mTOR",
        "Cell Cycle",
        "Apoptosis / Stress",
        "OxPhos",
        "Housekeeping",
    ]
    mat = pd.DataFrame(index=pathway_order, columns=["MEKi", "PI3Ki", "Combo"], dtype=float)
    for col_name, df in [("MEKi", de_meki), ("PI3Ki", de_pi3k), ("Combo", de_combo)]:
        means = df.groupby("pathway")["log2FC"].mean()
        for pw in pathway_order:
            mat.loc[pw, col_name] = means.get(pw, 0.0)

    im = ax_d.imshow(mat.values, cmap="RdBu_r", vmin=-2.6, vmax=2.6, aspect="auto")
    ax_d.set_xticks(range(len(mat.columns)))
    ax_d.set_xticklabels(mat.columns, fontweight="bold")
    ax_d.set_yticks(range(len(pretty_labels)))
    ax_d.set_yticklabels(pretty_labels)
    ax_d.set_title(r"Pathway Mean $\log_2$FC vs. Vehicle", pad=8)

    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat.iloc[i, j]
            txt_color = "white" if abs(val) > 1.4 else "#111111"
            ax_d.text(j, i, f"{val:+.2f}", ha="center", va="center", color=txt_color, fontsize=8.5, fontweight="bold")

    cbar = fig.colorbar(im, ax=ax_d, fraction=0.046, pad=0.04)
    cbar.set_label(r"Mean $\log_2$FC", fontsize=8.5)
    for spine in ax_d.spines.values():
        spine.set_visible(False)
    add_panel_label(ax_d, "D")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig1_transcriptomic_landscape.png", dpi=300)
    fig.savefig(OUT_DIR / "fig1_transcriptomic_landscape.svg")
    plt.close(fig)


def hill_model(conc: np.ndarray, ic50: float, hill: float, bottom: float) -> np.ndarray:
    return bottom + (1.0 - bottom) / (1.0 + (conc / ic50) ** hill)


def make_figure_2() -> None:
    dose_df = pd.read_csv(RAW_DIR / "dose_response.csv")
    fits_df = pd.read_csv(PROC_DIR / "dose_response_fits.csv").set_index("treatment")
    bliss_df = pd.read_csv(PROC_DIR / "bliss_synergy.csv")

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(10.5, 4.4), constrained_layout=True)

    # Panel A: Dose-response viability curves with individual replicate points
    conc_grid = np.logspace(np.log10(0.008), np.log10(12.0), 200)
    for trt in ["MEKi", "PI3Ki", "Combo"]:
        sub = dose_df[dose_df["treatment"] == trt]
        ic50 = fits_df.loc[trt, "ic50_uM"]
        hill = fits_df.loc[trt, "hill_slope"]
        bottom = fits_df.loc[trt, "bottom_plateau"]

        ax_a.scatter(
            sub["concentration_uM"],
            sub["viability"],
            c=OKABE_ITO[trt],
            marker=MARKERS[trt],
            s=24,
            alpha=0.55,
            edgecolors="none",
        )
        y_fit = hill_model(conc_grid, ic50, hill, bottom)
        ax_a.plot(
            conc_grid,
            y_fit,
            color=OKABE_ITO[trt],
            linewidth=2.0,
            label=f"{trt} ($IC_{{50}}$ = {ic50:.3f} µM)",
        )

    ax_a.axhline(0.5, color="#888888", linestyle=":", linewidth=0.9)
    ax_a.set_xscale("log")
    ax_a.set_ylim(0.0, 1.08)
    ax_a.set_xlabel("Drug Concentration (µM, log scale)")
    ax_a.set_ylabel("Relative Cell Viability")
    ax_a.set_title("Dose-Response Viability & Potency Shift", pad=8)
    ax_a.legend(frameon=False, loc="lower left")
    add_panel_label(ax_a, "A")

    # Panel B: Bliss independence synergy profile
    x = bliss_df["concentration_uM"].values
    obs = bliss_df["observed_combo_inhibition"].values
    exp = bliss_df["bliss_expected_inhibition"].values
    excess = bliss_df["bliss_excess"].values

    ax_b.plot(x, obs, color=OKABE_ITO["Combo"], marker="D", linewidth=2.0, markersize=5.5, label="Observed Combo Inhibition")
    ax_b.plot(x, exp, color="#444444", linestyle="--", marker="o", linewidth=1.6, markersize=4.5, label="Bliss Expected (Additive)")
    ax_b.fill_between(x, exp, obs, where=(obs >= exp), color=OKABE_ITO["Teal"], alpha=0.22, label="Positive Bliss Synergy")

    peak_idx = int(np.argmax(excess))
    ax_b.annotate(
        f"Peak Bliss excess\n+{excess[peak_idx]:.3f} @ {x[peak_idx]} µM",
        xy=(x[peak_idx], (obs[peak_idx] + exp[peak_idx]) / 2.0),
        xytext=(1.1, 0.30),
        fontsize=8,
        fontweight="bold",
        color="#005F45",
        arrowprops={"arrowstyle": "->", "color": "#005F45", "lw": 1.0},
    )

    ax_b.set_xscale("log")
    ax_b.set_ylim(0.0, 1.05)
    ax_b.set_xlabel("Drug Concentration (µM, log scale)")
    ax_b.set_ylabel("Fractional Growth Inhibition (1 - Viability)")
    ax_b.set_title("Bliss Independence Drug Synergy Profile", pad=8)
    ax_b.legend(frameon=False, loc="upper left")
    add_panel_label(ax_b, "B")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / "fig2_synergy_viability.png", dpi=300)
    fig.savefig(OUT_DIR / "fig2_synergy_viability.svg")
    plt.close(fig)


def main() -> int:
    configure_style()
    make_figure_1()
    make_figure_2()
    print(f"Generated publication figures (PNG + SVG) in {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
