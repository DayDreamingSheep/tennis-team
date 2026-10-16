#!/usr/bin/env python3
"""Pocket Tennis Team app server (v0.2).

Serves the app page on 127.0.0.1 behind a secret token, reads and patches the
player's workspace, and runs AI jobs (`claude -p` with this plugin) one at a
time. Standard library only. Build contract: design/v0.2-architecture.md.

Usage:
    python3 server.py [--workspace DIR] [--here DIR] [--port 8787] [--open] [--data-dir DIR]
Without --workspace the server starts in first-run mode and the page shows Welcome.
"""

import argparse
import datetime
import importlib.util
import json
import os
import queue
import re
import secrets
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))
from voice import VoiceManager  # noqa: E402
import net  # noqa: E402
PLUGIN_ROOT = APP_DIR.parent
PAGE = APP_DIR / "web" / "index.html"
# Installed through /plugin install (the hook passes CLAUDE_PLUGIN_ROOT): Claude already loads the plugin itself.
INSTALLED = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or "/nonexistent").resolve() == PLUGIN_ROOT
INIT_SCRIPT = PLUGIN_ROOT / "skills" / "setup" / "scripts" / "init_workspace.py"
TOKEN = secrets.token_urlsafe(18)
ALLOWED_TOOLS = "Read Write Edit Glob Grep Skill"
# How each teammate works (Adjust pages). Saved under "team" in _system/settings.json; every job gets them.
TEAM_SETTINGS = {
    "planner": {"pace": ["Gentle", "Steady", "Aggressive"], "drills": ["1", "2", "3"], "days": ["2", "3", "4", "5+"],
                "day": ["Sunday", "Monday"], "check": ["Monthly", "Every block"], "fitness": [True, False]},
    "journal": {"focus": ["Technique", "Tactics", "Mental side", "Body"], "followup": ["Just save it", "One follow-up", "Dig deeper"],
                "tone": ["Short and direct", "Encouraging"], "inbox": [True, False], "exact": [True, False]},
    "tournament": {"taper": ["3 days", "5 days", "1 week"], "remind": ["1 week", "2 weeks", "1 month"],
                   "plans": ["Before every match", "Tournaments only"], "scout": [True, False], "ask_after": [True, False]},
    "coach": {"tone": ["Encouraging", "Balanced", "Straight-talking"], "length": ["Short", "Detailed"], "ask_score": [True, False]},
}
TEAM_DEFAULTS = {
    "planner": {"pace": "Steady", "drills": "3", "days": "4", "day": "Sunday", "check": "Monthly", "fitness": True},
    "journal": {"focus": ["Technique"], "followup": "One follow-up", "tone": "Short and direct", "inbox": True, "exact": True},
    "tournament": {"taper": "1 week", "remind": "2 weeks", "plans": "Before every match", "scout": True, "ask_after": True},
    "coach": {"tone": "Balanced", "length": "Short", "ask_score": True},
}


def clean_team_settings(raw):
    """Keep only known groups, keys and values."""
    out = {}
    for g, keys in TEAM_SETTINGS.items():
        for k, allowed in keys.items():
            v = ((raw or {}).get(g) or {}).get(k)
            if k == "focus" and isinstance(v, list):
                v = [x for x in v if x in allowed] or None
            elif v not in allowed:
                v = None
            if v is not None:
                out.setdefault(g, {})[k] = v
    return out
STUDY_TOOLS = ALLOWED_TOOLS + " WebSearch WebFetch"   # saved links: read public text about them
MAX_BODY = 2_000_000

APP_MODE = (
    "APP MODE: You are answering inside the Pocket Tennis Team app. The first line of the message is "
    "'[app] kind=<kind> mode=<adult|parent> today=<YYYY-MM-DD>'; an optional '[fields]' line carries structured "
    "answers; the rest is the player's (or parent's) own words, often from speech-to-text, so repair obvious "
    "mishearings of tennis words and names. Use the tennis-team coach skill for every message and follow TEAM.md. "
    "Before replying, update the workspace files AND _system/state.json as the skills describe, then regenerate "
    "_system/plan-data.js. Your visible reply is shown in a chat and read aloud: under 120 words, warm, plain "
    "language, health first, no tables, no headings, no IDs or file names, at most 3 next steps. End the reply with "
    "a fenced block exactly like:\n```tt-meta\n{\"members\": [\"head-coach\"], \"next_steps\": [\"...\"], "
    "\"say\": \"...\", \"state_changed\": true}\n```\n\"say\" is the reply written to be spoken aloud by a warm coach: "
    "under 70 words, contractions, no lists or symbols, numbers as words, ends with a short question or nudge.\nMember ids: head-coach, team-manager, journal-keeper, coach-analyst, "
    "progress-coordinator, strategy-coach, tournament-coach. Reply in the language the player uses."
)

