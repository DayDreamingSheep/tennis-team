# Roadmap

Last updated 2026-10-15. Status: v0.2 is built and tested end to end with the real AI. Nothing is published yet.

## Where we are

**Built and tested in v0.2:**
- **App:** opens on its own (with an off switch) for a Head Coach interview with a live plan board. Then a team huddle, then a plan review where every item has a Why.
- **Home and tabs:** a conversation-first Home with Plan, Calendar, Tournaments, Team, and Health & Load for parents.
- **Team:** seven members, each a skill: Head Coach, Team Manager, Journal Keeper, Coach Analyst, Progress Coordinator, Planner (formerly Strategy Coach) and Tournament Coach.
- **Replies:** a fast reply in about 20 s; the journal, plan and calendar update in the background.
- **Voice:**
  - natural on-device voice (36 voices; defaults Heart and 曉曉 Xiaoxiao)
  - spoken-style replies and instant acknowledgements
  - hands-free talk mode
  - an editable transcript with clean-up of misheard tennis words
- **Families:** parent-operated junior mode with load and growth guardrails.
- **Training material:** a YouTube channel, YouTube video or web link added from any team member's "Teach them" box (Head Coach included). Public title and channel only; the coach asks for your takeaway.
- **HTTPS fix:** web requests work on Mac Pythons that ship without trusted certificates. This affected link lookup, the voice download and the cloud voice.

**Known gaps:**
- **Not tested on real devices:**
  - the microphone in talk mode
  - the auto-open hook inside a real Claude session
  - the premium cloud voice (needs a key)
  - a fresh Mac
- **Still slow:**
  - the first setup takes about 3½ minutes, behind the huddle
  - background bookkeeping takes about 2½ minutes per message
- **Missing:**
  - the page understands text with keyword rules only
  - there's no phone access
  - there's no sync between two devices

## Timeline at a glance

| Date | Milestone |
|---|---|
| Mon, Oct 26, 2026 | **v0.2.0 Preview** on GitHub, with live demo (gate G1) |
| Sun, Nov 1, 2026 | Case study live; project on resume |
| Sun, Nov 22, 2026 | Friends beta review (gate G2); weekly patches v0.2.1–0.2.4 before it |
| Mon, Jan 18, 2027 | **v0.3.0**: feels like a real team (gate G3) |
| Mon, Jan 25, 2027 | Submit to Anthropic's plugin directory |
| Mon, Mar 1, 2027 | **Go / no-go** on a paid product (gate G4) |
| Mon, Mar 29, 2027 | **v0.4.0**: family and on the go |
| Mon, Jun 21, 2027 | v1.0 hosted beta, only if go |

The full chart, the next 4 weeks, the decision gates and the risks are in [`design/timeline.html`](design/timeline.html). The plan assumes about 10 h a week; dates are targets.

---

## Phase 1: Launch-ready (next 2–3 weeks)

**Goal:** a stranger can install the plugin from GitHub and have a smooth first week, with no help from us.

