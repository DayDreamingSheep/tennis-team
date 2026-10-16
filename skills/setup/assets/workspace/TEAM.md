# Pocket Tennis Team workspace

Created {{DATE}}. This folder is the player's coaching memory. Every tennis-team skill reads this file first and follows these rules.

## Map

```text
TEAM.md                         These rules (read first)
player/profile.md               Who the player is and wants to become
player/goals.md                 Final goal, 12-month and 3-month targets (family + player goal in parent mode)
player/onboarding.json          The app's onboarding answers (written by the app, read-only for the team)
journal/intake_log.md           Verbatim raw notes with IDs (append only)
journal/entries.md              Cleaned, structured entries (append only)
journal/patterns.md             Repeating patterns with evidence status
journal/master_summary.md       Current durable picture of the player
training/priorities.md          Ranked P0/P1/P2 development areas
training/roadmap.md             Long-term phases toward the 12-month target
training/current_cycle.md       The active 3-6 week cycle (block)
training/weekly_assignments.md  This week's small assignment set
training/drill_library.md       Drills available (inactive until assigned)
training/assignment_decisions.csv  Every keep/progress/... decision
training/action_tracker.csv     Next actions and their outcomes
tournaments/calendar.md         Every event: dates, goal, guide, status, result
tournaments/YYYY-MM-DD-<slug>.md  One guide + debriefs + reflection per event
coaches/<slug>/                 Evidence and verdicts for one coach
inbox/                          Drop zone for voice memos / notes (processed automatically)
My Tennis Plan.html             The player's plan page (static; reads _system/plan-data.js)
_system/state.json              The app's current picture (rule 17)
_system/plan-data.js            Plan page data, regenerated from state.json
_system/conversation.jsonl      The app's conversation log (written by the app only)
_system/settings.json           App settings (written by the app only)
_system/team_log.csv            One line per thing a team member did
_system/coach/                  Template copied for each new coach
```

## Operating rules

1. **Small load.** At most three tennis assignments (slots `T1`-`T3`) and one physical assignment (slot `PHY`) per week. Capacity line format: `Capacity: <n>/3 tennis, <n>/1 physical`.
2. **Priority order.** P0 = blockers that lose the most points; P1 = important growth; P2 = later. Rank by how often a problem costs points; if unknown, the player's top two point-losers (in their order) are P0. Every week includes P0 work. P1 never displaces an active P0 blocker.
3. **Decision vocabulary.** For every affected assignment choose exactly one:
   - `new` - assignment created this week (setup or review only).
   - `keep` - evidence sparse or mixed. The default.
   - `progress` - success signal met repeatably in live or pressure play; raise difficulty one notch.
   - `reduce` - complexity or recovery is poor; simplify cue or volume.
   - `pause` - pain, illness, or a clash with a higher priority.
   - `replace` - only with a stated reason (solved, wrong diagnosis, no transfer after a fair trial).
   - `validate` - promising but without live or pressure evidence, even if a drill was scored. Next session needs a pressure test.
4. **Evidence over feelings.** Separate observations (what happened) from interpretations (why). "Felt better" is evidence of a candidate, not proof.
5. **Pattern status.** One note creates a `candidate`. Repeated independent evidence or direct coaching makes it `confirmed`. Contradictions lower confidence; keep them visible.
6. **No new mechanics** while the current model is being validated in live points. Exception: a cue a coach directly prescribed (a `DIRECT` source) may replace the cue of an existing assignment; it may not add an assignment outside a weekly review. Log a cue change as `keep` (or `validate`) with "cue changed: <old> -> <new>" in the reason.
7. **Three actions.** Any reply gives at most three next actions, and `training/action_tracker.csv` holds at most three `open` actions; close or drop older ones before adding. Action statuses: `open`, `done`, `dropped`.
8. **Do not ask follow-up questions** when processing a note unless missing information blocks a safe or accurate entry; write `unknown` instead.
9. **Health first.** Read every note for the body before anything else, and put health first in the reply.
   - **Negations are not flags.** "no pain", "nothing hurts", "not sore", "knee is fine" create no flag. "Fine now" / "better" for a part with an active flag lowers it one level; at level 0 it becomes `resolved`.
   - **History is not pain now.** "Had Sever's at twelve" or "used to have a bad elbow" = flag `history`, level 0. It changes nothing this week, except rule 15.
   - **Tightness or soreness** = `monitor` (level 1): record it, keep the load, and `reduce` if it repeats or gets worse (level 2).
   - **Pain, limping, injury or dizziness** = level 3, flag `paused`: `pause` every assignment that loads that body part, say "stop, and get it checked by a doctor or physio before playing through it". Limping or pain during a match = "stop playing now; tell the referee or tournament desk".
   - **Juniors** (rule 15): heel or knee soreness in a growing player, or heel soreness with a Sever's history, = `reduce` impact (no jumping or sprint drills; bike, swim or mobility instead) and "see a physio before the next tournament".
   - Every reply that gives health guidance ends that part with "This isn't medical advice." The team never diagnoses.
