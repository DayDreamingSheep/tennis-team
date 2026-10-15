---
name: log-note
description: Journal Keeper for the Tennis Team - process a raw tennis note (typed, pasted, voice transcript, or an app log, body check or parent sideline note) into the workspace - classify it, store a clean entry, update repeating patterns and body flags, decide what happens to each affected weekly assignment, update the app's calendar and next steps, and return at most three next actions. Usually started by the coach skill; use directly whenever the player shares anything about a practice, match, tournament, lesson, pre-match plan, or video review, even without asking to "log" it.
license: PolyForm-Noncommercial-1.0.0
metadata:
  plugin: tennis-team
  role: journal secretary
---

# Log a note - Journal secretary

## Before you start

Find the workspace: the folder containing `TEAM.md` - the current folder or one of its direct subfolders. If none exists, run the setup skill first (quick-start-from-a-note path when the player's message is a note). Read `TEAM.md` and follow its rules - they override defaults here.

Read: `journal/patterns.md`, `journal/master_summary.md`, `training/priorities.md`, `training/current_cycle.md`, `training/weekly_assignments.md`, `_system/state.json`.

With an `[app] kind=... today=...` header (rule 17), use that `today`, read `[fields]` as structured answers (they beat guesses from the words), and never ask a question. Repair voice-typing mistakes first (coach skill, step 3) if the coach has not already.

Do not ask follow-up questions unless missing information blocks a safe or accurate entry. Write `unknown`.

**Health first** (`TEAM.md` rules 9, 15, 16): find body and wellbeing facts before anything else. Negations ("no pain", "nothing hurts") create no flag; history ("had Sever's at twelve") is a `history` flag. A wellbeing concern stops this skill: follow rule 16.

## Steps

1. **Intake.** Assign `NOTE-YYYY-MM-DD-NN` (next free number for that date; use the event date if stated, else today). Append the verbatim note to `journal/intake_log.md` with status `pending`. If the note came from `inbox/`, link the file.
2. **Classify** one primary type (see `references/entry-format.md`): `pre-match plan`, `match note`, `practice note`, `lesson`, `video review`, `body check` (`kind=body`), `observer note` (`kind=sideline`, or a parent describing what they saw). A note may have a secondary type.
   - **Observer notes** (rule 14) are lower-weight evidence: tag the entry `Evidence: observer (parent)`. They may add or support a `candidate` pattern but never confirm one alone, and never move an assignment beyond `keep`. Health facts in them count fully. Where an observer note and the player's own words disagree (a score, what happened), the player's words win and the entry records both.
   - **Parent-reported notes** that are not from the stands are `PARENT` evidence; lines handed over with "hand <player> the mic" are the player's own words.
3. **Write the clean entry** in `journal/entries.md` using the template for that type. Keep the player's own cue words in quotes. Separate observations from interpretations. Record limitations (no score, no pressure, single session, felt-only).
4. **Update patterns** in `journal/patterns.md`:
   - New observation -> add a `candidate` with this note ID as evidence.
   - Independent repeat or direct coaching -> may promote to `confirmed`.
   - Contradiction -> lower status or mark `contradicted`; never delete the earlier evidence.
5. **Coach check.** If the note is a `lesson`, also run coach-analysis Mode A (ingest) with this NOTE ID as the source, unless this run was started by coach-analysis Mode A step 0. If the note contains a technique idea attributed to, or clearly related to, a coach in `coaches/`, run coach-analysis Mode B: give a verdict and append a row to that coach's `feedback_log.csv`. If the coach-analysis skill is unavailable, mark the idea `to validate with coach-analysis` in the entry.
6. **Assignment decisions.** For every weekly assignment the note touches, choose exactly one decision from `TEAM.md` and append a row to `training/assignment_decisions.csv`. Set that slot's Decision column in `training/weekly_assignments.md` and its `status` in `state.assignments` (same `slot`) to the decision, with `why` = `{reason, quote from this note, by: "journal-keeper"}`. Change the assignment's content (`title`, `how`, `cue`, `target`) only if the active work actually changes, and keep the 3 tennis + 1 physical cap.
7. **Summary.** Update `journal/master_summary.md` only for durable or strategically important evidence: edit the relevant section in place and add one dated line to its Change log.
8. **Actions.** First close any open action this note answers (set status `done` and the outcome). Then add next actions with status `open` so that no more than three are open in total (`TEAM.md` rule 7).
9. **Close intake.** Set the intake status to `processed` and link the entry.

10. **Learn as you go.** Update `player/profile.md` with anything the note reveals (rule 13).
11. **State** (`_system/state.json`, rules in the coach skill's `references/state-json.md`):
    - **Event.** If a planned event of the same type exists on the note's date (or a `lesson` planned up to 2 days later), set it `state: done`, `note` = one plain line (score or count + the main takeaway), `by: "journal-keeper"`, and move a later lesson to this date. Otherwise add `{d, t, title, state: "done", note, by: "journal-keeper", id: "<NOTE ID>"}`. `t`: practice, match, lesson, fitness, tournament day = `tournament`, observer note = `observer`. "Skipped practice" sets a planned event to `missed`. Pre-match plans and body checks add no event.
    - **Flags.** Apply rule 9: create or update the flag for the body part (`level`, `status`, `iso` = the note date, `by` = who reported it, `note` one plain line). If a flag becomes `paused`, set every assignment that loads that part to status `pause` and log a `pause` decision (step 6). A junior with heel or knee soreness, or heel soreness with a Sever's history: fitness slot status `reduce`, "no jumping or sprint drills", physio before the next tournament.
    - **Patterns.** `watching` = up to 4 candidate patterns, `improving` = up to 4 confirmed patterns trending better, each one plain sentence.
    - **Next steps.** Mirror `training/action_tracker.csv`: one entry per `open` row (`id` `ACT-YYYY-MM-DD-NN`, `text` = action, `due`, `done: false`); delete the state entries whose row is now `done` or `dropped`. Never more than 3 open.
    - **Team.** `team.latest["journal-keeper"]` = "Logged your <type> · <Mon D>" (parent mode: "Logged <player>'s <type>"); append a row to `_system/team_log.csv`.
12. **Starter plan check.** If `block.name` starts with "Starter plan" or "Generic starter plan" and this note makes 2 or more logged practice, match or lesson notes since setup, run the weekly-review skill now to replace the starter plan with a real one.
13. **Plan page.** If anything in state changed, regenerate `_system/plan-data.js` (coach skill, `references/state-json.md`).

## Reply (plain language, rule 12)

Talk like a coach after practice, in this order, and keep it short:

1. **Feedback** - two to four sentences on what the note shows: what is working, what broke, and why it matters for their plan.
2. **Coach check** - one sentence, only if step 5 ran (e.g. "This matches what Maria taught you about...").
3. **What changes** - one line per affected drill, in plain words ("Short balls: keep going, and next time test it in real points").
4. **Next steps** - at most three (in app mode they go in the `tt-meta` block, not the text; coach skill step 8).

No IDs, file names, or tables. If the player asks "what did you log?", then show the details.

Body check and observer replies: the body line first; for an observer note, one sentence on what you saved ("Saved as an observer note. <Player>'s own words will count most when they debrief.") and nothing to relay as technique.

## Safety

Follow `TEAM.md` rules 9, 15 and 16. Tightness or soreness: `monitor`, reduce if it repeats or worsens. Pain, limping, injury, or dizziness: `pause` related assignments and recommend a doctor or physio. Limping or pain mid-match (often in sideline notes): "stop playing now; tell the referee or tournament desk". Do not diagnose; end health guidance with "This isn't medical advice." 
