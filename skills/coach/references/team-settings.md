# Team settings: how each teammate works

The player sets these on the Adjust pages of the app (or by saying so, for example "make my plan more aggressive"). The app saves them under `team` in `_system/settings.json` and adds them to every app job as a `[team settings] {...}` line. In chat mode, read `_system/settings.json` yourself; anything missing uses the default (marked *). Never write `settings.json`; only the app does. When the player asks in words to change a setting, write the change to `_system/settings_request.json` (for example `{"planner": {"pace": "Aggressive"}}`, same keys and values as below) and the app saves it after the run.

Settings change how the team works inside the rules of `TEAM.md`. They never override:
- the caps of 3 tennis assignments and 1 fitness assignment (rule 1);
- health first (rules 9 and 15);
- the evidence rules (rules 4, 5 and 18).

## Planner (`planner`, owned by weekly-review and strategy)

| Key | Values | What it changes |
|---|---|---|
| `pace` | `Gentle`, `Steady`*, `Aggressive` | See the pace table below. |
| `drills` | `1`, `2`, `3`* | The most tennis assignments per week. Fewer is fine when the evidence is thin. |
| `days` | `2`, `3`, `4`*, `5+` | Tennis days per week to plan. Count lessons and matches the player already has first, then add practices up to this number. |
| `day` | `Sunday`*, `Monday` | Which day the weekly review is due. |
| `check` | `Monthly`*, `Every block` | How often strategy runs the roadmap check-in. |
| `fitness` | `true`*, `false` | `false` = no `PHY` assignment. Health-related mobility a physio asked for stays anyway. |

**Pace:**

| | Gentle | Steady | Aggressive |
|---|---|---|---|
| Level up (`progress`) after | 3 good sessions | 2 good sessions | 1 strong session (clearly above target), or 2 good ones |
| New targets | Same or a little easier | One step up | A bigger step up (for example 6/10 → 8/10) |
| Tennis assignments | At most 2, even if `drills` allows 3 | Up to `drills` | Up to `drills` |
| Rest | An extra easy day after a match | Normal | Normal; never fewer than one rest day a week |
| Fitness block | 1 short session | 2 short sessions | Up to 3 short sessions |
| Goal and roadmap (strategy) | Milestones can slide later without a fuss | As set | Bring milestones forward by up to a third when the evidence supports it, and say so |

**Limits on Aggressive:**
- A junior (parent mode, or a player under 18) is always treated as Steady. The app already sends it that way, with `junior_cap: true`.
- Any `monitor` or `paused` health flag makes the week Steady until it clears.

When pace or `drills` changes, the next weekly review re-plans with it. If the player asked for the change in a message, re-plan this week's planned sessions in the same run and record a decision for each changed assignment in `training/assignment_decisions.csv`, with the reason "Planner setting: <value>".

## Journal Keeper (`journal`, owned by log-note)

| Key | Values | What it changes |
|---|---|---|
| `focus` | any of `Technique`*, `Tactics`, `Mental side`, `Body` | Each entry gets a short "Focus" line on each chosen area (what the note shows about it, or "nothing this time"). Patterns in these areas are checked first. |
| `followup` | `Just save it`*, `One follow-up`, `Dig deeper` | `Just save it`: the reply asks nothing. `One follow-up`: the reply may end with one optional question about a focus area. `Dig deeper`: up to two optional questions. Rule 8 still holds: never a question that blocks the work. |
| `tone` | `Short and direct`*, `Encouraging` | How the journal feedback in the reply reads. |
| `exact` | `true`*, `false` | Keep the player's original words in `journal/intake_log.md` next to the clean entry. |
| `inbox` | `true`*, `false` | Pick up notes from the `inbox/` folder. |

## Tournament Coach (`tournament`, owned by tournament)

| Key | Values | What it changes |
|---|---|---|
| `taper` | `3 days`, `5 days`, `1 week`* | How long before an event training gets lighter (the taper event). |
| `remind` | `1 week`, `2 weeks`*, `1 month` | When the entry-deadline next step comes due, counted back from the deadline. |
| `plans` | `Before every match`*, `Tournaments only` | Whether league and practice matches also get a match card. |
| `scout` | `true`*, `false` | Add an opponent-scouting checklist to each guide. |
| `ask_after` | `true`*, `false` | Add a "tell me how it went" next step for the day after each event. |

## Head Coach (`coach`, every reply)

| Key | Values | What it changes |
|---|---|---|
| `tone` | `Encouraging`, `Balanced`*, `Straight-talking` | The voice of replies. |
| `length` | `Short`*, `Detailed` | `Detailed` adds one or two sentences on why. Spoken replies stay short either way. |
| `ask_score` | `true`*, `false` | One gentle reminder when a note has no numbers. |
