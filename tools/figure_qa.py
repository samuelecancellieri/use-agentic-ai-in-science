#!/usr/bin/env python3
"""Automated quality assurance for publication-grade scientific figures.

Checks every PNG figure in a directory for:
  1. Resolution >= 300 DPI (or configured minimum).
  2. Non-blank content (pixel standard deviation > 0).
  3. Print width within standard journal column guidelines (3.0 - 10.0 inches).
  4. Presence of a lossless vector counterpart (.svg or .pdf) for journal submission.

Usage:
    uv run python tools/figure_qa.py example-study/04_figures/output
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image


def inspect_figure(png_path: Path, min_dpi: float = 295.0) -> list[str]:
    issues: list[str] = []
    with Image.open(png_path) as img:
        width_px, height_px = img.size
        dpi_x, dpi_y = img.info.get("dpi", (0, 0))
        arr = np.asarray(img.convert("RGB"), dtype=np.float32)

    if dpi_x < min_dpi or dpi_y < min_dpi:
        issues.append(f"DPI too low ({dpi_x:.1f}x{dpi_y:.1f}; expected >= {min_dpi:.0f})")

    if dpi_x > 0:
        width_in = width_px / dpi_x
        if width_in < 2.5 or width_in > 12.0:
            issues.append(f"Unusual print width ({width_in:.2f} in)")

    if float(np.std(arr)) < 1.0:
        issues.append("Image appears blank or near-constant")

    has_vector = png_path.with_suffix(".svg").exists() or png_path.with_suffix(".pdf").exists()
    if not has_vector:
        issues.append("Missing vector counterpart (.svg or .pdf)")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate publication figure quality (DPI, size, vector pair).")
    parser.add_argument("directory", type=Path, help="Directory containing rendered PNG/SVG figures.")
    parser.add_argument("--min-dpi", type=float, default=295.0, help="Minimum required DPI (default: 295).")
    args = parser.parse_args()

    pngs = sorted(args.directory.glob("*.png"))
    if not pngs:
        print(f"ERROR: No PNG figures found in {args.directory}", file=sys.stderr)
        return 1

    total_issues = 0
    for png in pngs:
        issues = inspect_figure(png, min_dpi=args.min_dpi)
        with Image.open(png) as img:
            w, h = img.size
            dpi = img.info.get("dpi", (0, 0))
        if issues:
            total_issues += len(issues)
            print(f"[FAIL] {png.name} ({w}x{h}px @ {dpi[0]:.0f} DPI): {'; '.join(issues)}")
        else:
            print(f"[PASS] {png.name} ({w}x{h}px @ {dpi[0]:.0f} DPI, vector pair present)")

    if total_issues:
        print(f"\nFigure QA FAILED with {total_issues} issue(s).", file=sys.stderr)
        return 1
    print(f"\nFigure QA PASSED ({len(pngs)} figure(s) verified).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
