---
name: setup
description: Create or repair a Pocket Tennis Team workspace, the private folder that acts as the player's long-term coaching memory, with the least possible effort from the player, and turn the Pocket Tennis Team app's onboarding answers into the first real plan. Usually started by the coach skill (including the app's "[app] kind=onboarding" job). Use directly when the player says "start my tennis team", "set up my tennis coach", or when another tennis-team skill cannot find TEAM.md.
license: PolyForm-Noncommercial-1.0.0
allowed-tools: Bash(python3:*)
metadata:
  plugin: tennis-team
  role: team manager
---

# Setup - Team manager

Goal: the player is coaching-ready in under a minute. Ask as little as possible; learn the rest from their notes over time (rule 13 of `TEAM.md`).

## 1. Choose the location (do not ask)

- **App onboarding** (`[app] kind=onboarding`): the app already created the workspace in the current folder. Skip steps 1-2 unless `TEAM.md` is missing; then go to section 6.
- If the current folder or one of its direct subfolders contains `TEAM.md`, this is a repair. Add only missing files, never overwrite existing ones, report what was added in one line, and stop.
- If the current folder is empty or clearly meant for tennis, use it.
- Otherwise create a subfolder named `My Tennis Team/` and use that.

## 2. Copy the templates

Run the bundled script. It copies every template in under a second, fills in today's date, and never overwrites existing files:

```bash
python3 "<this skill's folder>/scripts/init_workspace.py" "<workspace path>"
```

If Python is unavailable (app runs have no shell), copy everything under `assets/workspace/` (next to this SKILL.md) yourself with the file tools, keeping the structure and including `_system/`, and replace `{{DATE}}` with today's date (YYYY-MM-DD).

## 3. Learn about the player - pick ONE path

App onboarding always uses section 6 instead of Path A or B.

### Path A - quick start from a note (preferred when available)

The player's first message is already a tennis note. Ask nothing.

1. Infer what you can for `player/profile.md` (level, backhand type, style, problems, health). Write `unknown` for everything else.
2. Treat the note's problems as the point-losers, and the note as evidence `SETUP-YYYY-MM-DD`.
3. Finish step 4, then process the same note with the log-note skill so it is journaled normally.

### Path B - quick-start questions

Send exactly this, one message, then wait:

> Let's set up your tennis team. Four quick questions - answer any you like, skip the rest:
> 1. What should I call you, and roughly what level are you? (e.g. beginner, club player, NTRP 3.5, UTR 6)
> 2. One-handed or two-handed backhand?
> 3. What loses you the most points right now?
> 4. Anything hurting or injured that I should know about?

Use whatever they answer. Everything unanswered is `unknown`. Do not ask follow-ups.

## 4. Fill the first state

The setup information is evidence `SETUP-YYYY-MM-DD`; cite it wherever setup creates something.

- **Profile.** Write `player/profile.md`.
- **Priorities.** Draft `training/priorities.md` with `TEAM.md` rule 2. If no problem is known yet, use a starter P0 of "footwork and early preparation" and mark it `starter - replace after first notes`.
- **Patterns.** Add each known problem and strength to `journal/patterns.md` as a `candidate`.
- **Cycle.** Fill `training/current_cycle.md` with a 3-4 week cycle (`CYCLE-YYYY-MM-THEME`) aimed at the top P0.
- **Drills and assignments.**
  - Add one drill per planned assignment to `training/drill_library.md`.
  - Fill `training/weekly_assignments.md` with one to three tennis slots (fewer is fine when little is known) and at most one `PHY` slot.
  - Give each slot a cue, a measurable success signal, and decision `new`.
  - Follow rule 9 for health.
- **Master summary.** Fill the sections you can, keeping at most three cues.
- **Actions.** Add one or two `open` actions, typically "tell your coach about your next practice - include a score or count if you can".
- **Coaches.** For each coach mentioned, add a row to the Coaches table in `TEAM.md` and copy `_system/coach/` to `coaches/<slug>/`.
- **Goal.** If a goal or target is known, run the strategy skill (set the goal, then draw the roadmap).
- **Tournaments.** For each upcoming event named, run the tournament skill's add flow.
- **State.** Write `_system/state.json` from what you just filed (shape and rules: the coach skill's `references/state-json.md`): names, level, age, `block` (name "Starter plan, adjusted after your first 2 sessions"), `week_of`, `assignments` with `why`, `cues`, `watching`, `flags`, `next_steps`, planned events from any schedule you know (section 6, step 6), and `team.latest["team-manager"]` = "Set up your team · <Mon D>".
- **Plan page.** Write `_system/plan-data.js` from state as described in that reference. `My Tennis Plan.html` already exists from step 2.

## 5. Reply (plain language, rule 12)

Keep it short and warm:

- One sentence: the team is ready, and where the folder is.
- "This week" as two or three bullets: what to practice and the cue to use.
- Mention **My Tennis Plan** (the page in their folder) once.
- Close with: "After your next practice or match, just tell me how it went, in any words. Say **help** anytime to see what I can do."

Do not list files, IDs, or folder structure.

## 6. App onboarding (`kind=onboarding`)

Before the job, the app wrote `player/onboarding.json`, a provisional `_system/state.json` built by the page's simple local rules, and a readable transcript `inbox/<date>-intro.md`. **Refine, never replace:** keep every provisional value the evidence supports, change only what the words show is wrong, and keep every key you do not own or do not understand (for example `assignments[].why.who`, `tournaments[].card`).

1. **Read the intro file first** (the readable one): one `## <questionKey> - PARENT|PLAYER` section per question, each with `Chips:`, `Answer:` and `Words:` lines; a section marked `PLAYER (own words)` (key `alexintro`) is the player speaking. Then read `player/onboarding.json` for exact values: `{"at", "answers": {"flow", "generic", "answers": {key: value}, "tags": {key: [chips]}, "words": {key: text}}}`. Keys vary (level, goal, lose, matches, when, body, coach, else, names, alexintro...); use every one you understand. `generic: true` = the interview was skipped (step 9). Repair voice-typing mistakes first (coach skill, step 3).
2. **Evidence.** All onboarding material is `SETUP-YYYY-MM-DD`. Append the intro text verbatim to `journal/intake_log.md` under that ID with status `processed`, linked to the inbox file, so it is never processed again. If the intro describes a specific recent match or practice with details (a score, a day), also journal that part with the log-note skill.
3. **Parent mode** (`mode: "parent"`, rule 14). Sections marked `PARENT` are `PARENT` evidence; the `PLAYER (own words)` section ("hand <player> the mic") is `PLAYER` evidence and outranks them. If it is missing, `goal.player_goal` stays `unknown`; the player's intro may arrive later as `kind=free` with `[fields] {"player_intro": true}` (coach skill routes it). Profile facts from the parent get "(reported by parent)". Where the two disagree, the player's words win and both go into `journal/patterns.md`.
4. **Priorities and assignments.** Rank the named point-losers with rule 2 (how often they cost points, else the player's order). Map each to an area. Areas that are nobody's named problem, and gaps, follow this order: P0 footwork and ball reading, returns, backhand protection; P1 serve plus first forehand, weak-ball early timing, inside-out forehand, net, big-point reset. For each provisional assignment:
   - **Confirm** it if a named problem supports it; **adjust** `k`, `area`, `title`, `how`, `cue`, `target` if the words show a different or higher-ranked problem. Keep at most 3 tennis + 1 fitness (`k: "phy"`). Every status is `new`.
   - Set `why` = `{reason, quote, by}`: `reason` one plain sentence ("Top priority: returns cost you the most points."); `quote` = the exact words from the answers or intro that support it, never invented, "" if none; `by` = `progress-coordinator` (`head-coach` for a starter focus chosen without evidence).
   - Health (rules 9, 15): set `flags` from the body answer and words. Pain now -> the fitness slot becomes "Paused: rest the <part>", status `pause`. Junior heel or knee soreness, or a Sever's history -> fitness slot "Low impact only: no jumping or sprint drills", status `reduce`, `why.reason` says a physio check comes before the next tournament.
5. **Starter label.** `block` = `{id: "CYCLE-YYYY-MM-THEME", name: "Starter plan, adjusted after your first 2 sessions", start: today, end: today + 27 days, goals: 1-2 from the assignment targets}`; `week_of` = this week's Monday; `cues` = the assignment cues (max 3); `watching` = each problem as a short plain sentence.
6. **Planned events for the coming week** (today through today + 6) from the schedule answers: one event per playing day, `id` `plan-YYYY-MM-DD-<t>`, `t` = practice, match or lesson, `state: planned`, title "Practice" / "League match" / "Lesson with <coach>", `plan` = "Your one thing: <T1 cue>", `by: "progress-coordinator"`. Lessons "every other week" go in this week. Replace provisional planned training in that window; keep anything else. No schedule -> no events.
7. **Run the other members:** strategy (goal + roadmap; parent mode records the family goal and the player's own goal), tournament add flow for each upcoming event (it skips ones already added), coach folders for each coach named (step 4, Coaches).
8. **Write every file** of step 4 (profile, priorities, patterns, cycle, drills, weekly assignments, master summary, actions, coaches), then `_system/state.json`, then `_system/plan-data.js`. Add 1-2 next steps (`ACT-` ids, same text as the action rows), e.g. "After your next practice: tell your coach how it went".
9. **Skipped interview** (`generic: true`, or the words say the interview was skipped): one footwork assignment, title "Split step and an early first step on every ball", `why.reason` "Generic starter focus: we don't know your game yet, so we start with footwork, which helps every shot.", `by: "head-coach"`, plus a mobility fitness slot; `block.name` = "Generic starter plan, adjusted after your first 2 sessions"; no goal, no roadmap.
10. **Reply** (app mode, under 120 words): one warm sentence welcoming them by name; the top one or two things this week with their cue; any health line first; "This is a starter plan; I'll adjust it after your first 2 sessions." No question.