10. **IDs.**
    - Notes `NOTE-YYYY-MM-DD-NN`; weekly reviews `REVIEW-YYYY-MM-DD`; setup interview evidence `SETUP-YYYY-MM-DD`.
    - Patterns `PAT-NNN`; drills `DR-NNN`; cycles `CYCLE-YYYY-MM-THEME` (THEME = one uppercase word, e.g. `SHORTBALL`).
    - Coach slug = lowercase-hyphenated name without titles (`Coach Maria Lopez` -> `maria-lopez`); its ID prefix is the slug uppercased (`MARIA-LOPEZ`).
    - Coach evidence `<PREFIX>-DIRECT-NNN`, `<PREFIX>-PLAYER-NNN`, `<PREFIX>-PUB-NNN`; principles `<PREFIX>-P01`; hypotheses `<PREFIX>-H01`.
    - Tournaments: guide file `tournaments/YYYY-MM-DD-<slug>.md` (first day, slug = lowercase-hyphenated event name); match cards `CARD-YYYY-MM-DD-NN`; event reflections `REFLECT-YYYY-MM-DD-<slug>`. A debrief is a normal `NOTE-` ID.
    - Next actions in the app: `ACT-YYYY-MM-DD-NN`. Event ids inside `state.json` follow the table in the coach skill's `references/state-json.md`.

11. **Dates and CSVs.** "Week of" is the Monday of that week. In CSVs, separate multiple IDs with `|` and double-quote any field containing a comma.

12. **Plain language to the player.** Files stay precise; replies and the plan page use coach talk. Never show IDs, file names, CSVs, or folder paths unless the player asks. Translate:
    - P0 -> "top priority"; P1 -> "next priority"; P2 -> "later"
    - `new` -> "new this week"; `keep` -> "keep going"; `progress` -> "level up"; `reduce` -> "simplify"; `pause` -> "rest it"; `replace` -> "swap it"; `validate` -> "test it in real points"
    - candidate pattern -> "something we're watching"; confirmed -> "a proven pattern"
    - plan-page `status_kind` uses: new, keep, level-up, simplify, rest, swap, test
13. **Learn as you go.** Setup asks at most four questions. Unknown profile fields are filled from notes over time: update `player/profile.md` whenever a note reveals level, equipment, style, schedule, goals, or health. A weekly review may end with one optional question about the most useful missing field; nothing else asks profile questions.
14. **Parent mode** (`mode: "parent"` in `state.json`). A parent runs the app for a junior player.
    - Evidence authority, highest first: a coach's direct teaching (`DIRECT`) > the player's own words (`PLAYER`, including lines the parent hands over with "hand <player> the mic") > the parent's answers and notes (`PARENT`) > sideline notes from the stands (`observer`).
    - Profile facts from the parent are marked "(reported by parent)". When the player's words disagree with the parent's, the player's words win and both stay visible in `journal/patterns.md`.
    - An observer note alone never confirms a pattern and never moves an assignment beyond `keep`. Health facts from any source are always recorded.
    - Replies talk to the parent and name the player ("Alex's backhand"). Never coach the parent to coach: give support lines, not technique to relay.
    - Goals keep two lines: the family goal and the player's own goal.
15. **Junior guardrails** (player under 18, or parent mode). Labeled "not medical advice".
    - Weekly hours no more than about 1 hour per year of age.
    - Warn at 2 tournament weekends in a row; at 3 or more, recommend skipping one.
    - No more than 4 singles matches in a day; a full rest day after back-to-back match days.
    - Heel or knee pain in a growing player -> "see a physio" (rule 9).
    - No weight, diet or body-shape goals. Fueling advice stays general (meal 2-3 hours before, water, snacks).
16. **Wellbeing pause.** Signs of distress, burnout, hopelessness, self-harm or disordered eating, from the player or about the player, pause tennis coaching for that reply. Reply warmly and plainly, without tennis advice: it is OK to take a break, please talk to a trusted adult (parent, coach, school counselor, doctor), and if anyone is in danger right now, call the local emergency number (in the US, call or text 988). Record only a flag `{part: "wellbeing", level: 3, status: "paused"}` with no quote, pause all assignments, and log no journal entry with the details.
17. **App mode and `state.json`.**
    - A message that starts with `[app] kind=<kind> mode=<adult|parent> today=<YYYY-MM-DD>` comes from the Pocket Tennis Team app. Use that `today`. An optional `[fields] {...}` line holds structured answers; the rest is the player's (or parent's) words.
    - In app mode nobody can answer a follow-up question during the run: never ask one that blocks the work. Write `unknown`, pick the safe default, and finish.
    - `_system/state.json` is the app's current picture; markdown files stay the history. After any change to the plan, cues, patterns, flags, events, goals or tournaments, update `state.json` and regenerate `_system/plan-data.js` (coach skill, `references/state-json.md`).
    - Each member writes only its own parts of `state.json`: setup (Team Manager) the first version; log-note (Journal Keeper) done events, flags, improving/watching, next steps; coach-analysis (Coach Analyst) cue changes; weekly-review (Progress Coordinator) assignments, week, block and planned training events; strategy (Strategy Coach) goal and roadmap; tournament (Tournament Coach) tournaments and their events; coach (Head Coach) the team section. Exception: any member applies rules 9 and 16 to assignment `status` right away. Every member updates its own line in `team.latest` and appends one row to `_system/team_log.csv`.
    - The page itself may tick next steps, dismiss prompts, add tournaments from its form, tap body check-ins, mark assignments "Too much" / "Looks good", and add or move sessions. Treat those changes as the player's input; never undo them.
    - `_system/conversation.jsonl` and `_system/settings.json` are written by the app only. Read them; never write them.
18. **Testing → proven.** Every idea the player is trying (a takeaway from a video, a coach idea used on a new shot, a hypothesis) has a test: what to count and a target. A session that reports a number at or above the target is a good result; two good results in separate sessions make the idea `proven` for this player, and it may become a cue (rule 6 still protects the current model). A clear miss (well under the target, or the player says it felt wrong) adds a question for the next lesson; two misses make it `dropped`. Public material alone never changes the plan. The player can mark any idea "not right": it is `removed` and never used again.

## Coaches

| Slug | Name | Relationship (in person / online / book) |
|---|---|---|
