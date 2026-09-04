#!/usr/bin/env python3
"""Create a new Negotiation AI SDLC change from canonical templates."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

CHANGE_ID_RE = re.compile(r"^[0-9]{8}-[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create intent.md and traceability.yaml for a new SDLC change."
    )
    parser.add_argument("--sdlc-root", required=True, type=Path)
    parser.add_argument("--id", required=True, dest="change_id")
    parser.add_argument("--title", required=True)
    parser.add_argument(
        "--date",
        default=datetime.now(timezone.utc).date().isoformat(),
        help="Creation date in YYYY-MM-DD format (default: current UTC date).",
    )
    return parser.parse_args()


def render(template_path: Path, change_id: str, title: str, date: str) -> str:
    text = template_path.read_text(encoding="utf-8")
    return (
        text.replace("{{CHANGE_ID}}", change_id)
        .replace("{{TITLE}}", title)
        .replace("{{DATE}}", date)
    )


def main() -> int:
    args = parse_args()
    sdlc_root = args.sdlc_root.resolve()
    change_id = args.change_id.strip()
    title = args.title.strip()
    date = args.date.strip()

    if not CHANGE_ID_RE.fullmatch(change_id):
        print(
            "ERROR: change ID must match YYYYMMDD-short-slug using lowercase letters, digits, and hyphens.",
            file=sys.stderr,
        )
        return 2
    if not title or any(char in title for char in ("\n", "\r")):
        print("ERROR: title must be a non-empty single line.", file=sys.stderr)
        return 2
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("ERROR: --date must use YYYY-MM-DD.", file=sys.stderr)
        return 2

    templates = sdlc_root / "templates"
    changes = sdlc_root / "changes"
    required_templates = {
        "intent.md": templates / "intent.md",
        "traceability.yaml": templates / "traceability.yaml",
    }

    missing = [str(path) for path in required_templates.values() if not path.is_file()]
    if missing:
        print("ERROR: missing template(s):", file=sys.stderr)
        for path in missing:
            print(f"  - {path}", file=sys.stderr)
        return 2

    changes.mkdir(parents=True, exist_ok=True)
    target = changes / change_id
    if target.exists():
        print(f"ERROR: change already exists: {target}", file=sys.stderr)
        return 1

    temp_path = Path(tempfile.mkdtemp(prefix=f".{change_id}-", dir=changes))
    try:
        (temp_path / "evidence").mkdir()
        for filename, template_path in required_templates.items():
            content = render(template_path, change_id, title, date)
            (temp_path / filename).write_text(content, encoding="utf-8")
        temp_path.replace(target)
    except Exception as exc:  # pragma: no cover - defensive cleanup
        shutil.rmtree(temp_path, ignore_errors=True)
        print(f"ERROR: failed to create change: {exc}", file=sys.stderr)
        return 1

    print(f"Created change: {target}")
    print(f"  - {target / 'intent.md'}")
    print(f"  - {target / 'traceability.yaml'}")
    print(f"  - {target / 'evidence'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
