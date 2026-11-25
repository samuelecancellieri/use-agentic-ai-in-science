#!/usr/bin/env python3
"""Mnemosyne-inspired local-first, auditable scientific memory store (SQLite + FTS5).

Zero external dependencies beyond Python's standard library (sqlite3).
Key Mnemosyne principles implemented for scientific rigor:
  1. Single local SQLite database (.memory/mnemosyne.db) — no cloud or API key required.
  2. Four memory tiers: working, episodic, semantic, procedural.
  3. Evidence pointer & trust tier on every record (verified_data, peer_reviewed, pi_decision, exploratory).
  4. Non-destructive superseding: corrected memories remain auditable and cascade 'needs_review'
     flags to dependent memories so future agent sessions never repeat stale conclusions.
  5. Sub-millisecond full-text recall via SQLite FTS5 + Markdown export for NotebookLM/Google Drive.

Usage:
    uv run python tools/memory_store.py init
    uv run python tools/memory_store.py add --tier semantic --trust verified_data \
        --evidence "example-study/03_analysis/analysis_summary.md" \
        --tags "melanoma,h1" --content "MEKi triggers adaptive PI3K/AKT upregulation (+1.34 log2FC)."
    uv run python tools/memory_store.py recall --query "PI3K adaptive"
    uv run python tools/memory_store.py supersede --id 1 --new-content "..." --evidence "..." --cascade
    uv run python tools/memory_store.py audit
    uv run python tools/memory_store.py export-md --out .memory/memory_digest.md
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB = Path(".memory/mnemosyne.db")
VALID_TIERS = ("working", "episodic", "semantic", "procedural")
VALID_TRUST = ("verified_data", "peer_reviewed", "pi_decision", "exploratory")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    tier TEXT NOT NULL CHECK (tier IN ('working', 'episodic', 'semantic', 'procedural')),
    trust TEXT NOT NULL CHECK (trust IN ('verified_data', 'peer_reviewed', 'pi_decision', 'exploratory')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'superseded', 'needs_review', 'retired')),
    content TEXT NOT NULL,
    evidence TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '',
    depends_on TEXT NOT NULL DEFAULT '',
    superseded_by INTEGER REFERENCES memories(id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    content,
    tags,
    evidence,
    content='memories',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, content, tags, evidence)
    VALUES (new.id, new.content, new.tags, new.evidence);
END;

CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content, tags, evidence)
    VALUES ('delete', old.id, old.content, old.tags, old.evidence);
END;

CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content, tags, evidence)
    VALUES ('delete', old.id, old.content, old.tags, old.evidence);
    INSERT INTO memories_fts(rowid, content, tags, evidence)
    VALUES (new.id, new.content, new.tags, new.evidence);
END;
"""


def connect_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    return conn


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_id_list(raw: str) -> list[int]:
    if not raw.strip():
        return []
    return [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]


def add_memory(
    conn: sqlite3.Connection,
    tier: str,
    trust: str,
    content: str,
    evidence: str = "",
    tags: str = "",
    depends_on: str = "",
) -> int:
    if trust in ("verified_data", "peer_reviewed") and not evidence.strip():
        raise ValueError(f"Trust tier '{trust}' requires a non-empty --evidence pointer (file path or DOI).")

    cur = conn.execute(
        """
        INSERT INTO memories (created_at, tier, trust, status, content, evidence, tags, depends_on)
        VALUES (?, ?, ?, 'active', ?, ?, ?, ?)
        """,
        (utc_now(), tier, trust, content.strip(), evidence.strip(), tags.strip(), depends_on.strip()),
    )
    conn.commit()
    return int(cur.lastrowid)


