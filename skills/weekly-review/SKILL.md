---
name: weekly-review
description: Progress Coordinator for the Pocket Tennis Team - run the player's weekly tennis progress review - read the week's journal evidence, judge each active assignment against its success signal, decide keep/progress/reduce/pause/replace/validate, set next week's small assignment set and planned sessions (rest days and load limits included), and update the cycle, summary and the app's plan. Use when the player asks for a weekly review, "what should I work on next week", "how is my progress", or at the end of a training cycle.
license: PolyForm-Noncommercial-1.0.0
metadata:
  plugin: tennis-team
  role: progress coordinator
---

# Weekly review - Progress coordinator

Find the workspace: the folder containing `TEAM.md` - the current folder or one of its direct subfolders. If none exists, run the setup skill first (quick-start-from-a-note path when the player's message is a note). Read `TEAM.md` and follow its rules.

## Read

- Entries in `journal/entries.md` logged since the last review (the latest row in `training/assignment_decisions.csv` whose `report_id` starts with `REVIEW-`), regardless of their event date. With no earlier review, include every entry.
- `journal/patterns.md`, `journal/master_summary.md`
- `training/priorities.md`, `training/current_cycle.md`, `training/weekly_assignments.md`
- `training/assignment_decisions.csv`, open rows in `training/action_tracker.csv`
- Recent rows of every `coaches/*/feedback_log.csv` and open hypotheses
- `_system/state.json` (`assignments`, including any "Too much" / "Looks good" marks the page added; `events`; `flags`; `tournaments`; `load`; `block`; `mode`; `age`), reflections in `tournaments/` since the last review ("Train next"), and the Check-ins table in `training/roadmap.md`

With an `[app] ... today=...` header use that `today` and ask no question except the optional one in Reply step 6.

If there are no new entries (including a review on the same day as setup), say so and keep every assignment. Still set `Week of` in `training/weekly_assignments.md` and `week_of` in state to this week's Monday, so the review is not triggered again, plan the coming week's events (Write, step 6), and write no decision rows. Give one action: log at least one scored session this week.

## Decide

1. Summarize evidence by priority. Separate outcomes (scores, counts, results) from interpretations (feelings).
2. For each active assignment, compare evidence with its success signal and choose one decision using the definitions in `TEAM.md` rule 3. Default to `keep` when evidence is sparse.
3. Choose next week's set in priority order: max three tennis (`T1`-`T3`) + one physical (`PHY`). At least one slot is P0. New slots get decision `new`. Pick drills from `training/drill_library.md`, or add new drills there first (`DR-NNN`). Cue changes follow `TEAM.md` rule 6.
4. Check the cycle: if progress criteria are met or the cycle end date has passed, propose the next cycle theme; otherwise keep it.
5. Reconcile patterns (promote/weaken with evidence IDs), refresh the master summary's "Current performance read" and "Current decisions", and keep the cue stack at three cues or fewer. Preserve contradictions.
6. **Serve the roadmap.** Apply any open recommendation in the roadmap's Check-ins table. Weekly work must serve the `now` phase: every tennis slot is a P0 area or one of the phase's focus areas. Then run the strategy skill's check-in if `Last checked` in `training/roadmap.md` is 28 or more days ago, or the block's end date has passed.
7. **Player feedback from the app.** An assignment marked "Too much" = evidence for `reduce` (simplify the cue or halve the volume). "Looks good" = the player accepts it; it is not performance evidence.
7b. **Ideas being tested.** For `state.knowledge` items with `label: "testing"`, check this week's results. A `proven` idea that fits the current focus may become a cue next week (rule 6). An idea with no attempt in two weeks gets one next step to try it, or is left alone if the plan is full.
8. **Starter plan.** If `block.name` starts with "Starter plan" or "Generic starter plan" and 2 or more sessions are logged, replace it with a real cycle (step 4) and a real block name.

## Write

- Append one decision row per slot to `training/assignment_decisions.csv` with `report_id` = `REVIEW-YYYY-MM-DD`.
- Rewrite `training/weekly_assignments.md` for the coming week: `Week of` = the Monday of the current week (or of next week if today is Sunday), and keep the capacity line valid.
- Update `training/current_cycle.md` only if focus, dates, criteria, or status changed.
- Close, drop, or carry over open actions in `training/action_tracker.csv`, so that no more than three stay open in total.

- **State** (`_system/state.json`, rules in the coach skill's `references/state-json.md`):
  1. `assignments` = the new set (max 3 tennis + 1 `phy`), each with `slot`, `k`, `level`, `area`, `title`, `how`, `cue`, `target`, `status` = this review's decision, and `why` = `{reason: one plain sentence from the evidence, quote: the player's exact words from the week's notes or "", by: "progress-coordinator"}`. Health pauses and reductions (rules 9, 15) stay in force.
  2. `week_of` = the same Monday as the file; `cues` = the cue stack; `block` = `{id, name, start, end, goals: [{t, ok}]}` from `training/current_cycle.md` (`ok: true` for criteria met).
  3. **Planned events for the coming week** (Monday-Sunday of the new `week_of`): delete planned events with `plan-` ids in that week, then add one per usual session, copying the weekday and type of last week's training events (planned or done) and the schedule in `player/profile.md`; lessons follow their cadence. `id` `plan-YYYY-MM-DD-<t>`, `state: planned`, `plan` = "Your one thing: <cue of the slot it serves>", `by: "progress-coordinator"`. Inside a taper window (from a `taper-` event up to its tournament's first day) prefix `plan` with "Taper: lighter, more points. ". Never touch `tourn-`, `taper-`, `rest-`, `deadline-` or `card-` events, or done events.
  4. **Rest days REPLACE training.** On every `rest` day (planned rest, the day after a tournament, a junior's day after back-to-back match days) delete planned practice, match, lesson and fitness events; never add rest on top of training. No training on tournament days.
  5. **Hours check** (section 4 of the reference): compute the coming week's hours. If they jump more than 30% (and at least 2 h) above last week, or a junior's hours exceed their age, delete planned sessions, the one serving the lowest-priority slot first, until it fits, and say so in the reply. Store `load.weekly_hours[<Monday>]` for last week and the coming week.
  6. `next_steps` mirrors the open rows of `training/action_tracker.csv` (max 3, `ACT-` ids); `team.latest["progress-coordinator"]` = "Planned your week of <Mon D>"; append a row to `_system/team_log.csv`.
- Regenerate `_system/plan-data.js` (coach skill, `references/state-json.md`).

## Reply (plain language, rule 12)

Write it like a coach's weekly check-in:

1. **How the week went** - two or three sentences, with the strongest evidence in plain words.
2. **What's getting better / what we're watching** - a few bullets.
3. **Next week** - one line per drill: what, the cue, and the target, plus the plain-language status ("keep going", "level up", ...).
4. **One thing to test with your coach** - only if a coach idea is waiting to be tested.
5. **Next steps** - at most three.
6. Optionally, one question to fill the most useful missing profile field (rule 13).

In chat mode end with: "Your plan page is updated - open **My Tennis Plan** in your tennis folder." In app mode keep it under 120 words and put next steps in the `tt-meta` block (coach skill step 8). Show the decision table with IDs only if the player asks for details.