FAST_MODE = (
    "FAST REPLY MODE for the Pocket Tennis Team app. Do NOT edit files and do NOT use skills; your teammates update the "
    "journal and plan right after you. Read _system/state.json first (the player's current plan, flags, events, "
    "tournaments, coach); read TEAM.md only if you need a rule. The message starts with '[app] kind=... mode=... "
    "today=...', may have '[fields]' (structured answers) and '[recent]' (the last messages), then the player's words "
    "(often speech-to-text: repair obvious mishearings). Reply as their Head Coach, crediting teammates where useful.\n"
    "Follow '[team settings]': coach.tone and coach.length set how you talk; journal.followup 'One follow-up' or 'Dig "
    "deeper' lets you end with one optional question about journal.focus (never one that blocks anything). If the player "
    "asks to change how a teammate works ('make my plan more aggressive', 'only two things a week', 'ask me fewer "
    "questions', 'remind me a month before entries'), put the change in tt-meta \"settings\" using only these values: "
    "planner.pace Gentle|Steady|Aggressive, planner.drills 1|2|3, planner.days 2|3|4|5+, planner.day Sunday|Monday, "
    "planner.fitness true|false, journal.focus [Technique, Tactics, Mental side, Body], journal.followup Just save it|One "
    "follow-up|Dig deeper, journal.tone Short and direct|Encouraging, tournament.taper 3 days|5 days|1 week, "
    "tournament.remind 1 week|2 weeks|1 month, tournament.plans Before every match|Tournaments only, coach.tone "
    "Encouraging|Balanced|Straight-talking, coach.length Short|Detailed; then say in the reply what will change, "
    "crediting the Planner, Journal Keeper or Tournament Coach. Juniors (mode=parent) stay at Steady at most; say so. "
    "Rules: health first. Tightness or soreness = keep an eye on it; pain = rest that work and see a professional; "
    "limping or pain during a match = stop playing now. Juniors (mode=parent) with growth pain such as Sever's: less "
    "impact, physio before the next event, withdrawing is OK. Signs of distress, burnout, self-harm or disordered "
    "eating: pause coaching, reply warmly, encourage talking to a trusted adult, mention crisis resources. Always say "
    "'This isn't medical advice' when giving health guidance. React to their numbers versus the current targets and "
    "cues. kind=car-talk: give 2 things to say, 1 to avoid, 1 question for later. kind=source: the player saved training "
    "material (a link). You have NOT seen its content and must not pretend you have or invent what it says; thank them "
    "and say Coach Analyst is studying it now (reading public information about it) and will have study notes ready on "
    "that teammate's page in a few minutes; ask them to tell you the one thing they take from it after they watch or "
    "read it, since their own takeaway counts most. When a question touches a coach or channel the player learns from, "
    "you may read coaches/<slug>/study-notes.md and principles.md and use them, saying they come from public material "
    "and haven't been checked against the player's own lessons yet. kind=knowledge: the player acted on one idea the "
    "Head Coach knows ([fields] action fix or test): for fix, thank them and say the team will correct it; for test, say "
    "exactly what to count next practice and the target, in one or two sentences. In parent mode speak to the parent "
    "about the junior by name. Plain language, no IDs or file names, no tables or headings, under 110 words, at most "
    "3 next steps, in the player's language. End with a fenced block exactly like:\n```tt-meta\n{\"members\": "
    "[\"head-coach\"], \"next_steps\": [\"...\"], \"say\": \"...\", \"state_changed\": false, \"settings\": {}}\n```\n"
    "\"say\" is the same message written to be spoken aloud by a warm coach: under 70 words, contractions, "
    "no lists, symbols or emoji, numbers and scores as words (\"six out of ten\", \"four-six\"), uses the player's "
    "name once, sounds like talking not reading, and ends with a short question or nudge.\nMember ids: head-coach, "
    "team-manager, journal-keeper, coach-analyst, progress-coordinator, strategy-coach, tournament-coach, fitness-coach. "
    "Active state.fitness.limits bind every suggestion. Names the player "
    "sees: strategy-coach is 'the Planner' (never 'Strategy Coach'); coach-analyst is 'Coach Analyst', who works behind the "
    "Head Coach."
)
BOOK_MODE = (
    "BOOKKEEPING MODE for the Pocket Tennis Team app. The player has ALREADY been answered; the '[replied]' line holds that "
    "reply and its next steps. Do the team's full work for this message with the tennis-team coach skill and TEAM.md: "
    "journal it, update patterns, decisions, flags, events, tournaments, coach notes, next steps (use the replied next "
    "steps), _system/state.json and _system/plan-data.js, so the app matches what the player was told. Follow "
    "'[team settings]' as TEAM.md rule 19 and the coach skill's references/team-settings.md describe; if this message "
    "changed a setting (the reply says so), re-plan what it affects now, and write the change to "
    "_system/settings_request.json as {\"planner\": {\"pace\": \"Aggressive\"}} (same keys and values as the reply's "
    "settings) so the app saves it. assignments[].status uses only new, keep, progress, reduce, pause, replace or validate. For kind=source, "
    "study the saved link with the coach-analysis skill, Mode D (study a saved link): public text only, written up as "
    "study notes for the Head Coach, and the matching _system/sources.json item updated by its id. Do not "
    "contradict the reply; if the evidence clearly requires a different decision, record it and add one short next "
    "step that explains the change. Your final text is not shown to anyone: end with just 'done'."
)


