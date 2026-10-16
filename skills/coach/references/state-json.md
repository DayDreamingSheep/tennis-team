# `_system/state.json`: the app's current picture

Markdown and CSV files stay canonical for history and evidence. `_system/state.json` is the current picture the app renders. Every tennis-team skill that changes the plan, cues, patterns, flags, events, goals or tournaments updates this file in the same run, then regenerates `_system/plan-data.js` (section 6).

## 1. Shape

All keys are optional except `version` and `mode`. Dates are ISO `YYYY-MM-DD`. Keep keys you do not own exactly as you found them, including keys not listed here (the page adds some, e.g. `assignments[].why.who`, `tournaments[].card`).

```json
{
  "version": 1,
  "mode": "adult",
  "player": "Sam", "parent": "", "coach": "Maria", "academy": "",
  "level": "NTRP 3.5", "age": null,
  "goal": { "dream": "", "target": "NTRP 4.0", "by": "2027-10", "measure": "", "three_month": "",
            "family": "", "player_goal": "", "why": { "quote": "", "by": "strategy-coach" } },
  "roadmap": [ { "when": "Oct – Dec", "title": "", "focus": "", "status": "now" } ],
  "block": { "id": "CYCLE-2026-10-RETURNS", "name": "", "start": "2026-10-12", "end": "2026-11-08",
             "goals": [ { "t": "", "ok": false } ] },
  "week_of": "2026-10-12",
  "assignments": [ { "k": "return", "slot": "T1", "level": "top", "area": "Top priority · Returns",
                     "title": "", "how": "", "cue": "", "target": "", "status": "new",
                     "why": { "reason": "", "quote": "", "by": "progress-coordinator" } } ],
  "cues": [""],
  "improving": [""], "watching": [""],
  "events": [ { "d": "2026-10-17", "t": "practice", "title": "", "state": "planned", "plan": "", "note": "", "by": "", "id": "" } ],
  "tournaments": [ { "name": "", "iso": "2026-11-08", "end": "2026-11-08", "format": "", "goal": "", "deadline": null,
                     "entered": false, "result": "", "reflection": "", "reflected": false, "matches": 0,
                     "guide": { "before": [], "game_plan": [], "match_day": [], "between_points": [], "after": [] } } ],
  "flags": [ { "part": "left knee", "level": 1, "iso": "2026-10-15", "status": "monitor", "by": "Sam", "note": "" } ],
  "next_steps": [ { "id": "", "text": "", "due": "2026-10-17", "done": false } ],
  "knowledge": [ { "id": "PRIYA-P-001", "text": "", "label": "coach", "from": "Priya", "src": "Lesson · Oct 9",
                   "cue": "", "in_plan": true, "status": "active",
                   "test": { "how": "", "target": "", "need": 2, "results": [ { "d": "2026-10-11", "ok": true, "note": "7/10" } ] } } ],
  "fitness": { "limits": [ { "id": "FIT-2026-10-15-01", "text": "", "part": "", "by": "", "since": "", "until": "until cleared", "status": "active" } ],
               "watch": [], "program": { "name": "", "days": [], "src": "" }, "felt": [] },
  "coach_questions": [ { "id": "", "text": "", "about": "PRIYA-P-001", "added": "2026-10-15", "asked": false } ],
  "team": { "active": ["head-coach", "journal-keeper", "progress-coordinator", "strategy-coach"],
            "latest": { "journal-keeper": "Logged your practice · Oct 15" } },
  "load": { "weekly_hours": { "2026-10-12": 6 } },
  "prompts_dismissed": { "id": "2026-10-16T10:00" }
}
```

## 2. Field rules

- `mode`: `adult` or `parent`. Never change it; the page sets it.
- `assignments`: at most 3 tennis (`slot` T1-T3) + 1 fitness (`k: "phy"`, `slot: "PHY"`). `k` is one of `footwork`, `return`, `backhand`, `serve`, `forehand`, `net`, `mental`, `phy`. `level`: `top` (P0), `next` (P1), `later` (P2). `status` uses the decision words: `new`, `keep`, `progress`, `reduce`, `pause`, `replace`, `validate`. Every assignment has `why` = `{reason, quote, by}`: `reason` is one plain sentence, `quote` is the player's (or parent's) exact words or "", `by` is a member id. `area` is plain text such as "Top priority · Returns".
- `cues`: at most 3, the same cues as the master summary's cue stack.
- `improving` / `watching`: at most 4 each, plain sentences. `improving` = confirmed patterns getting better; `watching` = candidate patterns.
- `events[].t`: `practice`, `match`, `lesson`, `fitness`, `tournament`, `review`, `rest`, `observer`, `logistics`. `state`: `planned`, `done`, `missed`. `by` is a member id.
- `flags[].status`: `monitor`, `paused`, `resolved`, `history`. `level`: 0 none/history, 1 tight or a little sore, 2 sore and getting worse or repeating, 3 pain, limping or injury.
- `next_steps`: at most 3 with `done: false`. `text` equals the `action` column of the matching row in `training/action_tracker.csv`.
- `team.latest`: one plain line per member, "<what> · <Mon D>", e.g. "Added the Fall Open · Oct 15".
- `load.weekly_hours`: key = the Monday of the week; value = planned + done hours (section 4).
- `prompts_dismissed`: written only by the page. Never edit it.
- `knowledge`: what the Head Coach knows about the player's tennis, one item per principle or hypothesis in `coaches/<slug>/` (plus general tips the team relies on). `id` = the principle or hypothesis ID in the coach files (general tips: `GEN-NN`). `text` is one plain sentence (max 110 characters). `label`, strongest first:
  - `coach`: taught to this player by a real coach (`DIRECT` evidence).
  - `proven`: tested on court and it held up (see `test`).
  - `testing`: the player's takeaway from a video, a coach idea applied somewhere new, or any hypothesis with a test running.
  - `public`: from public material only (study notes). Background reading; never changes the plan alone.
  - `general`: general tennis knowledge.
  `from` = the coach or channel name, `src` = a short plain source ("Lesson · Oct 9", "Your takeaway from an Olivari video", "Study notes"). `cue` = the cue words when it is one of the active cues; `in_plan` = true when an assignment uses it. `status`: `active`, `dropped` (tested and it didn't work for this player, kept for history) or `removed` (the player said it's wrong; never use it again). `test` (for `testing` and `proven`): `how` = what to count, `target` = e.g. "7/10", `need` = good sessions to prove it (2), `results` = one per session that tried it. Owners: coach-analysis adds, relabels and removes items; log-note appends `test.results` and makes the promotion (TEAM.md rule 18); weekly-review checks it.