def recall_memories(
    conn: sqlite3.Connection,
    query: str,
    limit: int = 10,
    tier: str | None = None,
    include_superseded: bool = False,
) -> list[dict[str, Any]]:
    status_clause = "" if include_superseded else "AND m.status IN ('active', 'needs_review')"
    tier_clause = "AND m.tier = ?" if tier else ""
    params: list[Any] = [query]
    if tier:
        params.append(tier)
    params.append(limit)

    sql = f"""
        SELECT m.*, bm25(memories_fts) AS rank_score
        FROM memories_fts f
        JOIN memories m ON m.id = f.rowid
        WHERE memories_fts MATCH ?
        {status_clause}
        {tier_clause}
        ORDER BY
            CASE m.trust
                WHEN 'verified_data' THEN 1
                WHEN 'peer_reviewed' THEN 2
                WHEN 'pi_decision' THEN 3
                ELSE 4
            END,
            rank_score ASC
        LIMIT ?
    """
    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        # Fallback to LIKE if user query contains special FTS characters
        like = f"%{query}%"
        fb_params: list[Any] = [like, like, like]
        if tier:
            fb_params.append(tier)
        fb_params.append(limit)
        fb_sql = f"""
            SELECT m.*, 0.0 AS rank_score
            FROM memories m
            WHERE (m.content LIKE ? OR m.tags LIKE ? OR m.evidence LIKE ?)
            {status_clause}
            {tier_clause}
            ORDER BY m.id DESC
            LIMIT ?
        """
        rows = conn.execute(fb_sql, fb_params).fetchall()
    return [dict(r) for r in rows]


def supersede_memory(
    conn: sqlite3.Connection,
    old_id: int,
    new_content: str,
    evidence: str,
    cascade: bool = True,
) -> tuple[int, list[int]]:
    row = conn.execute("SELECT * FROM memories WHERE id = ?", (old_id,)).fetchone()
    if row is None:
        raise ValueError(f"Memory ID {old_id} not found.")

    new_id = add_memory(
        conn,
        tier=row["tier"],
        trust=row["trust"],
        content=new_content,
        evidence=evidence or row["evidence"],
        tags=row["tags"],
        depends_on=row["depends_on"],
    )
    conn.execute(
        "UPDATE memories SET status = 'superseded', superseded_by = ? WHERE id = ?",
        (new_id, old_id),
    )

    flagged: list[int] = []
    if cascade:
        active_rows = conn.execute(
            "SELECT id, depends_on FROM memories WHERE status = 'active' AND depends_on != ''"
        ).fetchall()
        for dep in active_rows:
            if old_id in parse_id_list(dep["depends_on"]):
                conn.execute("UPDATE memories SET status = 'needs_review' WHERE id = ?", (dep["id"],))
                flagged.append(int(dep["id"]))

    conn.commit()
    return new_id, flagged


def audit_memories(conn: sqlite3.Connection) -> dict[str, Any]:
    rows = [dict(r) for r in conn.execute("SELECT * FROM memories ORDER BY id ASC").fetchall()]
    by_status: dict[str, int] = {}
    by_tier: dict[str, int] = {}
    missing_evidence: list[int] = []

    for r in rows:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        by_tier[r["tier"]] = by_tier.get(r["tier"], 0) + 1
        if r["status"] == "active" and r["trust"] in ("verified_data", "peer_reviewed") and not r["evidence"]:
            missing_evidence.append(int(r["id"]))

    return {
        "total_records": len(rows),
        "by_status": by_status,
        "by_tier": by_tier,
        "missing_evidence_ids": missing_evidence,
    }


