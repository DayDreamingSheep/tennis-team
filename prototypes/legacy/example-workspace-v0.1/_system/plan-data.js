/*
  Data for "My Tennis Plan.html". The Tennis Team rewrites this whole file after each update.
  Rules: plain, friendly language. No IDs (NOTE-, PAT-, DR-), file names, or jargon such as P0 or "validate".
  player: "" if the name is unknown. Dates like "Oct 19".
  status_kind: new | keep | level-up | simplify | rest | swap | test
  Shape of the object assigned below:
  {
    "player": "Sam", "updated": "Oct 15", "week_of": "Oct 19",
    "focus": "This block's main goal in one sentence", "cycle_progress": "Week 1 of 4",
    "assignments": [{ "area": "Top priority - Short balls", "title": "...", "how": "...",
                      "cue": "...", "target": "7 out of 10", "status": "New this week", "status_kind": "new" }],
    "cues": ["..."], "improving": ["..."], "watching": ["..."], "health": "", "next_steps": ["..."]
  }
*/
window.PLAN_DATA = {
  "player": "Sam",
  "updated": "Oct 15",
  "week_of": "Oct 19",
  "focus": "Build a second serve that can't be attacked, and make moving in on short balls your default.",
  "cycle_progress": "Week 2 of 4",
  "assignments": [
    {
      "area": "Top priority - Second serve",
      "title": "Brushed second serves to the body, then under pressure",
      "how": "20 brushed second serves aimed at the body, then 10 serves pretending it's 30-30",
      "cue": "Brush up, body, less pace",
      "target": "14 out of 20 in and at the body; 7 out of 10 in at 30-30",
      "status": "Test it in real points",
      "status_kind": "test"
    },
    {
      "area": "Top priority - Short balls",
      "title": "Move in on every short ball, even when tired",
      "how": "2 x 10 mixed deep/short feeds, approaching every short one, then 10 live points late in the session",
      "cue": "Split, first step forward on short - call \"short\" out loud",
      "target": "7 out of 10 first steps forward in live points",
      "status": "Test it in real points",
      "status_kind": "test"
    },
    {
      "area": "Next priority - High backhands",
      "title": "Take high backhands early instead of backing up",
      "how": "2 x 10 high feeds to your two-handed backhand; count how many you hit without getting jammed",
      "cue": "Short backswing, take it rising",
      "target": "6 out of 10 not jammed",
      "status": "Keep going",
      "status_kind": "keep"
    },
    {
      "area": "Body - Calves",
      "title": "Calf strength in the gym",
      "how": "Calf raises, straight and bent knee, 3 x 12, twice a week",
      "cue": "Slow down, control up",
      "target": "Both gym sessions done, and the calf feels no tighter",
      "status": "Keep going",
      "status_kind": "keep"
    }
  ],
  "cues": [
    "Brush up, body, less pace",
    "Split, first step forward - say \"short!\"",
    "Short backswing, take it rising"
  ],
  "improving": [
    "Second serve: the brushed serve felt better and 14 of 20 landed fairly deep in practice",
    "Short balls: calling \"short\" out loud got you moving in earlier - about 7 of 10 approaches"
  ],
  "watching": [
    "Calling \"short\" out loud may be the trigger for moving in - now we test it in real points",
    "You still back up on short balls once you get tired",
    "High backhands are still rushed and often jam you"
  ],
  "health": "Your left calf got a bit tight at the end of practice. Rate it 0-10 after each session. Tightness is fine to train through carefully; if it turns into pain, rest it and see a qualified professional.",
  "next_steps": [
    "Next session: call \"short\" out loud in 10 live points and count your forward first steps, including the tired ones",
    "Ask Coach Maria what she means by \"go through the ball\" on the approach",
    "Rate your left calf 0-10 after each session"
  ]
};
