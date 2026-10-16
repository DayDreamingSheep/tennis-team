#!/usr/bin/env python3
"""Create (or repair) a Pocket Tennis Team workspace from the bundled templates.

Copies skills/setup/assets/workspace/ into the target folder, replacing {{DATE}}
with today's date. Existing files are never overwritten. Standard library only.

Usage: python3 init_workspace.py "/path/to/workspace"
"""

import datetime
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "workspace"


def init_workspace(target: Path):
    today = datetime.date.today().isoformat()
    created, kept = [], []
    for src in sorted(TEMPLATES.rglob("*")):
        if src.is_dir() or src.name == ".DS_Store":
            continue
        rel = src.relative_to(TEMPLATES)
        dest = target / rel
        if dest.exists():
            kept.append(str(rel))
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in {".md", ".csv", ".js", ".html"}:
            dest.write_text(src.read_text(encoding="utf-8").replace("{{DATE}}", today), encoding="utf-8")
        else:
            dest.write_bytes(src.read_bytes())
        created.append(str(rel))
    return created, kept


def main():
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 init_workspace.py "/path/to/workspace"')
    target = Path(sys.argv[1]).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    created, kept = init_workspace(target)
    print(f"WORKSPACE {target}")
    print(f"CREATED {len(created)}: " + ", ".join(created))
    if kept:
        print(f"KEPT {len(kept)} existing files")


if __name__ == "__main__":
    main()