SKILL_MEMBER = {
    "coach": "head-coach", "setup": "team-manager", "log-note": "journal-keeper",
    "coach-analysis": "coach-analyst", "weekly-review": "progress-coordinator",
    "strategy": "strategy-coach", "tournament": "tournament-coach", "fitness": "fitness-coach",
}
MEMBER_STEP = {
    "head-coach": "Listening", "team-manager": "Setting up your team", "journal-keeper": "Writing it into your journal",
    "coach-analyst": "Checking your coach's advice", "progress-coordinator": "Reviewing your plan",
    "strategy-coach": "Checking your long-term plan", "tournament-coach": "Working on your tournaments",
    "fitness-coach": "Checking your body and fitness",
}
FILE_STEPS = [   # (path fragment, step text, team member who owns that file; None = keep the active member)
    ("state.json", "Updating your app", None), ("plan-data", "Updating your plan page", "head-coach"),
    ("weekly_assignments", "Updating this week's plan", "progress-coordinator"), ("current_cycle", "Planning this block", "progress-coordinator"),
    ("priorities", "Choosing your priorities", "progress-coordinator"), ("assignment_decisions", "Recording decisions", "progress-coordinator"),
    ("drill_library", "Picking drills", "progress-coordinator"), ("action_tracker", "Updating your next steps", "journal-keeper"),
    ("entries", "Writing your journal", "journal-keeper"), ("intake_log", "Saving your note", "journal-keeper"),
    ("patterns", "Looking for patterns", "journal-keeper"), ("master_summary", "Updating your big picture", "journal-keeper"),
    ("profile", "Updating your player profile", "team-manager"), ("onboarding", "Reading your answers", "team-manager"),
    ("goals", "Setting your goal", "strategy-coach"), ("roadmap", "Drawing your roadmap", "strategy-coach"),
    ("tournaments/", "Updating your tournaments", "tournament-coach"), ("study-notes", "Writing study notes", "coach-analyst"),
    ("health.md", "Updating your body notes", "fitness-coach"), ("fitness_program", "Fitting your gym program in", "fitness-coach"),
    ("sources.json", "Saving what they learned", "coach-analyst"), ("coaches/", "Updating your coach notes", "coach-analyst"),
    ("TEAM.md", "Reading your team rules", None),
]


# ---------------------------------------------------------------- helpers
def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")


def today_iso():
    return datetime.date.today().isoformat()


def data_dir(arg=None):
    d = Path(arg or os.environ.get("CLAUDE_PLUGIN_DATA") or (Path.home() / ".tennis-team")).expanduser()
    d.mkdir(parents=True, exist_ok=True)
    return d


def plugin_version():
    return (read_json(PLUGIN_ROOT / ".claude-plugin" / "plugin.json", {}) or {}).get("version", "")


def find_claude():
    found = shutil.which("claude")
    if found:
        return found
    for c in (Path.home() / ".local/bin/claude", Path("/opt/homebrew/bin/claude"), Path("/usr/local/bin/claude")):
        if c.exists():
            return str(c)
    return None


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def find_workspace(start):
    start = Path(start)
    if (start / "TEAM.md").exists():
        return start
    try:
        for child in sorted(p for p in start.iterdir() if p.is_dir() and not p.name.startswith(".")):
            if (child / "TEAM.md").exists():
                return child
    except OSError:
        pass
    return None


def icloud_dir():
    d = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
    return d if d.exists() else None


