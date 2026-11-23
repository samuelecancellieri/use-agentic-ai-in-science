#!/usr/bin/env python3
"""Sync scientific datasets, NotebookLM packets, figures, and manuscript drafts with Google Drive.

Follows the "Code in Git, Unpublished Data/Results/Drafts in Google Drive" pattern:
  - Git tracks scripts, skills, docs, Quarto source, and SHA-256 data manifests.
  - Google Drive stores raw/processed datasets, literature PDFs, NotebookLM source packets,
    intermediate analysis outputs, and working manuscript drafts.

Supports two CLI backends:
  - gdrive : Official Antigravity / Google Drive CLI (`gdrive mutate upload`, `gdrive readonly download`)
  - rclone : Bulk folder sync with checksum verification (`rclone copy`)

Usage:
    uv run python tools/gdrive_sync.py manifest --local example-study/02_data/raw --out example-study/02_data/raw_manifest.json
    uv run python tools/gdrive_sync.py push --backend gdrive --local example-study/03_analysis/analysis_summary.md --folder-id <DRIVE_FOLDER_ID> --dry-run
    uv run python tools/gdrive_sync.py push --backend rclone --local example-study/04_figures/output --remote gdrive:science/figures --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(local_dir: Path, out_path: Path) -> dict[str, object]:
    files = sorted(p for p in local_dir.rglob("*") if p.is_file())
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(local_dir),
        "file_count": len(files),
        "files": [
            {
                "relative_path": str(p.relative_to(local_dir)),
                "bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            }
            for p in files
        ],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def push_gdrive_cli(local_path: Path, folder_id: str, dry_run: bool) -> int:
    if not shutil.which("gdrive"):
        print("ERROR: 'gdrive' CLI not found on PATH.", file=sys.stderr)
        return 1

    files = [local_path] if local_path.is_file() else sorted(p for p in local_path.rglob("*") if p.is_file())
    if not files:
        print(f"No files found under {local_path}")
        return 0

    for f in files:
        cmd = ["gdrive", "mutate", "upload", str(f), "--parent", folder_id]
        if dry_run:
            print("[DRY-RUN]", " ".join(cmd))
        else:
            print("Executing:", " ".join(cmd))
            rc = subprocess.call(cmd)
            if rc != 0:
                return rc
    return 0


def pull_gdrive_cli(file_id: str, local_out: Path, dry_run: bool) -> int:
    if not shutil.which("gdrive"):
        print("ERROR: 'gdrive' CLI not found on PATH.", file=sys.stderr)
        return 1

    local_out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["gdrive", "readonly", "download", file_id, "--out", str(local_out)]
    if dry_run:
        print("[DRY-RUN]", " ".join(cmd))
        return 0
    print("Executing:", " ".join(cmd))
    return subprocess.call(cmd)


def run_rclone(src: str, dst: str, dry_run: bool) -> int:
    if not shutil.which("rclone"):
        print(
            "ERROR: 'rclone' is not installed on PATH. Install it (https://rclone.org/drive/) "
            "or use --backend gdrive with the Google Drive CLI.",
            file=sys.stderr,
        )
        return 1

    cmd = ["rclone", "copy", src, dst, "--progress", "--checksum"]
    if dry_run:
        cmd.append("--dry-run")
    print("Executing:", " ".join(cmd))
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Google Drive sync & data manifest helper for scientific projects.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_manifest = sub.add_parser("manifest", help="Compute SHA-256 manifest for a local data/results directory.")
    p_manifest.add_argument("--local", type=Path, required=True, help="Local directory to hash.")
    p_manifest.add_argument("--out", type=Path, required=True, help="Output JSON manifest path.")

    p_push = sub.add_parser("push", help="Upload local artifacts (data, results, figures, drafts) to Google Drive.")
    p_push.add_argument("--backend", choices=["gdrive", "rclone"], default="gdrive", help="Sync backend.")
    p_push.add_argument("--local", type=Path, required=True, help="Local directory or file.")
    p_push.add_argument("--folder-id", help="Google Drive parent folder ID (required for --backend gdrive).")
    p_push.add_argument("--remote", help="rclone remote path (required for --backend rclone).")
    p_push.add_argument("--dry-run", action="store_true", help="Preview transfers without uploading.")

    p_pull = sub.add_parser("pull", help="Download datasets or shared drafts from Google Drive.")
    p_pull.add_argument("--backend", choices=["gdrive", "rclone"], default="gdrive", help="Sync backend.")
    p_pull.add_argument("--file-id", help="Google Drive file ID (required for --backend gdrive).")
    p_pull.add_argument("--remote", help="rclone remote path (required for --backend rclone).")
    p_pull.add_argument("--local", type=Path, required=True, help="Local destination path.")
    p_pull.add_argument("--dry-run", action="store_true", help="Preview transfers without downloading.")

    args = parser.parse_args()

    if args.command == "manifest":
        if not args.local.exists():
            print(f"ERROR: Local path not found: {args.local}", file=sys.stderr)
            return 1
        manifest = build_manifest(args.local, args.out)
        print(f"Wrote SHA-256 manifest ({manifest['file_count']} files) -> {args.out}")
        return 0

    if args.command == "push":
        if not args.local.exists():
            print(f"ERROR: Local path not found: {args.local}", file=sys.stderr)
            return 1
        if args.backend == "gdrive":
            if not args.folder_id:
                print("ERROR: --folder-id is required when --backend gdrive.", file=sys.stderr)
                return 1
            return push_gdrive_cli(args.local, args.folder_id, dry_run=args.dry_run)
        if not args.remote:
            print("ERROR: --remote is required when --backend rclone.", file=sys.stderr)
            return 1
        return run_rclone(str(args.local), args.remote, dry_run=args.dry_run)

    if args.command == "pull":
        if args.backend == "gdrive":
            if not args.file_id:
                print("ERROR: --file-id is required when --backend gdrive.", file=sys.stderr)
                return 1
            return pull_gdrive_cli(args.file_id, args.local, dry_run=args.dry_run)
        if not args.remote:
            print("ERROR: --remote is required when --backend rclone.", file=sys.stderr)
            return 1
        args.local.mkdir(parents=True, exist_ok=True)
        return run_rclone(args.remote, str(args.local), dry_run=args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
