#!/usr/bin/env python3
"""Grounded scientific literature search via Europe PMC (PubMed/PMC) REST API.

Usage:
    uv run python tools/lit_search.py \
        --query "MAPK PI3K dual inhibition melanoma resistance" \
        --limit 10 \
        --out example-study/01_hypothesis/lit_results.json \
        --bibtex example-study/01_hypothesis/lit_results.bib
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import requests

EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def search_europe_pmc(query: str, limit: int = 10, sort_by: str = "CITED desc") -> list[dict[str, Any]]:
    """Query Europe PMC and return normalized paper records."""
    params = {
        "query": query,
        "format": "json",
        "resultType": "core",
        "pageSize": min(max(limit, 1), 100),
        "sort": sort_by,
    }
    resp = requests.get(EUROPE_PMC_URL, params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()

    results = []
    for item in payload.get("resultList", {}).get("result", []):
        authors = item.get("authorString", "Unknown")
        first_author = authors.split(",")[0].split()[0] if authors else "unknown"
        year = str(item.get("pubYear", "n.d."))
        citekey = re.sub(r"[^a-zA-Z0-9]", "", f"{first_author.lower()}{year}")
        results.append(
            {
                "citekey": citekey,
                "pmid": item.get("pmid"),
                "pmcid": item.get("pmcid"),
                "doi": item.get("doi"),
                "title": (item.get("title") or "").rstrip("."),
                "authors": authors,
                "journal": item.get("journalTitle") or item.get("bookOrReportDetails", {}).get("publisher", ""),
                "year": year,
                "cited_by_count": item.get("citedByCount", 0),
                "is_open_access": item.get("isOpenAccess") == "Y",
                "abstract": item.get("abstractText") or "",
            }
        )
    return results


def to_bibtex(records: list[dict[str, Any]]) -> str:
    """Convert normalized paper records into BibTeX entries."""
    seen_keys: dict[str, int] = {}
    entries: list[str] = []
    for rec in records:
        base_key = rec["citekey"]
        count = seen_keys.get(base_key, 0)
        seen_keys[base_key] = count + 1
        key = base_key if count == 0 else f"{base_key}_{chr(97 + count)}"

        fields = [
            f"  title = {{{rec['title']}}}",
            f"  author = {{{rec['authors']}}}",
            f"  journal = {{{rec['journal']}}}",
            f"  year = {{{rec['year']}}}",
        ]
        if rec.get("doi"):
            fields.append(f"  doi = {{{rec['doi']}}}")
        if rec.get("pmid"):
            fields.append(f"  pmid = {{{rec['pmid']}}}")
        entries.append(f"@article{{{key},\n" + ",\n".join(fields) + "\n}")
    return "\n\n".join(entries) + "\n"


def to_markdown(records: list[dict[str, Any]], query: str) -> str:
    """Format paper records as a Markdown literature table."""
    lines = [
        f"# Literature Search Results: `{query}`",
        "",
        "| Citekey | Year | Citations | Title | Journal | DOI |",
        "|---|---:|---:|---|---|---|",
    ]
    for r in records:
        doi_str = f"[{r['doi']}](https://doi.org/{r['doi']})" if r.get("doi") else "N/A"
        lines.append(
            f"| `{r['citekey']}` | {r['year']} | {r['cited_by_count']} | {r['title']} | {r['journal']} | {doi_str} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search Europe PMC for peer-reviewed scientific literature.")
    parser.add_argument("--query", required=True, help="Search query string (Europe PMC syntax supported).")
    parser.add_argument("--limit", type=int, default=10, help="Number of results to retrieve (1-100).")
    parser.add_argument("--sort", default="CITED desc", help="Sort order (e.g., 'CITED desc', 'P_PDATE_D desc').")
    parser.add_argument("--out", type=Path, help="Optional path to save JSON results.")
    parser.add_argument("--markdown", type=Path, help="Optional path to save Markdown summary table.")
    parser.add_argument("--bibtex", type=Path, help="Optional path to save BibTeX entries.")
    args = parser.parse_args()

    try:
        records = search_europe_pmc(args.query, limit=args.limit, sort_by=args.sort)
    except requests.RequestException as exc:
        print(f"ERROR: Literature search failed: {exc}", file=sys.stderr)
        return 1

    print(f"Retrieved {len(records)} articles from Europe PMC for query: {args.query!r}")
    for i, r in enumerate(records[:5], start=1):
        print(f"  {i}. [{r['year']}] {r['title']} (DOI: {r['doi'] or 'N/A'}, cited: {r['cited_by_count']})")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(records, indent=2), encoding="utf-8")
        print(f"Saved JSON -> {args.out}")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(to_markdown(records, args.query), encoding="utf-8")
        print(f"Saved Markdown -> {args.markdown}")
    if args.bibtex:
        args.bibtex.parent.mkdir(parents=True, exist_ok=True)
        args.bibtex.write_text(to_bibtex(records), encoding="utf-8")
        print(f"Saved BibTeX -> {args.bibtex}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