def run_init(target):
    spec = importlib.util.spec_from_file_location("init_workspace", INIT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    target.mkdir(parents=True, exist_ok=True)
    return mod.init_workspace(target)


def apply_patch(obj, ops):
    """ops: [{op: set|push|remove, path: 'a.b.0', value}]"""
    for o in ops:
        parts = [p for p in str(o.get("path", "")).split(".") if p != ""]
        if not parts:
            continue
        cur = obj
        for i, key in enumerate(parts[:-1]):
            nxt = parts[i + 1]
            if isinstance(cur, list):
                cur = cur[int(key)]
            else:
                if key not in cur or not isinstance(cur[key], (dict, list)):
                    cur[key] = [] if nxt.isdigit() else {}
                cur = cur[key]
        last, op = parts[-1], o.get("op", "set")
        if isinstance(cur, list):
            idx = int(last)
            if op == "remove":
                cur.pop(idx)
            else:
                cur[idx] = o.get("value")
        else:
            if op == "set":
                cur[last] = o.get("value")
            elif op == "push":
                cur.setdefault(last, [])
                cur[last].append(o.get("value"))
            elif op == "remove":
                cur.pop(last, None)
    return obj


# ---------------------------------------------------------------- jobs
class Job:
    def __init__(self, kind):
        self.id = uuid.uuid4().hex[:12]
        self.kind = kind
        self.steps = []
        self.members = []
        self.reply = None
        self.next_steps = []
        self.error = None
        self.done = False
        self.state_changed = False
        self.say = None
        self.bookkeeping = None          # None (single pass) | pending | running | done | error | skipped
        self._member = "head-coach"

    def member(self, m):
        if m and m not in self.members:
            self.members.append(m)
        if m:
            self._member = m

    def step(self, text, member=None):
        member = member or self._member
        if text and not any(s["text"] == text for s in self.steps):
            self.steps.append({"member": member, "text": text})

    def as_dict(self):
        return {"id": self.id, "kind": self.kind, "steps": self.steps, "members": self.members, "reply": self.reply,
                "next_steps": self.next_steps, "error": self.error, "done": self.done, "state_changed": self.state_changed,
                "bookkeeping": self.bookkeeping, "say": self.say}


class App:
    def __init__(self, args):
        self.args = args
        self.data = data_dir(args.data_dir)
        self.voice = VoiceManager(self.data)
        self.claude = find_claude()
        self.here = Path(args.here or os.getcwd()).expanduser().resolve()
        ws = Path(args.workspace).expanduser().resolve() if args.workspace else None
        self.workspace = ws
        self.jobs = {}
        self.q = queue.Queue()       # serialized writes: patches, bookkeeping, onboarding
        self.fq = queue.Queue()      # fast read-only replies
        self.busy = False
        threading.Thread(target=self._worker, daemon=True).start()
        threading.Thread(target=self._fast_worker, daemon=True).start()

    # -- paths
    def ws(self, *p):
        return self.workspace.joinpath(*p)

    def session_file(self):
        return self.ws("_system", "session.json")

    # -- state
    def read_state(self):
        if not self.workspace:
            return None
        return read_json(self.ws("_system", "state.json"))

    def onboarded(self):
        return bool(self.workspace and self.ws("player", "onboarding.json").exists())

    def conversation(self, limit=200):
        if not self.workspace:
            return []
        f = self.ws("_system", "conversation.jsonl")
        if not f.exists():
            return []
        out = []
        for line in f.read_text(encoding="utf-8").splitlines()[-limit:]:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
        return out

    def append_convo(self, entry):
        f = self.ws("_system", "conversation.jsonl")
        f.parent.mkdir(parents=True, exist_ok=True)
        entry.setdefault("at", now_iso())
        with f.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def settings(self):
        s = read_json(self.ws("_system", "settings.json"), {}) if self.workspace else {}
        s["autoOpen"] = not (self.data / "no-autoopen").exists()
        s["team"] = self.team_settings()
        return s

    def team_settings(self):
        saved = clean_team_settings((read_json(self.ws("_system", "settings.json"), {}) if self.workspace else {}).get("team"))
        out = {g: dict(v, **saved.get(g, {})) for g, v in TEAM_DEFAULTS.items()}
        st = self.read_state() or {}
        if st.get("mode") == "parent" or (isinstance(st.get("age"), int) and st["age"] < 18):
            if out["planner"]["pace"] == "Aggressive":
                out["planner"]["pace"] = "Steady"      # junior guardrail (TEAM.md rule 15)
                out["planner"]["junior_cap"] = True
        return out

    def save_team_settings(self, change):
        change = clean_team_settings(change)
        if not change or not self.workspace:
            return False
        s = read_json(self.ws("_system", "settings.json"), {})
        team = s.get("team") or {}
        for g, v in change.items():
            team.setdefault(g, {}).update(v)
        s["team"] = team
        write_json(self.ws("_system", "settings.json"), s)
        return True

    def ready(self):
        return bool(self.workspace and self.ws("TEAM.md").exists())

    def folders(self):
        ic = icloud_dir()
        return {"documents": str(Path.home() / "Documents" / "Tennis"),
                "icloud": str(ic / "Tennis") if ic else None,
                "here": str(self.here)}

    def boot(self):
        return {"token": TOKEN, "firstRun": not self.ready(), "workspace": str(self.workspace) if self.workspace else None,
                "today": today_iso(), "folders": self.folders(), "claude": bool(self.claude)}

    def record_server(self, port):
        write_json(self.data / "server.json", {"pid": os.getpid(), "port": port, "token": TOKEN, "version": plugin_version(),
                                                "workspace": str(self.workspace) if self.workspace else None, "started": now_iso()})

    def remember_workspace(self):
        w = read_json(self.data / "workspaces.json", {"last": None, "all": []})
        p = str(self.workspace)
        w["last"] = p
        if p not in w.get("all", []):
            w.setdefault("all", []).append(p)
        write_json(self.data / "workspaces.json", w)

    def write_launcher(self):
        """Double-clickable 'Open Pocket Tennis Team.command' inside the workspace (macOS)."""
        try:
            f = self.ws("Open Pocket Tennis Team.command")
            f.write_text('#!/bin/bash\ncd "$(dirname "$0")"\npython3 "%s" --open --dir "$(pwd)"\n' % (APP_DIR / "launch.py"), encoding="utf-8")
            f.chmod(0o755)
        except OSError:
            pass

    # -- folder + onboarding
    def choose_folder(self, choice, path=None):
        if choice == "icloud" and icloud_dir():
            target = icloud_dir() / "Tennis"
        elif choice == "here":
            target = self.here
        elif choice == "path" and path:
            target = Path(path).expanduser()
        else:
            target = Path.home() / "Documents" / "Tennis"
        existing = find_workspace(target)
        self.workspace = (existing or target).resolve()
        run_init(self.workspace)
        self.remember_workspace()
        self.write_launcher()
        self.record_server(self.port)
        return str(self.workspace)

    def onboarding(self, answers, state):
        if not self.workspace:
            self.choose_folder("documents")
        run_init(self.workspace)
        write_json(self.ws("player", "onboarding.json"), {"at": now_iso(), "answers": answers})
        if isinstance(state, dict) and state:
            state.setdefault("version", 1)
            write_json(self.ws("_system", "state.json"), state)
        answers = answers or {}
        mode = (state or {}).get("mode") or answers.get("mode") or "adult"
        skipped = bool(answers.get("skipped") or answers.get("generic"))
        intro = intro_markdown(answers, mode)
        day = today_iso()
        if intro:
            self.ws("inbox").mkdir(exist_ok=True)
            self.ws("inbox", f"{day}-intro.md").write_text(intro, encoding="utf-8")
        (self.data / ".onboarded").write_text(now_iso(), encoding="utf-8")
        text = ("Set up my tennis team from my onboarding answers (player/onboarding.json), the provisional plan in "
                "_system/state.json, and my interview in inbox/" + day + "-intro.md. Refine the plan; keep what I said.")
        if skipped:
            text = "I skipped the interview. Make a clearly labelled generic starter plan I can adjust later."
        return self.enqueue_ask(text, "onboarding", {"mode": mode}, log_user=False)

    # -- training material links (public metadata only; see describe_link)
    def sources(self):
        return read_json(self.ws("_system", "sources.json"), []) if self.workspace else []

    def add_source(self, url, member):
        src = describe_link(url)
        src.update({"member": member or "coach-analyst", "added": today_iso(), "id": uuid.uuid4().hex[:8],
                    "status": "studying"})
        items = [x for x in self.sources() if x.get("url") != url]
        items.insert(0, src)
        write_json(self.ws("_system", "sources.json"), items)
        what = {"youtube-channel": "a YouTube channel I learn from", "youtube-video": "a YouTube video",
                "doc": "a document", "web": "a web page"}[src["kind"]]
        text = (f"Add {what} to my training material: {src['title']}" + (f" by {src['author']}" if src["author"] else "")
                + f" ({url}). Please study it.")
        job = self.enqueue_ask(text, "source", {k: src[k] for k in ("id", "url", "kind", "title", "author", "member")})
        job.source_id = src["id"]
        return src, job

    def finish_study(self, sid, ok):
        """After the study pass: make sure the card never stays 'studying'."""
        items = self.sources()
        for x in items:
            if x.get("id") == sid and x.get("status") == "studying":
                x["status"] = "studied" if ok else "error"
                write_json(self.ws("_system", "sources.json"), items)
                return

    # -- queues: fast replies (read-only, parallel to writes) and one serialized writer
    def enqueue_ask(self, text, kind, fields=None, log_user=True):
        key = " ".join(str(text).lower().split())
        last = getattr(self, "_last_ask", None)
        if last and last[0] == key and time.time() - last[1] < 30 and last[2].id in self.jobs:
            return last[2]                    # same message twice (double tap, mic + Send): reuse the first job
        job = Job(kind)
        self._last_ask = (key, time.time(), job)
        self.jobs[job.id] = job
        if log_user and self.workspace:
            self.append_convo({"role": "user", "kind": kind, "text": text, "job": job.id})
        if kind == "onboarding":                     # the plan must exist before the review: one full pass
            self.q.put(("full", job, text, fields or {}))
        else:
            job.bookkeeping = "pending"
            self.fq.put((job, text, fields or {}))
        return job

    def enqueue_book(self, text, kind, fields=None):
        """Background-only work (no visible reply): the team updates files and state."""
        job = Job(kind)
        job.bookkeeping = "pending"
        job.done = True
        self.jobs[job.id] = job
        self.q.put(("book", job, text, fields or {}))
        return job

    def knowledge_action(self, action, kid, text):
        """The Head Coach page acts on one idea it knows (state.knowledge)."""
        st = self.read_state() or {}
        items = st.get("knowledge") or []
        idx = next((i for i, k in enumerate(items) if k.get("id") == kid), None)
        if action == "rebuild":
            return {"job": self.enqueue_book("Rebuild what the Head Coach knows from my coach files.", "knowledge",
                                             {"action": "rebuild"}).id}
        if idx is None:
            raise ValueError("That idea isn't in your team's notes any more.")
        item = items[idx]
        fields = {"action": action, "id": kid, "idea": item.get("text", ""), "text": text}
        if action == "question":
            q = {"id": "Q-" + uuid.uuid4().hex[:6], "text": text or f"Ask about: {item.get('text', '')}", "about": kid,
                 "added": today_iso(), "asked": False}
            done, box = self.enqueue_patch([{"op": "push", "path": "coach_questions", "value": q}])
            done.wait(10)
            return {"question": q}
        if action == "remove":
            done, box = self.enqueue_patch([{"op": "set", "path": f"knowledge.{idx}.status", "value": "removed"}])
            done.wait(10)
            return {"job": self.enqueue_book(f"Forget this idea, it's not right for me: {item.get('text', '')}",
                                             "knowledge", fields).id}
        if action == "fix":
            words = f"That's not right: \"{item.get('text', '')}\". " + (text or "")
        elif action == "test":
            words = f"I want to test this next practice: {item.get('text', '')}"
        else:
            raise ValueError("Unknown action.")
        return {"job": self.enqueue_ask(words, "knowledge", fields).id}

    def enqueue_patch(self, ops):
        done = threading.Event()
        box = {}
        self.q.put(("patch", ops, done, box))
        return done, box

    def _fast_worker(self):
        while True:
            job, text, fields = self.fq.get()
            try:
                self._fast(job, text, fields)
            finally:
                if not job.error:
                    self.q.put(("book", job, text, fields))
                else:
                    job.bookkeeping = "skipped"

    def _worker(self):
        while True:
            item = self.q.get()
            self.busy = True
            try:
                if item[0] == "patch":
                    _, ops, done, box = item
                    try:
                        st = self.read_state() or {"version": 1}
                        apply_patch(st, ops)
                        write_json(self.ws("_system", "state.json"), st)
                        box["ok"] = True
                    except Exception as exc:  # report to the page
                        box["error"] = str(exc)
                    done.set()
                elif item[0] == "full":
                    _, job, text, fields = item
                    self._full(job, text, fields)
                else:
                    _, job, text, fields = item
                    self._book(job, text, fields)
            finally:
                self.busy = False

    def _message(self, job, text, fields, extra=""):
        st = self.read_state() or {}
        mode = fields.get("mode") or st.get("mode") or "adult"
        header = f"[app] kind={job.kind} mode={mode} today={today_iso()}"
        clean = {k: v for k, v in fields.items() if k != "mode"}
        team = "\n[team settings] " + json.dumps(self.team_settings(), ensure_ascii=False)
        return header + ("\n[fields] " + json.dumps(clean, ensure_ascii=False) if clean else "") + team + extra + "\n" + text

    def _claude(self, job, message, system, tools, plugin=True, track=True):
        """Run one claude -p pass; returns (result_text or None, error or None)."""
        cmd = [self.claude, "-p", "--output-format", "stream-json", "--verbose", "--allowedTools", tools,
               "--append-system-prompt", system]
        if plugin:
            if not INSTALLED:                      # running from a checkout: load the plugin explicitly
                cmd += ["--plugin-dir", str(PLUGIN_ROOT)]
            cmd += ["--permission-mode", "acceptEdits"]
        env = dict(os.environ, TT_JOB="1")         # tells our SessionStart hook not to start another app
        result, err = None, None
        try:
            proc = subprocess.Popen(cmd, cwd=str(self.workspace), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True, bufsize=1, env=env)
            proc.stdin.write(message)
            proc.stdin.close()
            for line in proc.stdout:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if track and ev.get("type") == "assistant":
                    for item in (ev.get("message") or {}).get("content", []):
                        if item.get("type") == "tool_use":
                            self._describe(job, item.get("name"), item.get("input") or {})
                elif ev.get("type") == "result":
                    if ev.get("is_error"):
                        err = str(ev.get("result") or "Something went wrong.")
                    else:
                        result = str(ev.get("result") or "")
            proc.wait(timeout=900)
            if result is None and not err:
                lines = (proc.stderr.read() or "").strip().splitlines()
                err = lines[-1] if lines else "Your team didn't answer. Please try again."
        except Exception as exc:
            err = f"Couldn't reach your team: {exc}"
        return result, err

    def _finish_reply(self, job, result_text):
        reply, meta = split_meta(result_text)
        job.reply = reply
        for m in meta.get("members", []):
            job.member(m)
        job.next_steps = [x for x in meta.get("next_steps", []) if isinstance(x, str)][:3]
        job.state_changed = bool(meta.get("state_changed", True))
        job.say = str(meta.get("say") or "").strip() or None
        if isinstance(meta.get("settings"), dict) and self.save_team_settings(meta["settings"]):
            job.settings_changed = True
        self.append_convo({"role": "team", "kind": job.kind, "text": reply, "say": job.say, "members": job.members,
                           "next_steps": job.next_steps, "job": job.id})

    def _fast(self, job, text, fields):
        """Pass 1: a quick, read-only reply from the current state (about 15 s)."""
        job.member("head-coach")
        job.step("Listening")
        if not self.claude:
            job.error = "Claude isn't installed or signed in on this computer."
            job.done = True
            return
        recent = [c for c in self.conversation(12) if c.get("job") != job.id][-6:]
        convo = "\n[recent] " + json.dumps([{"who": c.get("role"), "text": str(c.get("text", ""))[:400]} for c in recent], ensure_ascii=False) if recent else ""
        job.step("Reading your plan")
        result, err = self._claude(job, self._message(job, text, fields, convo), FAST_MODE, "Read", plugin=False, track=False)
        if result is not None:
            self._finish_reply(job, result)
        else:
            job.error = err
            self._save_unanswered(text)
        job.done = True

    def _book(self, job, text, fields):
        """Pass 2: the team updates journal, plan, calendar and state.json in the background."""
        job.bookkeeping = "running"
        extra = "\n[replied] " + json.dumps({"reply": job.reply or "", "next_steps": job.next_steps}, ensure_ascii=False)
        sid = getattr(job, "source_id", None)
        result, err = self._claude(job, self._message(job, text, fields, extra), BOOK_MODE,
                                   STUDY_TOOLS if sid else ALLOWED_TOOLS)
        if sid:
            self.finish_study(sid, not err)
        req = self.ws("_system", "settings_request.json")
        if req.exists():                       # a setting the player asked for in words: the app owns settings.json
            self.save_team_settings(read_json(req, {}))
            req.unlink(missing_ok=True)
        if err:
            job.bookkeeping = "error"
            self._save_unanswered(text)
        else:
            job.bookkeeping = "done"
            job.state_changed = True

    def _full(self, job, text, fields):
        """Onboarding: one full pass that writes the plan and the first reply."""
        job.member("head-coach")
        job.step("Listening")
        if not self.claude:
            job.error = "Claude isn't installed or signed in on this computer."
            job.done = True
            return
        result, err = self._claude(job, self._message(job, text, fields), APP_MODE, ALLOWED_TOOLS)
        if result is not None:
            self._finish_reply(job, result)
        else:
            job.error = err
        job.bookkeeping = "done"
        job.done = True

    def _save_unanswered(self, text):
        try:
            stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
            self.ws("inbox").mkdir(exist_ok=True)
            self.ws("inbox", f"{stamp}-app-note.md").write_text(text + "\n", encoding="utf-8")
        except OSError:
            pass

    def _describe(self, job, name, inp):
        if name == "Skill":
            skill = str(inp.get("skill", "")).split(":")[-1]
            m = SKILL_MEMBER.get(skill)
            if m:
                job.member(m)
                job.step(MEMBER_STEP[m], m)
            return
        path = str(inp.get("file_path") or inp.get("path") or inp.get("pattern") or "")
        if "/skills/" in path and path.endswith("SKILL.md"):        # a skill read directly instead of via the Skill tool
            m = SKILL_MEMBER.get(Path(path).parent.name)
            if m:
                job.member(m)
                job.step(MEMBER_STEP[m], m)
            return
        if name in ("Write", "Edit"):
            for key, label, member in FILE_STEPS:
                if key in path:
                    if member:
                        job.member(member)
                    job.step(label, member)
                    return
            job.step("Saving your updates")
        elif name in ("WebSearch", "WebFetch"):
            job.member("coach-analyst")
            job.step("Reading public information about it" if name == "WebFetch" else "Searching for what they teach",
                     "coach-analyst")
        elif name in ("Read", "Glob", "Grep"):
            if "TEAM.md" in path:
                job.step("Reading your team rules")
            elif "state.json" in path or "weekly_assignments" in path:
                job.step("Checking your plan")
            else:
                job.step("Looking through your notes")


PLAYER_KEYS = ("alexintro", "player_intro", "playerintro")


def intro_markdown(answers, mode):
    """Readable interview transcript from the page's {answers, tags, words} (or a plain intro_text)."""
    if answers.get("intro_text"):
        return f"# Onboarding interview ({mode})\n\n{answers['intro_text']}\n"
    words = answers.get("words") or {}
    tags = answers.get("tags") or {}
    picked = answers.get("answers") or {}
    keys = list(dict.fromkeys(list(words) + list(tags) + list(picked)))
    if not keys:
        return ""
    lines = [f"# Onboarding interview ({mode})", "",
             "Each section is one interview question. Chips are what was tapped; Words are what was said or typed."]
    for k in keys:
        who = "PLAYER (own words)" if k.lower() in PLAYER_KEYS else ("PARENT" if mode == "parent" else "PLAYER")
        lines += ["", f"## {k} - {who}"]
        t = tags.get(k)
        if t:
            lines.append("Chips: " + (", ".join(map(str, t)) if isinstance(t, list) else str(t)))
        a = picked.get(k)
        if a not in (None, "", [], {}) and not isinstance(a, (dict, list)):
            lines.append(f"Answer: {a}")
        w = words.get(k)
        if w:
            lines.append(f"Words: {w}")
    return "\n".join(lines) + "\n"


YT_HOSTS = ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "music.youtube.com")


