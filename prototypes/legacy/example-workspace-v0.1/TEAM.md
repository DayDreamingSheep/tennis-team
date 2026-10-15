# Tennis Team workspace

Created 2026-10-15. This folder is the player's coaching memory. Every tennis-team skill reads this file first and follows these rules.

## Map

```text
player/profile.md               Who the player is and wants to become
journal/intake_log.md           Verbatim raw notes with IDs (append only)
journal/entries.md              Cleaned, structured entries (append only)
journal/patterns.md             Repeating patterns with evidence status
journal/master_summary.md       Current durable picture of the player
training/priorities.md          Ranked P0/P1/P2 development areas
training/current_cycle.md       The active 3-6 week cycle
training/weekly_assignments.md  This week's small assignment set
training/drill_library.md       Drills available (inactive until assigned)
training/assignment_decisions.csv  Every keep/progress/... decision
training/action_tracker.csv     Next actions and their outcomes
coaches/<slug>/                 Evidence and verdicts for one coach
inbox/                          Drop zone for voice memos / notes (processed automatically)
My Tennis Plan.html             The player's plan page (static; reads _system/plan-data.js)
_system/                        Plan data and templates used by the team
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
9. **Health.** Tightness or soreness = `monitor`: record it, keep load, and reduce if it worsens or repeats. Pain, injury, or dizziness = `pause` related work and point to qualified guidance. The team does not give medical advice.
10. **IDs.**
    - Notes `NOTE-YYYY-MM-DD-NN`; weekly reviews `REVIEW-YYYY-MM-DD`; setup interview evidence `SETUP-YYYY-MM-DD`.
    - Patterns `PAT-NNN`; drills `DR-NNN`; cycles `CYCLE-YYYY-MM-THEME` (THEME = one uppercase word, e.g. `SHORTBALL`).
    - Coach slug = lowercase-hyphenated name without titles (`Coach Maria Lopez` -> `maria-lopez`); its ID prefix is the slug uppercased (`MARIA-LOPEZ`).
    - Coach evidence `<PREFIX>-DIRECT-NNN`, `<PREFIX>-PLAYER-NNN`, `<PREFIX>-PUB-NNN`; principles `<PREFIX>-P01`; hypotheses `<PREFIX>-H01`.
11. **Dates and CSVs.** "Week of" is the Monday of that week. In CSVs, separate multiple IDs with `|` and double-quote any field containing a comma.

12. **Plain language to the player.** Files stay precise; replies and the plan page use coach talk. Never show IDs, file names, CSVs, or folder paths unless the player asks. Translate:
    - P0 -> "top priority"; P1 -> "next priority"; P2 -> "later"
    - `new` -> "new this week"; `keep` -> "keep going"; `progress` -> "level up"; `reduce` -> "simplify"; `pause` -> "rest it"; `replace` -> "swap it"; `validate` -> "test it in real points"
    - candidate pattern -> "something we're watching"; confirmed -> "a proven pattern"
    - plan-page `status_kind` uses: new, keep, level-up, simplify, rest, swap, test
13. **Learn as you go.** Setup asks at most four questions. Unknown profile fields are filled from notes over time: update `player/profile.md` whenever a note reveals level, equipment, style, schedule, goals, or health. A weekly review may end with one optional question about the most useful missing field; nothing else asks profile questions.

## Coaches

| Slug | Name | Relationship (in person / online / book) |
|---|---|---|
| maria | Coach Maria | in person (weekly lesson) |
