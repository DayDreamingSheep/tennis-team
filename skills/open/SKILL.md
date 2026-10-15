---
name: open
description: Open the Tennis Team app, the page where the player talks or types to their coaching team and sees their plan, calendar, tournaments, and team. Use when the player says "open the app", "open Tennis Team", "voice mode", "I want to talk to my coach", "show me my plan page", or invokes this skill directly.
license: PolyForm-Noncommercial-1.0.0
allowed-tools: Bash(python3:*)
metadata:
  plugin: tennis-team
  role: app launcher
---

# Open the Tennis Team app

The app usually opens by itself when Claude starts in the player's tennis folder. This skill opens it on request.

1. Run, from the current folder:

   ```bash
   python3 "<plugin root>/app/launch.py" --open --dir "<current folder>"
   ```

   The plugin root is two folders up from this SKILL.md. The script starts the local app server if needed and opens the browser. It reuses a server that is already running.
2. Reply in plain words:

   > Your Tennis Team is open in your browser. Tap the green mic and talk, or type to your team.
   > If it didn't open, double-click **Open Tennis Team** in your Tennis folder.

3. If `python3` is missing, say so plainly and suggest installing Python 3 from python.org.

Notes:
- The app only works on this computer, and its link contains a secret token.
- To stop it opening automatically, the player can turn off **Open automatically** in the app's Settings.