def describe_link(url):
    """Public metadata only. Videos use YouTube's official oEmbed endpoint; nothing is downloaded or scraped."""
    import urllib.request
    from urllib.parse import quote
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.netloc:
        raise ValueError("That doesn't look like a link. Paste the full address (https://…).")
    host = u.netloc.lower()
    src = {"url": url, "kind": "web", "title": host, "author": "", "thumb": ""}
    if host in ("docs.google.com", "drive.google.com"):
        src.update(kind="doc", title="Google " + ("Drive file" if host.startswith("drive") else
                                                    "Sheet" if "/spreadsheets/" in u.path else "Doc"))
        return src
    if host in YT_HOSTS:
        path = u.path.rstrip("/")
        if path.startswith("/@") or path.startswith("/channel/") or path.startswith("/c/") or path.startswith("/user/"):
            handle = path.split("/")[1] if path.startswith("/@") else path.split("/")[2]
            src.update(kind="youtube-channel", title=handle if handle.startswith("@") else handle, author=handle)
            return src
        src["kind"] = "youtube-video"
        try:
            with net.urlopen("https://www.youtube.com/oembed?format=json&url=" + quote(url, safe=""), timeout=8) as r:
                meta = json.loads(r.read().decode("utf-8"))
            src.update(title=meta.get("title") or "YouTube video", author=meta.get("author_name") or "",
                       thumb=meta.get("thumbnail_url") or "")
        except Exception:
            src["title"] = "YouTube video"
    return src


