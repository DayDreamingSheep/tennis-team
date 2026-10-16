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
    # GitHub Pages lets browsers cache pages for 10 minutes; stamping the demo link with the commit makes
    # visitors from the landing page load the newest demo right after a deploy.
    import os, subprocess
    ver = os.environ.get("GITHUB_SHA") or subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                          capture_output=True, text=True).stdout.strip()
    landing = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    landing = landing.replace('href="demo/?demo=1"', f'href="demo/?demo=1&amp;v={ver[:8]}"')
    (OUT / "index.html").write_text(landing, encoding="utf-8")
    (OUT / "demo").mkdir()
    demo = (ROOT / "app" / "web" / "index.html").read_text(encoding="utf-8")
    # The public demo talks to nothing: no server, no API, no third parties. This policy enforces it in the browser
    # (connect-src 'none' blocks every fetch/XHR/WebSocket), so the page can't be abused to send data anywhere.
    csp = ('<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; '
           'style-src \'unsafe-inline\'; img-src data: blob:; media-src blob: data:; font-src data:; connect-src \'none\'; '
           'base-uri \'none\'; form-action \'none\'">\n<meta name="referrer" content="no-referrer">')
    demo = demo.replace("<head>", "<head>\n" + csp, 1)
    (OUT / "demo" / "index.html").write_text(demo, encoding="utf-8")
    wrap(ROOT / "design" / "flow-report.html", OUT / "case-study" / "index.html", MERMAID)
    wrap(ROOT / "design" / "timeline.html", OUT / "timeline" / "index.html")
    (OUT / "voice").mkdir()
    for f in (ROOT / "design" / "voice-samples").glob("*.m4a"):
        shutil.copy(f, OUT / "voice" / f.name)
    (OUT / ".nojekyll").write_text("")
    print("built", sum(1 for _ in OUT.rglob("*") if _.is_file()), "files")


if __name__ == "__main__":
    main()