- `fitness`: owned by the fitness skill (shape and rules there). `limits` with `status: "active"` bind every teammate: weekly-review, tournament and log-note never plan or suggest work that breaks one.
- `coach_questions`: questions to bring to the next lesson. The page adds them ("Ask my coach about this"); skills add one when a test clearly misses. Set `asked: true` once a lesson note answers it.

## 3. IDs inside state

| Thing | `id` format | Written by |
|---|---|---|
| Training session planned by the plan | `plan-YYYY-MM-DD-<t>` | setup, weekly-review |
| Logged session (done) | the note ID, `NOTE-YYYY-MM-DD-NN` | log-note |
| Tournament day | `tourn-YYYY-MM-DD-<slug>-d<N>` (start date of the event, day number) | tournament |
| Taper start | `taper-YYYY-MM-DD-<slug>` | tournament |
| Rest day after an event | `rest-YYYY-MM-DD-<slug>` | tournament |
| Entry deadline | `deadline-YYYY-MM-DD-<slug>` | tournament |
| Match card | `card-YYYY-MM-DD-NN` | tournament |
| Next step | `ACT-YYYY-MM-DD-NN` | the skill that adds it |

`<slug>` = the event name lowercase-hyphenated (`Fall Junior Open` -> `fall-junior-open`). A tournament is identified by its `iso` plus `name`. Events the page added have no `id`; leave them alone unless they are planned training on a rest or tournament day (then delete them).

## 4. Hours (for every load check)

Hours per event: practice 1.5, match 1.5, lesson 1, fitness 0.5, tournament 4 per day. rest, review, observer, logistics = 0. Weekly hours = the sum over Monday-Sunday of all events whose `state` is not `missed`.

- **Jump:** a week's hours are more than 30% above the previous week's AND at least 2 hours more. Skip the jump check when the previous week has 0 hours (nothing planned or logged yet).
- **Junior cap** (section 5): weekly hours above the player's age in years (about 1 h per year of age).

## 5. Who is a junior

The player is a junior when `mode` is `parent` or `age` is below 18. If `mode` is `parent` and `age` is null, use 14 for the hours cap and say "about" in replies.

## 6. Writing state.json and plan-data.js

1. Read the whole `_system/state.json`. If it is missing or empty, start from `{"version": 1, "mode": "adult"}`.
2. Change only the fields your skill owns (`TEAM.md` rule 17). Merge lists by `id` (events, next steps) or by `iso` + `name` (tournaments) or `part` (flags, ignoring "left"/"right"); never drop entries you did not write.
3. Write the whole file with the file write tool as strict JSON: double quotes, no comments, no trailing commas, `null` not `None`. Then read it back once and confirm it starts with `{` and every bracket closes.
4. Rewrite `_system/plan-data.js` entirely. Keep the comment block at its top unchanged (copy it from the current file), then one `window.PLAN_DATA = {...};` built from state.json:

| PLAN_DATA key | From |
|---|---|
| `player`, `updated` | `state.player` (or ""), today as "Oct 15" |
| `goal` | `state.goal` with `by` as "Oct 2027" (drop `why`, `family`, `player_goal` unless set) |
| `roadmap` | `state.roadmap` |
| `focus`, `cycle_progress`, `block_goals` | `block.name` (or the cycle goal), "Week N of M" from `block.start`/`end`, `block.goals[].t` |
| `week_of` | `state.week_of` as "Oct 12" |
| `assignments` | each assignment with `status` translated (rule 12) and `status_kind` |
| `cues`, `improving`, `watching` | same keys |
| `health` | one plain line for flags with status `monitor` or `paused`, else "" |
| `next_steps` | `text` of next steps with `done: false` |
| `tournaments` | upcoming and last 2 played: `date` "Nov 8", `days_to_go`, `status` `upcoming` or `played`, `guide` without `when` |
| `team_activity` | one row per `team.latest` entry: `{member, did, when}` |

Use the file write tool, not shell commands. plan-data.js must stay valid JavaScript: strings in double quotes, inner quotes as `\"`.
