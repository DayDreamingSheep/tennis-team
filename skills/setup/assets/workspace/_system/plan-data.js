/*
  Data for "My Tennis Plan.html". The Tennis Team rewrites this whole file after each update.
  Rules: plain, friendly language. No IDs (NOTE-, PAT-, DR-), file names, or jargon such as P0 or "validate".
  player: "" if the name is unknown. Dates like "Oct 19".
  status_kind: new | keep | level-up | simplify | rest | swap | test
  Shape of the object assigned below (every key optional except player/updated):
  {
    "player": "Sam", "updated": "Oct 15",
    "goal": { "dream": "Play college club tennis", "target": "Reach NTRP 4.0", "by": "Oct 2027",
              "measure": "Win 60% of league matches at 4.0", "three_month": "Beat the top seed in my 3.5 flight" },
    "roadmap": [{ "when": "Oct - Dec", "title": "Build a second serve you trust", "focus": "Second serve, short balls",
                  "status": "now" }],            // status: done | now | next | later
    "focus": "This block's main goal in one sentence", "cycle_progress": "Week 1 of 4",
    "block_goals": ["Second serve lands deep 7/10 under pressure"],
    "week_of": "Oct 19",
    "assignments": [{ "area": "Top priority - Short balls", "title": "...", "how": "...",
                      "cue": "...", "target": "7 out of 10", "status": "New this week", "status_kind": "new" }],
    "cues": ["..."], "improving": ["..."], "watching": ["..."], "health": "", "next_steps": ["..."],
    "tournaments": [{ "name": "Fall Club Championship", "date": "Nov 8", "days_to_go": 24, "format": "3.5 singles",
                      "goal": "Win two rounds", "status": "upcoming", "result": "",
                      "guide": { "before": ["..."], "match_day": ["..."], "between_points": ["..."],
                                 "game_plan": ["..."], "after": ["..."] } }],   // status: upcoming | played
    "team_activity": [{ "member": "journal-keeper", "did": "Logged your doubles match", "when": "Oct 15" }]
  }
  member ids: head-coach, team-manager, journal-keeper, coach-analyst, progress-coordinator,
              strategy-coach, tournament-coach
*/
window.PLAN_DATA = {
  "player": "",
  "updated": "{{DATE}}",
  "week_of": "",
  "goal": {},
  "roadmap": [],
  "focus": "Tell your coach about your next practice or match to get your first plan.",
  "cycle_progress": "",
  "assignments": [],
  "cues": [],
  "improving": [],
  "watching": [],
  "health": "",
  "next_steps": ["Tell your coach how your next practice or match went - talk or type, any words."],
  "tournaments": [],
  "team_activity": []
};
