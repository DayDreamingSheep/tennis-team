#!/usr/bin/env python3
"""Tennis Team voice coach: a tiny local server for talking to your team.

Serves a voice page on 127.0.0.1, turns each message into a headless
`claude -p` run with the tennis-team plugin inside the player's workspace,
and streams friendly progress steps back to the page.

Standard library only. Usage:
    python3 voice_server.py --workspace "/path/to/My Tennis Team" [--port 8787] [--no-browser]
"""

import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parents[2]  # skills/voice/scripts -> plugin root
PAGE = HERE / "voice.html"
TOKEN = secrets.token_urlsafe(16)
ALLOWED_TOOLS = "Read Write Edit Glob Grep Skill"
VOICE_PROMPT = (
    "VOICE MODE: The player is talking to you through the Tennis Team voice page; "
    "their words come from speech-to-text, so expect filler words and mis-heard tennis terms "
    "and interpret them sensibly. Use the tennis-team coach skill for every message. "
    "Your reply is shown on screen and read aloud: keep it under 120 words, warm and spoken, "
    "short sentences, no tables, no headings, at most three short bullet points. "
    "Reply in the language the player speaks."
)

FRIENDLY_SKILLS = {
    "coach": "Your coach is listening",
    "setup": "Setting up your team",
    "log-note": "The journal keeper is writing it down",
    "coach-analysis": "The coach analyst is checking your coach's advice",
    "weekly-review": "The progress coordinator is reviewing your week",
}
FRIENDLY_FILES = {
    "weekly_assignments": "Checking this week's plan",
    "entries": "Writing your journal",
    "intake_log": "Saving your note",
    "patterns": "Looking for patterns",
    "master_summary": "Updating your big picture",
    "profile": "Updating your player profile",
    "priorities": "Reviewing your priorities",
    "current_cycle": "Checking your training block",
    "assignment_decisions": "Recording decisions",
    "action_tracker": "Updating your next steps",
    "drill_library": "Picking drills",
    "plan-data": "Updating your plan page",
    "init_workspace": "Setting up your team folder",
    "TEAM": "Reading your team rules",
}


def find_claude():
    found = shutil.which("claude")
    if found:
        return found
    for candidate in (Path.home() / ".local/bin/claude", Path("/opt/homebrew/bin/claude"), Path("/usr/local/bin/claude")):
        if candidate.exists():
            return str(candidate)
    return None


def find_workspace(start: Path) -> Path:
    if (start / "TEAM.md").exists():
        return start
    for child in sorted(p for p in start.iterdir() if p.is_dir()):
        if (child / "TEAM.md").exists():
            return child
    return start  # the coach skill sets the team up on the first message


def describe_tool(name, tool_input):
    if name == "Skill":
        skill = str(tool_input.get("skill", "")).split(":")[-1]
        return FRIENDLY_SKILLS.get(skill, "Bringing in your team")
    path = str(tool_input.get("file_path") or tool_input.get("path") or tool_input.get("command") or "")
    for key, label in FRIENDLY_FILES.items():
        if key in path:
            return label
    if name in ("Glob", "Grep"):
        return "Looking through your notes"
    if name in ("Write", "Edit"):
        return "Saving your updates"
    return None


class Job:
    def __init__(self):
        self.id = uuid.uuid4().hex
        self.steps = []
        self.reply = None
        self.error = None
        self.done = False

    def step(self, text):
        if text and text not in self.steps:
            self.steps.append(text)

    def as_dict(self):
        return {"id": self.id, "steps": self.steps, "reply": self.reply, "error": self.error, "done": self.done}


