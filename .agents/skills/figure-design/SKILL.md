---
name: figure-design
description: Design publication-grade scientific plots and multi-panel composite figures meeting Nature/Cell/Science visual standards.
---

# Plots & Publication-Grade Figure Design Skill

Use this skill at **Stage 3** to turn processed analysis outputs into clear, accessible, journal-ready figures.

## Visual & Scientific Design Standards

1. **Colorblind-Safe Palettes**:
   - Prefer **Okabe-Ito** (categorical) and **Viridis / Cividis / RdBu_r** (continuous/diverging). Never use rainbow/jet colormaps or red-green-only contrasts.
2. **Typography & Sizing**:
   - Use clean sans-serif fonts (`DejaVu Sans` / `Arial` / `Helvetica`).
   - Minimum readable font size at final print width: 7–8 pt for tick labels, 8–9 pt for axis labels, 10–12 pt bold uppercase (`A`, `B`, `C`, `D`) for multi-panel labels.
   - Target standard journal widths: single-column (~89 mm / 3.5 in) or double-column (~180–183 mm / 7.1–7.2 in).
3. **Data Integrity & Clarity**:
   - Show individual data points (strip/swarm/jitter overlay) whenever $n \le 20$ per group rather than hiding distributions behind dynamite (bar + error) plots.
   - Always label axes with clear variable names **and units** (e.g., `Concentration (µM)`, `log2 Fold Change`, `-log10(FDR)`).
   - Remove chartjunk: despined top/right axes, subtle grids only where helpful, direct labeling of key genes/curves instead of cluttered legends.
   - Ensure zero overlapping text labels.
4. **Dual-Format Export**:
   - Export every figure in **both** raster (`300 DPI PNG` for quick review & Quarto HTML/DOCX) and vector (`SVG` or `PDF` for lossless journal submission and Illustrator/Inkscape touch-ups).
5. **Automated & Visual QA**:
   - Run `uv run python tools/figure_qa.py 04_figures/output` to validate resolution, dimensions, and vector pairs.
   - Visually inspect every rendered PNG before marking the figure complete.

## Human-in-the-Loop Checkpoint (Gate 3)

- Present each rendered figure alongside its draft figure legend to the researcher for visual and narrative sign-off before drafting the full manuscript.
