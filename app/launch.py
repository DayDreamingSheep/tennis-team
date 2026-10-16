#!/usr/bin/env python3
"""Decide whether to start the Pocket Tennis Team app and open it (contract §5).

Called by the plugin's SessionStart hook (async) with CLAUDE_PROJECT_DIR set, by the
`open` skill (`--open`), and by the "Open Pocket Tennis Team" launcher in the workspace.
Standard library only. Must return quickly and print nothing in hook mode.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
SERVER = APP_DIR / "server.py"


def data_dir():
    d = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or (Path.home() / ".tennis-team")).expanduser()
    d.mkdir(parents=True, exist_ok=True)
    return d


def read_json(p, default=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return default


def find_workspace(start):
    start = Path(start)
    if (start / "TEAM.md").exists():
        return start.resolve()
    try:
        for c in sorted(p for p in start.iterdir() if p.is_dir() and not p.name.startswith(".")):
            if (c / "TEAM.md").exists():
                return c.resolve()
    except OSError:
        pass
    return None


def plugin_version():
    return (read_json(APP_DIR.parent / ".claude-plugin" / "plugin.json", {}) or {}).get("version", "")


def alive(info):
    """True when server.json points at a running Pocket Tennis Team server."""
    if not info or not info.get("pid") or not info.get("port"):
        return False
    try:
        os.kill(int(info["pid"]), 0)
    except (OSError, ValueError):
        return False
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{info['port']}/api/ping", timeout=0.5) as r:
            return r.status == 200
    except Exception:
        return False


def url_of(info):
    return f"http://127.0.0.1:{info['port']}/?t={info['token']}"


def stop(info):
    try:
        os.kill(int(info["pid"]), 15)
    except Exception:
        pass


def start(data, workspace, here, open_browser):
    log = open(data / "server.log", "a")
    cmd = [sys.executable, str(SERVER), "--here", str(here), "--data-dir", str(data)]
    if workspace:
        cmd += ["--workspace", str(workspace)]
    if open_browser and not os.environ.get("TT_NO_BROWSER"):
        cmd.append("--open")
    subprocess.Popen(cmd, stdout=log, stderr=log, stdin=subprocess.DEVNULL, start_new_session=True, cwd=str(here))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true", help="always open the app (skill / launcher)")
    ap.add_argument("--dir", help="folder to look for a workspace in (default: CLAUDE_PROJECT_DIR or cwd)")
    args = ap.parse_args()

    if os.environ.get("TT_JOB"):
        return                           # a background job of the app itself: never start another app
    data = data_dir()
    here = Path(args.dir or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).expanduser().resolve()
    info = read_json(data / "server.json")
    onboarded = (data / ".onboarded").exists()

    if not args.open and (data / "no-autoopen").exists():
        return
    workspace = find_workspace(here)
    if args.open and not workspace and onboarded:
        last = (read_json(data / "workspaces.json", {}) or {}).get("last")
        workspace = Path(last) if last and (Path(last) / "TEAM.md").exists() else None

    if not args.open:
        if onboarded and not workspace:
            return                       # not a tennis folder: stay silent
        # not onboarded yet: first run opens Welcome wherever Claude started

    running = alive(info)
    if running and info.get("version") != plugin_version():
        stop(info)                       # the plugin was updated: restart the app on the new code
        time.sleep(0.3)
        running = False
    if running:
        same = (info.get("workspace") or None) == (str(workspace) if workspace else None)
        if same or (not workspace and not info.get("workspace")):
            if args.open and not os.environ.get("TT_NO_BROWSER"):
                webbrowser.open(url_of(info))
            return                       # already open for this workspace (hook mode: don't pop a second tab)
        stop(info)
        time.sleep(0.3)
    start(data, workspace, here, open_browser=True)
    if args.open:
        print("Opening Pocket Tennis Team…")


if __name__ == "__main__":
    main()