class Coach:
    def __init__(self, workspace: Path, claude: str):
        self.workspace = workspace
        self.claude = claude
        self.session_id = None
        self.jobs = {}
        self.lock = threading.Lock()

    def plan_path(self):
        ws = find_workspace(self.workspace)
        return ws / "My Tennis Plan.html"

    def start(self, text):
        job = Job()
        self.jobs[job.id] = job
        threading.Thread(target=self._run, args=(job, text), daemon=True).start()
        return job

    def _run(self, job, text):
        with self.lock:  # one conversation turn at a time
            job.step("Your coach is listening")
            cmd = [
                self.claude, "-p",
                "--plugin-dir", str(PLUGIN_ROOT),
                "--output-format", "stream-json", "--verbose",
                "--permission-mode", "acceptEdits",
                "--allowedTools", ALLOWED_TOOLS,
                "--append-system-prompt", VOICE_PROMPT,
            ]
            if self.session_id:
                cmd += ["--resume", self.session_id]
            try:
                proc = subprocess.Popen(
                    cmd, cwd=str(self.workspace), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True, bufsize=1,
                )
                proc.stdin.write(text)
                proc.stdin.close()
                for line in proc.stdout:
                    self._handle_event(job, line)
                proc.wait(timeout=900)
                if job.reply is None:
                    err = (proc.stderr.read() or "").strip()
                    job.error = err.splitlines()[-1] if err else "The coach did not answer. Please try again."
            except Exception as exc:  # surface any failure to the page
                job.error = f"Could not reach your team: {exc}"
            finally:
                job.done = True

    def _handle_event(self, job, line):
        try:
            event = json.loads(line)
        except ValueError:
            return
        if event.get("session_id"):
            self.session_id = event["session_id"]
        kind = event.get("type")
        if kind == "assistant":
            for item in event.get("message", {}).get("content", []):
                if item.get("type") == "tool_use":
                    job.step(describe_tool(item.get("name"), item.get("input") or {}))
        elif kind == "result":
            if event.get("is_error"):
                job.error = str(event.get("result") or "Something went wrong.")
            else:
                job.reply = str(event.get("result") or "").strip()

    def reset(self):
        self.session_id = None


def make_handler(coach: Coach):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _authorized(self, query):
            return query.get("t", [""])[0] == TOKEN or self.headers.get("X-Token") == TOKEN

        def _send(self, status, body, ctype="application/json"):
            data = body if isinstance(body, bytes) else body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", ctype + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            url = urlparse(self.path)
            query = parse_qs(url.query)
            if not self._authorized(query):
                return self._send(403, "Open the link printed by the voice coach.", "text/plain")
            if url.path == "/":
                return self._send(200, PAGE.read_bytes(), "text/html")
            if url.path == "/plan":
                plan = coach.plan_path()
                if plan.exists():
                    html = plan.read_text(encoding="utf-8")
                    data = plan.parent / "_system" / "plan-data.js"
                    if data.exists():  # inline the data so no unauthenticated file route is needed
                        tag = '<script src="_system/plan-data.js"></script>'
                        inline = "<script>" + data.read_text(encoding="utf-8").replace("</", "<\\/") + "</script>"
                        html = html.replace(tag, inline)
                    return self._send(200, html, "text/html")
                return self._send(404, "No plan yet - tell your coach about a practice first.", "text/plain")
            if url.path == "/api/status":
                ws = find_workspace(coach.workspace)
                return self._send(200, json.dumps({
                    "workspace": ws.name,
                    "ready": (ws / "TEAM.md").exists(),
                    "plan": coach.plan_path().exists(),
                }))
            if url.path.startswith("/api/job/"):
                job = coach.jobs.get(url.path.rsplit("/", 1)[-1])
                if not job:
                    return self._send(404, json.dumps({"error": "unknown job"}))
                return self._send(200, json.dumps(job.as_dict()))
            return self._send(404, "Not found", "text/plain")

        def do_POST(self):
            url = urlparse(self.path)
            if not self._authorized(parse_qs(url.query)):
                return self._send(403, json.dumps({"error": "forbidden"}))
            length = int(self.headers.get("Content-Length") or 0)
            try:
                payload = json.loads(self.rfile.read(length) or b"{}")
            except ValueError:
                payload = {}
            if url.path == "/api/ask":
                text = str(payload.get("text", "")).strip()
                if not text:
                    return self._send(400, json.dumps({"error": "empty message"}))
                return self._send(200, json.dumps({"id": coach.start(text[:8000]).id}))
            if url.path == "/api/reset":
                coach.reset()
                return self._send(200, json.dumps({"ok": True}))
            return self._send(404, json.dumps({"error": "not found"}))

    return Handler


def main():
    parser = argparse.ArgumentParser(description="Tennis Team voice coach")
    parser.add_argument("--workspace", default=os.getcwd())
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    claude = find_claude()
    if not claude:
        sys.exit("Could not find the `claude` command. Install Claude Code and sign in first.")
    workspace = Path(args.workspace).expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    server = None
    for port in range(args.port, args.port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(Coach(workspace, claude)))
            break
        except OSError:
            continue
    if server is None:
        sys.exit("No free port found between %d and %d." % (args.port, args.port + 19))

    url = f"http://127.0.0.1:{server.server_address[1]}/?t={TOKEN}"
    print(f"VOICE_COACH_URL {url}", flush=True)
    print(f"Workspace: {workspace}", flush=True)
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
