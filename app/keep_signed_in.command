#!/bin/zsh
# Gives Pocket Tennis Team a long-lived Claude sign-in (about a year), so reports don't stop when the normal login expires.
D="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/tennis-team-tennis-team}"
mkdir -p "$D"
echo "Step 1: a browser window opens. Approve it with your Claude account."
echo "Step 2: Terminal then shows a long token starting with sk-ant-oat. Copy it."
echo
claude setup-token
echo
read -s "T?Step 3: paste that token here, then press Enter: "
echo
if [[ "$T" != sk-ant-* ]]; then echo "That doesn't look like the token. Run this again."; exit 1; fi
printf %s "$T" > "$D/claude.token"; chmod 600 "$D/claude.token"; unset T
echo "Done. Pocket Tennis Team will stay signed in. You can close this window."
