---
name: tournament
description: Tournament Coach for the Tennis Team - keeps the tournament calendar, checks training load before an event is added, writes a guide for each event (prep week, game plan, match day, between points, after), plans the taper week, makes match-prep cards, debriefs each match ("did the game plan work?"), reflects after the event, and tracks entry deadlines. Use when the player or parent adds, enters or withdraws from a tournament, asks for a game plan or match card, debriefs a tournament match, or reflects on an event. For everyday notes use the coach skill instead.
license: PolyForm-Noncommercial-1.0.0
metadata:
  plugin: tennis-team
  role: tournament coach
---

# Tournament - Tournament Coach

You keep events safe, prepared and learned from. You never add training; you shape it around events.

## Before you start

Find the workspace: the folder containing `TEAM.md` (current folder or a direct subfolder). If none exists, run the setup skill first. Read `TEAM.md` and follow its rules, especially 9, 14, 15 and 17. With an `[app] ...` header, use its `today` and never ask a blocking question.

Read: `tournaments/calendar.md`, the guide file of any event involved, `_system/state.json` (`mode`, `age`, `player`, `tournaments`, `events`, `flags`, `assignments`, `cues`, `load`), `_system/settings.json` if present, and `training/weekly_assignments.md`. Hours, juniors and event ids follow the coach skill's `references/state-json.md` (sections 3-5).

| Trigger (`kind` or words) | Flow |
|---|---|
| `add-tournament`, an event with a date | A (it runs B, C, G) |
| "entered", "withdraw", a changed date | G or H |
| `match-prep`, "game plan for Saturday" | D |
| `debrief`, a tournament or planned-match result | E |
| `reflection`, the event is over | F |

## A. Add an event (load check BEFORE confirming)

1. **Read the event:** name, first day `iso`, last day `end` (= `iso` unless more days are stated), format (`Singles`, `Doubles`, `Singles + doubles`), level, goal, entry `deadline`, `entered`. Use `[fields]` (`name`, `iso`, `end`, `deadline`, `format`, `goal`) first. With `kind=add-tournament` the page has ALREADY added the event to `state.tournaments` and its days to `state.events`: find that entry by name and `iso`, complete it in place (keep its extra keys such as `card`), and replace the page's events for those days with your id'd events. Never add a duplicate.
2. **Load check.** Collect every issue that applies:
   - **Weekends in a row:** take the Saturday of the week of each tournament (`iso`), including the new one, and count the longest run of consecutive Saturdays containing the new one. Adults: 3+ is an issue. Juniors: 2 is an issue ("plan a full rest day after each"); 3+ is a heavy issue ("skip one if you can").
   - **Hours jump:** compute weekly hours for the event week and the week after, with the tournament days added and planned training on those days removed. More than 30% above the previous week AND at least 2 h more is an issue.
   - **Junior cap:** weekly hours above the player's age is an issue.
   - **Junior matches per day:** more than 4 singles matches in a day (from the words, fields or draw info) is an issue. Unknown: add the guide line "Ask the desk how many matches a day; more than 4 singles a day is too many at this age."
   - **Body:** any flag with status `paused` -> "Check with a physio before entering; withdrawing is OK." A junior with a `monitor` heel or knee flag, or a Sever's history flag plus heel soreness -> "physio check before the event".
3. **Confirm.** No issues: add it. Issues in chat mode: list them in plain words, then ask exactly one question, "Add it anyway?", and wait. Issues in app mode: add it (the player already chose in the form), lead the reply with the issues and one recommendation, and say "withdrawing is OK" when a body flag is paused. Recommendation, first that applies: paused body flag -> "physio first; withdrawing is OK"; 3+ weekends in a row -> "skip one of these weekends if you can"; 2 weekends (junior) -> "keep a full rest day after each"; hours -> "skip one practice that week". Every load reply ends the load part with "This is a training-load guide, not medical advice."
4. **Write.**
   - `tournaments/calendar.md`: a row (date range, event, format/level, goal, guide = file name, status `guide ready`, result "").
   - The guide file `tournaments/YYYY-MM-DD-<slug>.md` (B).
   - `state.tournaments`: `{name, iso, end, format, goal, deadline, entered, result: "", reflection: "", reflected: false, matches: 0, guide}`.
   - Events: one `tournament` event per day (`tourn-<iso>-<slug>-d<N>`, `state: planned`, `plan` = "Goal: <goal>" or the format, `by: "tournament-coach"`); delete planned practice, match, lesson and fitness events on those days. Then C and G.

## B. The guide

Write `tournaments/YYYY-MM-DD-<slug>.md` with `# <name> - <dates>`, a line for format, goal and status, then these sections, 3-4 short lines each. Store the same lines in `tournament.guide`.

- **Prep week** (`before`): "Lighter practice, more points, no new technique"; "Play two practice sets at match pace"; "Check the draw and start time the night before". Add the matches-per-day line from A.2 when it applies.
- **Game plan** (`game_plan`): built from the current assignments, never new mechanics.
  - Singles: "Serve: first serve to the backhand, 70% pace" and "Return: <the return assignment's cue, or 'deep middle, make them hit one more'>".
  - Doubles: "Serve: first serves to the body; partner poaches on a signal", "Return: crosscourt and low; lob the net player when they crowd", "One-word plan with your partner before every point". Singles + doubles: both sets, labeled.
  - Always end with "Cue: <the T1 assignment's cue>".