def export_markdown(conn: sqlite3.Connection, out_path: Path) -> int:
    rows = [
        dict(r)
        for r in conn.execute(
            "SELECT * FROM memories WHERE status IN ('active', 'needs_review') ORDER BY tier, id"
        ).fetchall()
    ]
    lines = [
        "# Scientific Memory Digest (Mnemosyne Local Store)",
        "",
        f"_Exported: {utc_now()} — {len(rows)} active/reviewable memories._",
        "",
    ]
    for tier in VALID_TIERS:
        tier_rows = [r for r in rows if r["tier"] == tier]
        if not tier_rows:
            continue
        lines.append(f"## Tier: `{tier}`")
        lines.append("")
        for r in tier_rows:
            flag = " **[NEEDS REVIEW]**" if r["status"] == "needs_review" else ""
            ev = f" | Evidence: `{r['evidence']}`" if r["evidence"] else ""
            tags = f" | Tags: `{r['tags']}`" if r["tags"] else ""
            lines.append(f"- **[#{r['id']} | {r['trust']}]{flag}** {r['content']}{ev}{tags}")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Mnemosyne-inspired local-first scientific memory CLI (SQLite + FTS5).")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help=f"Path to SQLite DB (default: {DEFAULT_DB}).")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize the local Mnemosyne SQLite database.")

    p_add = sub.add_parser("add", help="Store a new evidence-grounded memory.")
    p_add.add_argument("--tier", choices=VALID_TIERS, required=True)
    p_add.add_argument("--trust", choices=VALID_TRUST, required=True)
    p_add.add_argument("--content", required=True)
    p_add.add_argument("--evidence", default="", help="Source file path, DOI, commit hash, or gate note.")
    p_add.add_argument("--tags", default="", help="Comma-separated tags (e.g., 'scrna,pseudobulk,h2').")
    p_add.add_argument("--depends-on", default="", help="Comma-separated parent memory IDs.")

    p_rec = sub.add_parser("recall", help="Full-text search across active memories.")
    p_rec.add_argument("--query", required=True)
    p_rec.add_argument("--limit", type=int, default=10)
    p_rec.add_argument("--tier", choices=VALID_TIERS)
    p_rec.add_argument("--include-superseded", action="store_true")
    p_rec.add_argument("--json", action="store_true", dest="as_json")

    p_sup = sub.add_parser("supersede", help="Supersede a memory with corrected evidence and optionally cascade review.")
    p_sup.add_argument("--id", type=int, required=True)
    p_sup.add_argument("--new-content", required=True)
    p_sup.add_argument("--evidence", default="")
    p_sup.add_argument("--cascade", action="store_true", help="Flag dependent active memories as 'needs_review'.")

    sub.add_parser("audit", help="Audit memory health, tiers, and evidence coverage.")

    p_exp = sub.add_parser("export-md", help="Export active memories to Markdown for NotebookLM or Google Drive.")
    p_exp.add_argument("--out", type=Path, required=True)

    args = parser.parse_args()
    conn = connect_db(args.db)

    try:
        if args.command == "init":
            print(f"Initialized Mnemosyne scientific memory store -> {args.db}")
            return 0

        if args.command == "add":
            mid = add_memory(conn, args.tier, args.trust, args.content, args.evidence, args.tags, args.depends_on)
            print(f"Stored memory #{mid} [{args.tier} | {args.trust}]")
            return 0

        if args.command == "recall":
            hits = recall_memories(conn, args.query, limit=args.limit, tier=args.tier, include_superseded=args.include_superseded)
            if args.as_json:
                print(json.dumps(hits, indent=2))
            else:
                print(f"Found {len(hits)} memory hit(s) for {args.query!r}:")
                for h in hits:
                    print(f"  [#{h['id']} | {h['tier']} | {h['trust']} | {h['status']}] {h['content']}")
                    if h["evidence"]:
                        print(f"      evidence: {h['evidence']}")
            return 0

        if args.command == "supersede":
            new_id, flagged = supersede_memory(conn, args.id, args.new_content, args.evidence, cascade=args.cascade)
            print(f"Superseded memory #{args.id} -> new memory #{new_id}")
            if flagged:
                print(f"Flagged dependent memories as needs_review: {flagged}")
            return 0

        if args.command == "audit":
            report = audit_memories(conn)
            print(json.dumps(report, indent=2))
            if report["missing_evidence_ids"]:
                return 1
            return 0

        if args.command == "export-md":
            count = export_markdown(conn, args.out)
            print(f"Exported {count} memories -> {args.out}")
            return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
