---
name: voice
description: Open the Tennis Team Voice Coach - a page in the browser with a big microphone button where the player talks to their tennis team instead of typing. Replies appear on screen and are read aloud. Use when the player says "voice", "voice mode", "open voice coach", "I want to talk", "let me just speak", or invokes this skill directly.
license: MIT
allowed-tools: Bash(python3:*)
metadata:
  plugin: tennis-team
  role: voice interface
---

# Voice Coach

Launch a small local server that serves the voice page and passes each spoken message to the tennis team. The server needs Python 3 (standard library only) and the `claude` command, already signed in.

## Steps

1. **Workspace.** Use the folder containing `TEAM.md`: the current folder or one of its direct subfolders. If there is none, use the current folder; the coach sets the team up from the player's first spoken note.
2. **Start the server in the background.** Use the Bash tool with background mode, so it keeps running after your reply:

   ```bash
   python3 "<this skill's folder>/scripts/voice_server.py" --workspace "<workspace path>"
   ```

   It opens the browser automatically and prints a line starting with `VOICE_COACH_URL`.
3. **Read the URL.** Wait a moment, then read the background output for the `VOICE_COACH_URL` line. If `python3` is missing, say so plainly and suggest installing Python 3 from python.org.
4. **Reply in plain words:**

   > Your Voice Coach is open in your browser. Tap the green button, talk about your practice or match, then tap again when you're done. I'll answer on screen and out loud.
   > If it didn't open, use this link: <URL>
   > Tip: the first time, your browser will ask to use the microphone. Choose **Allow**.

## Notes

- The page only works on this computer (127.0.0.1), and it is protected by a secret link.
- Speech-to-text runs in the browser (Chrome, Edge, or Safari). Some browsers send audio to their own speech service, so mention this if the player asks about privacy.
- Each message runs the tennis team with file tools only (read, write, edit). It cannot run shell commands.
- To stop the Voice Coach, stop the background task, or close this Claude session.