META_RE = re.compile(r"```tt-meta\s*(\{.*?\})\s*```", re.S)


def split_meta(text):
    meta = {}
    m = META_RE.search(text or "")
    if m:
        try:
            meta = json.loads(m.group(1))
        except ValueError:
            meta = {}
        text = (text[:m.start()] + text[m.end():]).strip()
    return text.strip(), meta


# ---------------------------------------------------------------- HTTP
def make_handler(app):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _local(self):
            """Only this computer's own pages may talk to the app (blocks DNS-rebinding and cross-site requests)."""
            host = (self.headers.get("Host") or "").split(":")[0]
            if host not in ("127.0.0.1", "localhost"):
                return False
            origin = self.headers.get("Origin")
            return not origin or urlparse(origin).hostname in ("127.0.0.1", "localhost")

        def _ok(self, q):
            if not self._local():
                return False
            return secrets.compare_digest(q.get("t", [""])[0] or self.headers.get("X-Token") or "", TOKEN)

        def _send(self, status, body, ctype="application/json"):
            data = body if isinstance(body, bytes) else (body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", ctype + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")          # the URL holds the token: never leak it to other sites
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)

        def _body(self):
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_BODY:
                return None
            try:
                return json.loads(self.rfile.read(n) or b"{}")
            except ValueError:
                return {}

        def do_GET(self):
            u = urlparse(self.path)
            q = parse_qs(u.query)
            if u.path == "/api/ping":
                return self._send(200, {"ok": True})
            if not self._ok(q):
                return self._send(403, "Open Pocket Tennis Team from Claude or the launcher in your Tennis folder.", "text/plain")
            if u.path == "/":
                if not PAGE.exists():
                    return self._send(503, "The Pocket Tennis Team app page is missing. Reinstall the plugin.", "text/plain")
                html = PAGE.read_text(encoding="utf-8")
                boot = "<script>window.TT_BOOT = " + json.dumps(app.boot()).replace("</", "<\\/") + ";</script>"
                i = html.find("<script")
                html = html[:i] + boot + "\n" + html[i:] if i >= 0 else html + boot
                return self._send(200, html, "text/html")
            if u.path == "/api/state":
                return self._send(200, {"ready": app.ready(), "workspace": str(app.workspace) if app.workspace else None,
                                        "onboarded": app.onboarded(), "sources": app.sources(),
                                        "state": app.read_state() if app.onboarded() else None,
                                        "conversation": app.conversation(), "settings": app.settings(),
                                        "busy": app.busy, "today": today_iso()})
            if u.path == "/api/voice":
                return self._send(200, app.voice.public())
            if u.path.startswith("/api/job/"):
                job = app.jobs.get(u.path.rsplit("/", 1)[-1])
                return self._send(200, job.as_dict()) if job else self._send(404, {"error": "unknown job"})
            if u.path == "/plan":
                if not app.workspace:
                    return self._send(404, "No plan yet.", "text/plain")
                page = app.ws("My Tennis Plan.html")
                if not page.exists():
                    return self._send(404, "No plan yet: tell your coach about a practice first.", "text/plain")
                html = page.read_text(encoding="utf-8")
                data = app.ws("_system", "plan-data.js")
                if data.exists():
                    html = html.replace('<script src="_system/plan-data.js"></script>',
                                        "<script>" + data.read_text(encoding="utf-8").replace("</", "<\\/") + "</script>")
                return self._send(200, html, "text/html")
            return self._send(404, {"error": "not found"})

        def do_POST(self):
            u = urlparse(self.path)
            if not self._ok(parse_qs(u.query)):
                return self._send(403, {"error": "forbidden"})
            b = self._body()
            if b is None:
                return self._send(413, {"error": "too large"})
            if u.path == "/api/voice/setup":
                return self._send(200, app.voice.start_setup())
            if u.path == "/api/voice":
                return self._send(200, app.voice.save(b))
            if u.path == "/api/tts":
                try:
                    audio, ctype = app.voice.tts(b.get("text"), b.get("voice"), b.get("speed"))
                except LookupError as exc:
                    return self._send(409, {"error": str(exc)})
                except Exception as exc:
                    return self._send(500, {"error": str(exc)})
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(audio)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(audio)
                return
            if u.path == "/api/knowledge":
                if not app.workspace:
                    return self._send(409, {"error": "Choose a folder first."})
                try:
                    return self._send(200, app.knowledge_action(str(b.get("action", "")), str(b.get("id", "")),
                                                                str(b.get("text", "")).strip()[:600]))
                except ValueError as exc:
                    return self._send(400, {"error": str(exc)})
            if u.path == "/api/source":
                if not app.workspace:
                    return self._send(409, {"error": "Choose a folder first."})
                try:
                    src, job = app.add_source(str(b.get("url", "")).strip(), b.get("member"))
                except ValueError as exc:
                    return self._send(400, {"error": str(exc)})
                return self._send(200, {"source": src, "job": job.id})
            if u.path == "/api/folder":
                try:
                    return self._send(200, {"workspace": app.choose_folder(b.get("choice", "documents"), b.get("path"))})
                except Exception as exc:
                    return self._send(500, {"error": f"Couldn't create that folder: {exc}"})
            if u.path == "/api/settings":
                flag = app.data / "no-autoopen"
                if "autoOpen" in b:
                    if b["autoOpen"]:
                        flag.unlink(missing_ok=True)
                    else:
                        flag.write_text(now_iso(), encoding="utf-8")
                if app.workspace:
                    if isinstance(b.get("team"), dict):
                        app.save_team_settings(b["team"])
                    s = read_json(app.ws("_system", "settings.json"), {})
                    s.update({k: v for k, v in b.items() if k not in ("autoOpen", "team")})
                    write_json(app.ws("_system", "settings.json"), s)
                return self._send(200, app.settings())
            if not app.workspace and u.path != "/api/onboarding":
                return self._send(409, {"error": "Choose a folder first."})
            if u.path == "/api/onboarding":
                job = app.onboarding(b.get("answers") or {}, b.get("state") or {})
                return self._send(200, {"job": job.id})
            if u.path == "/api/ask":
                text = str(b.get("text", "")).strip()[:8000]
                if not text:
                    return self._send(400, {"error": "empty message"})
                job = app.enqueue_ask(text, str(b.get("kind") or "free"), b.get("fields") or {})
                return self._send(200, {"job": job.id})
            if u.path == "/api/state":
                done, box = app.enqueue_patch(b.get("patch") or [])
                done.wait(timeout=1.5)
                if not done.is_set():
                    return self._send(202, {"queued": True})
                return self._send(200 if box.get("ok") else 400, box)
            return self._send(404, {"error": "not found"})

    return H


def main():
    ap = argparse.ArgumentParser(description="Pocket Tennis Team app server")
    ap.add_argument("--workspace")
    ap.add_argument("--here")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--open", action="store_true")
    ap.add_argument("--data-dir")
    args = ap.parse_args()

    app = App(args)
    server = None
    for port in range(args.port, args.port + 30):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(app))
            break
        except OSError:
            continue
    if not server:
        sys.exit("No free port.")
    app.port = server.server_address[1]
    app.record_server(app.port)
    if app.workspace and app.ready():
        app.remember_workspace()
        app.write_launcher()
    url = f"http://127.0.0.1:{app.port}/?t={TOKEN}"
    print(f"TENNIS_TEAM_URL {url}", flush=True)

    def stop(*_):
        try:
            sj = read_json(app.data / "server.json", {})
            if sj.get("pid") == os.getpid():
                (app.data / "server.json").unlink(missing_ok=True)
        finally:
            os._exit(0)

    signal.signal(signal.SIGTERM, stop)
    if args.open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        stop()


if __name__ == "__main__":
    main()
