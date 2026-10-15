#!/usr/bin/env python3
"""Assemble the GitHub Pages site into _site/ (run by .github/workflows/pages.yml).

/            site/index.html            portfolio landing page
/demo/       app/web/index.html         the real app; without a server it runs in demo mode
/case-study/ design/flow-report.html    wrapped in a full page; mermaid diagrams rendered in the browser
/timeline/   design/timeline.html       wrapped in a full page
/voice/      design/voice-samples/*.m4a
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{extra}
</head>
<body>
{body}
</body>
</html>
"""
MERMAID = """<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
mermaid.initialize({ startOnLoad: false, theme: "neutral", securityLevel: "strict" });
await mermaid.run({ querySelector: "pre.mermaid" });
</script>"""


def wrap(src, dest, extra=""):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(PAGE.format(extra=extra, body=src.read_text(encoding="utf-8")), encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "site" / "index.html", OUT / "index.html")
    (OUT / "demo").mkdir()
    shutil.copy(ROOT / "app" / "web" / "index.html", OUT / "demo" / "index.html")
    wrap(ROOT / "design" / "flow-report.html", OUT / "case-study" / "index.html", MERMAID)
    wrap(ROOT / "design" / "timeline.html", OUT / "timeline" / "index.html")
    (OUT / "voice").mkdir()
    for f in (ROOT / "design" / "voice-samples").glob("*.m4a"):
        shutil.copy(f, OUT / "voice" / f.name)
    (OUT / ".nojekyll").write_text("")
    print("built", sum(1 for _ in OUT.rglob("*") if _.is_file()), "files")


if __name__ == "__main__":
    main()
