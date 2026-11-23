#!/usr/bin/env python3
"""Verify BibTeX entries and Quarto manuscript citations against CrossRef.

Prevents hallucinated citations by:
1. Checking that every @citekey referenced in a .qmd file exists in references.bib.
2. Flagging unused entries in references.bib.
3. Optionally validating every DOI online via the CrossRef REST API.

Usage:
    uv run python tools/verify_citations.py \
        --bib example-study/06_manuscript/references.bib \
        --qmd example-study/06_manuscript/manuscript.qmd
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

import requests

CROSSREF_WORKS_URL = "https://api.crossref.org/works/"


def parse_bibtex(bib_text: str) -> dict[str, dict[str, str]]:
    """Parse a BibTeX file into a dict mapping citekey -> field dict."""
    entries: dict[str, dict[str, str]] = {}
    pattern = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", re.DOTALL)
    field_pattern = re.compile(r"(\w+)\s*=\s*[\{\"](.*?)[\}\"]\s*,?(?:\n|$)", re.DOTALL)

    for match in pattern.finditer(bib_text):
        key = match.group(1).strip()
        body = match.group(2)
        fields: dict[str, str] = {}
        for fmatch in field_pattern.finditer(body):
            fname = fmatch.group(1).strip().lower()
            fval = " ".join(fmatch.group(2).split())
            fields[fname] = fval
        entries[key] = fields
    return entries


def extract_qmd_citations(qmd_text: str) -> set[str]:
    """Extract Pandoc/Quarto citation keys (@key) while ignoring cross-refs (@fig-, @tbl-, @sec-, @eq-)."""
    # Strip YAML frontmatter and fenced code blocks
    cleaned = re.sub(r"^---.*?---\s*", "", qmd_text, count=1, flags=re.DOTALL)
    cleaned = re.sub(r"```.*?```", "", cleaned, flags=re.DOTALL)

    candidates = set(re.findall(r"(?<![A-Za-z0-9_])@([A-Za-z][A-Za-z0-9_:-]*)", cleaned))
    crossref_prefixes = ("fig-", "tbl-", "sec-", "eq-", "lst-", "thm-")
    return {c for c in candidates if not c.startswith(crossref_prefixes)}


def verify_doi_crossref(doi: str, timeout: int = 15) -> tuple[bool, str]:
    """Check whether a DOI resolves via CrossRef and return (ok, resolved_title)."""
    headers = {}
    email = os.getenv("RESEARCH_CONTACT_EMAIL")
    if email:
        headers["User-Agent"] = f"use-agentic-ai-in-science/0.1 (mailto:{email})"
    try:
        resp = requests.get(f"{CROSSREF_WORKS_URL}{doi}", headers=headers, timeout=timeout)
        if resp.status_code != 200:
            return False, f"HTTP {resp.status_code}"
        msg: dict[str, Any] = resp.json().get("message", {})
        titles = msg.get("title") or ["(no title)"]
        return True, titles[0]
    except requests.RequestException as exc:
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit BibTeX and Quarto citations.")
    parser.add_argument("--bib", type=Path, required=True, help="Path to references.bib.")
    parser.add_argument("--qmd", type=Path, help="Optional path to manuscript.qmd to cross-check citekeys.")
    parser.add_argument("--offline", action="store_true", help="Skip live CrossRef DOI API verification.")
    args = parser.parse_args()

    if not args.bib.exists():
        print(f"ERROR: BibTeX file not found: {args.bib}", file=sys.stderr)
        return 1

    entries = parse_bibtex(args.bib.read_text(encoding="utf-8"))
    print(f"Parsed {len(entries)} BibTeX entries from {args.bib}")
    errors = 0

    if args.qmd:
        if not args.qmd.exists():
            print(f"ERROR: Manuscript file not found: {args.qmd}", file=sys.stderr)
            return 1
        cited = extract_qmd_citations(args.qmd.read_text(encoding="utf-8"))
        missing = sorted(cited - set(entries.keys()))
        unused = sorted(set(entries.keys()) - cited)

        print(f"Found {len(cited)} unique citation keys in {args.qmd}")
        if missing:
            errors += len(missing)
            print(f"  [FAIL] Missing from .bib: {', '.join(missing)}")
        else:
            print("  [PASS] All cited keys exist in references.bib")
        if unused:
            print(f"  [WARN] Unused entries in .bib: {', '.join(unused)}")

    if not args.offline:
        print("\nVerifying DOIs against CrossRef API:")
        for key, fields in entries.items():
            doi = fields.get("doi")
            if not doi:
                print(f"  [WARN] {key}: no DOI field present")
                continue
            ok, info = verify_doi_crossref(doi)
            if ok:
                print(f"  [PASS] {key} ({doi}) -> {info[:80]}")
            else:
                errors += 1
                print(f"  [FAIL] {key} ({doi}) -> {info}")
    else:
        print("Skipped online CrossRef verification (--offline mode).")

    if errors:
        print(f"\nCitation audit FAILED with {errors} error(s).", file=sys.stderr)
        return 1
    print("\nCitation audit PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