| # | Enhancement | Why | Done when |
|---|---|---|---|
| 1.1 | **Real-device test pass:** talk mode on a real mic, the hook in the CLI, the Desktop Code tab and Cowork, a fresh Mac (Python and Apple's command line tools popup), Chrome / Safari / Edge | Every test so far ran in simulation or a scratch setup | A checklist passes on 2 Macs. Each issue is fixed or written down |
| 1.2 | **Faster onboarding:** the plan review shows the board's plan instantly as a draft while setup finishes, then updates it in place | 3½ min is too long, even with the huddle | Plan review within 10 s of the last answer |
| 1.3 | **Lighter bookkeeping:** skip the files a message doesn't touch, and batch reads | 60 tool steps per message costs time and money | Under 60 s and about 30% of today's cost per message |
| 1.4 | **Cost guard:** a daily message cap and a "your team is resting" message; show usage in Settings | Each message is two AI runs | No surprise bills; the cap can be adjusted |
| 1.5 | **Error recovery:** retry, an offline banner, an inbox replay after a failed job, server crash recovery | Low-tech users quit at the first error | No raw error text anywhere |
| 1.6 | **Publish v0.2:** commit, a GitHub repo with a marketplace entry, an install guide with screenshots, a privacy note | It isn't installable by anyone else yet | `/plugin install` works from GitHub |
| 1.7 | **Demo video and screenshots** for the README | People need to see it before installing | A 60-second walkthrough |

## Phase 2: Feels like a real team (v0.3, about 6 weeks)

**Goal:** daily use is effortless, and the team feels smart rather than scripted.

| # | Enhancement | Notes |
|---|---|---|
| 2.1 | **Understanding by AI instead of keyword rules:** a small fast pass understands free text, so routing, the board cards and parsing come from the model | Fixes the remaining "said X, app understood Y" issues |
| 2.2 | **Streaming replies:** speak and show the first sentence while the rest is still being written | Cuts the wait from about 20 s to about 5 s until the coach starts talking |
| 2.3 | **On-device Whisper speech recognition** (already decided): primed with tennis words and the player's and coaches' names | Accents and mixed Chinese/English; private |
| 2.4 | **More voice languages:** fix the espeak issue on macOS for Spanish, French, Japanese and Portuguese voices. Add a kids' voice preset | Kokoro already ships these voices |
| 2.5 | **Player Scout:** pick a pro you admire; the team breaks down their style and what you can borrow for your body and level, as part of your roadmap | From your original idea; labelled as interpretation |
| 2.6 | **Fitness Coach:** one weekly block that serves the current tennis priority; injury- and growth-aware | Uses the load data we already keep |
| 2.7 | **Knowledge library, part 2:** public Google Docs with Keep in sync, PDF and photo upload, Loom. **Part 1 shipped in v0.2:** YouTube channel, YouTube video and web links saved with public metadata only (official oEmbed); the player's own takeaway becomes the evidence | No video downloading or transcript scraping (YouTube Terms of Service); only summaries and short quotes, kept private |
| 2.8 | **Weekly check-in as a moment:** a Sunday summary card plus a short voice recap, with a scheduled run if the platform allows | Builds the weekly habit |
| 2.9 | **Better match tools:** score-by-score debrief chips, opponent notes that carry across matches, and a printable match card | For tournament players |

## Phase 3: Family and on the go (v0.4, about 8 weeks)

**Goal:** parents and players can use it courtside and from two devices.

| # | Enhancement | Notes |
|---|---|---|
| 3.1 | **Phone capture first:** voice memos land in an iCloud or Drive `inbox/` and are processed automatically | Works today in principle; needs a guided setup |
| 3.2 | **Phone app access:** a local HTTPS link with QR pairing, or a small hosted relay | Browsers only allow the microphone over HTTPS |
| 3.3 | **Two-device family sync:** one writer per file, conflict-safe | Parent device plus junior device |
| 3.4 | **Teen role:** a junior's own login view and private notes, **after a policy review** on minors and Claude accounts | Deferred on purpose in v0.2 |
| 3.5 | **Nutrition Coach:** match-day fueling and hydration; adults first, juniors general fueling only | Never weight goals for minors |
| 3.6 | **Google Calendar sync:** sessions, lessons, tournaments and entry deadlines | Prototyped button |

## Phase 4: Connected team (2027)

| # | Enhancement | Notes |
|---|---|---|
| 4.1 | **Real-coach view:** a read-only weekly brief the player can share with their human coach, who can add notes | Brings the real coach into the loop |
| 4.2 | **Stats Analyst:** SwingVision and UTR imports turned into patterns and charts | Data-backed progress |
| 4.3 | **Multi-player:** siblings, or a coach with several students | One folder per player |
| 4.4 | **Opt-in hosted sync** with encryption, deletion and consent flows | Only if users ask; local stays the default |
| 4.5 | **Monthly report** as a shareable page | Progress you can show a coach or parent |

---

## How we'll measure progress

- **Activation:** 80% of installs reach a plan review in 5 minutes or less.
- **Habit:** 60% log a second note within 7 days; 40% are still active at week 8.
- **Speed:** the coach starts speaking within 5 s (Phase 2), and the full reply is under 20 s.
- **Effort:** 70% or more of notes come from voice or chips, not typing.
- **Trust:**
  - every plan item has a Why
  - pain is always answered first
  - no raw errors are ever shown

## Guiding rules (unchanged)

- Small load: at most 3 tennis focuses plus 1 fitness block a week.
- Evidence before change: one session is "something we're watching", not proof.
- Health first: "not medical advice" on every health reply; pain pauses the related work.
- Local and private by default. The player owns the files.