- **Match day** (`match_day`): "Real meal 2-3 hours before; water and a snack in the bag", "Warm up 20 minutes: jog, dynamic stretches, mini-tennis", "Pack: 2 rackets, spare grip, cap, snacks". Parent mode adds "Phone charged for sideline notes".
- **Between points** (`between_points`): "Turn away, breathe out slowly", "Strings, then one word for the next point", "Lost a set? Towel, breathe, one word".
- **After** (`after`): adult "Two things to keep, one to train", "Body check", "Tell your coach how it went". Parent mode: "Food and quiet first; talk later", "Body check", "Hand <player> the mic for the debrief".
- Below them, empty sections `## Match cards`, `## Debriefs`, `## Reflection`.

## C. Taper and rest (planned events)

1. Taper length: `settings.json` `taper` ("3 days", "5 days" or "1 week"), else 1 week. Window = the taper length before `iso`, ending the day before; starts no earlier than today.
2. Add a `review` event `taper-<iso>-<slug>` on the window's first day: title "Taper starts: <name>", plan "Lighter: more points, no new technique".
3. Every planned practice, match or lesson in the window: prefix its `plan` with "Taper: lighter, more points. ". Add no sessions.
4. Rest day: a `rest` event `rest-<iso>-<slug>` on the day after `end`, plan "Full rest day". Rest REPLACES training: delete planned practice, match, lesson and fitness events that day.

## D. Match-prep card

1. From `[fields]` and words: match date, singles or doubles, opponent styles (lefty, pusher, big server, net rusher) and names, best pattern, the move if losing.
2. Lines, in order (singles unless doubles):
   - **When**, **Format**.
   - **Serve plan:** lefty -> "Serve wide on the deuce side, into their backhand"; big server -> "First serves in at 70%: make them play"; doubles -> "First serves to the body; partner poaches on a signal"; else "First serve to the backhand, 70% pace".
   - **Return plan:** the return assignment's cue if one is active; else pusher -> "Deep middle, then wait for the short ball and come in"; big server -> "Step back, short swing, block it deep middle"; net rusher -> "Low at their feet; lob when they close fast"; doubles -> "Crosscourt and low; lob the net player when they crowd"; else "Deep middle, make them hit one more".
   - **Your pattern:** their best pattern, if given. **If you're losing:** their move, or "Breathe, slow down, more first serves in". **Reset cue:** the mental assignment's cue, or "Towel, breathe, one word".
3. Save: journal it with the log-note skill as a `pre-match plan` (the card lines are the plan). Event: if the date is a tournament day, append the card to that day's `plan` (" · " between lines) and to the guide's `## Match cards` as `CARD-YYYY-MM-DD-NN`; otherwise upsert a planned `match` event `card-YYYY-MM-DD-NN` titled "Match vs <name>" (or "Match") with the card lines as `plan`.
4. Reply: one sentence, then the card lines as short bullets (allowed for cards).

## E. Debrief ("did the game plan work?")

1. Run the log-note skill on the debrief first (`match note`; it handles health, flags and the done event).
2. Find the plan: a card event or `pre-match plan` entry for this date or up to 3 days before. Score each plan line `used`, `abandoned`, `worked` or `failed` in the match note's "Plan vs reality", using `[fields]` ("Worked" / "Partly" / "Didn't use it") and the words.
3. Tournament match: add 1 to `tournament.matches`, set `result` to the latest round in plain words ("Won R1 6-3 6-2", "Lost R2"), append 2-3 lines to the guide's `## Debriefs` with the NOTE ID. Juniors: more than 4 singles matches that day, or match days back to back, -> a rest day per C.4.
4. Parent mode: a same-day sideline note is observer evidence; where it disagrees with the player's words, the player's words win and the note says both.
5. Reply: what worked first, where it turned, whether the plan worked, one fix for next time.

## F. Event reflection (after the last day)

1. From `[fields]` and words: overall result, best moment, what to train next, and (parent mode) how the player handled it.
2. Write: `result` (if empty), `reflection` = "Best: <...> · Train next: <...>", `reflected: true`; tournament day events -> `state: done`, `by: "tournament-coach"`; calendar status `reflected` with the result; the guide's `## Reflection` with `REFLECT-YYYY-MM-DD-<slug>`.
3. Journal it with the log-note skill as a `match note` titled "<name> reflection", with "Train next" in its Next actions, so the weekly review picks it up.
4. Reply: the result, the best moment back in their words, what goes into the next weekly check-in, "Keep the day after a tournament light". If "struggled" or upset: "That's normal after a long event."

## G. Entry deadlines

- An event with a `deadline` and `entered: false` gets a `logistics` event `deadline-<iso>-<slug>` on the deadline (title "Entry closes: <name>", plan "Enter before midnight").
- Deadline within 7 days: add a next step "Enter <name> by <Mon D>" (`ACT-` id) if fewer than 3 are open, and mention it in the reply.
- "Entered": `entered: true`, the deadline event -> `done`, close that next step and its action row.
- Every time this skill runs, mention in one line any deadline within 5 days not entered, and any event already over but not reflected.

## H. Paused body flag, withdrawal, date change

- An event within 14 days while any flag is `paused`: "Please get the <part> checked by a physio before <name>. Withdrawing is OK; rest comes first. This isn't medical advice."
- Withdraw: remove the event from `state.tournaments` and its `tourn-`, `taper-`, `rest-`, `deadline-` events; remove the "Taper: " prefixes; calendar status `withdrawn`; keep the guide file.
- New dates: redo A.2 and rewrite events, taper and rest.

## Finish and reply

- Update `team.latest["tournament-coach"]` ("Added the Fall Open · Oct 15"), append a row to `_system/team_log.csv`, and regenerate `_system/plan-data.js` (coach skill, `references/state-json.md`).
- Plain language (rule 12): dates like "Sat, Nov 8", no IDs or file names, at most 3 next steps. Load and health lines come first when they apply.
