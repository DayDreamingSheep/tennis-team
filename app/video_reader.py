#!/usr/bin/env python3
"""Prototype: read a public YouTube coaching video (or a player's own clip) with Google's Gemini API.

Gemini watches the video itself (picture and sound) through Google's documented YouTube-URL input.
Nothing is downloaded or scraped, and we keep coaching notes, not transcripts.
Key: ~/.tennis-team/gemini.key (or GEMINI_API_KEY). Standard library only.
"""
import argparse
import base64
import json
import mimetypes
import os
import pathlib
import sys
import time
import urllib.request

API = "https://generativelanguage.googleapis.com/v1beta"
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import net  # noqa: E402  (certificate fallback for python.org builds)

NOTES_PROMPT = """You are a careful tennis coaching analyst. Watch this coaching video: listen to the coach AND watch what he demonstrates.
Accuracy rules (most important):
- Every claim must be tagged with its source: "said" (the coach says it; give the timestamp and a short exact quote of at most 12 words) or "seen" (only visible in the demonstration; give the timestamp).
- Do NOT add anything the coach doesn't say or show: no rep counts, sets or durations unless he states them; no mechanisms, reasons or jargon he doesn't use (use his words, not technical labels).
- If unsure what you saw, leave it out.
Return JSON only, with these keys:
- "title", "for_whom" (who this applies to, only if he says), "problem" (the miss as he describes it)
- "model": list of 3-6 {"point", "source": "said"|"seen", "t", "quote"} - his model in plain words
- "chains": list of {"chain": "cause -> effect", "source", "t", "quote"} - only chains he states
- "cues": list of {"cue": his exact words, "meaning", "t"} (max 6)
- "images": list of {"image": his metaphor, "meaning", "t"}
- "learning_order": his progression exactly in his order, as {"step", "what_to_feel", "t", "quote"} - keep separate steps separate; include steps like "miss into the net on purpose first" if he says so
- "mindset_rules": list of {"rule", "t", "quote"} - what he says about fear, misses being OK, what to accept, what to think under pressure
- "warnings": list of {"warning", "t", "quote"} - mistakes, injury cautions, what not to do
- "seen_only": list of {"observation", "t"} - things visible but not said (positions, timing, racket at contact)
- "key_moments": list of {"t", "what"} (max 8)
Write in your own words except quotes. Do not include a transcript."""

CLIP_PROMPT = """You are an expert tennis coach. Watch this short clip of a recreational player and compare it with the coach's model below.
Coach's model and cues:
{model}
Return JSON only: {{"what_i_see": [3-5 specific observations with timestamps], "main_issue": "the one thing that matters most, as body cause and effect",
"matches_model": [what already matches the coach], "the_fix": "one fix in the coach's words and images", "cue": "one 2-4 word cue",
"drill": "a short progression to try next session", "confidence": "high|medium|low and why (camera angle, clip length)"}}"""


def key():
    k = os.environ.get("GEMINI_API_KEY") or ""
    f = pathlib.Path.home() / ".tennis-team" / "gemini.key"
    if not k and f.exists():
        k = f.read_text().strip()
    if not k:
        sys.exit("No Gemini key: save it to ~/.tennis-team/gemini.key")
    return k


def call(method, path, body=None, timeout=600):
    req = urllib.request.Request(f"{API}/{path}", method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"x-goog-api-key": key(), "Content-Type": "application/json"})
    with net.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def pick_model():
    """The newest general Flash model that can generate content."""
    names = [m["name"] for m in call("GET", "models?pageSize=200").get("models", [])
             if "generateContent" in m.get("supportedGenerationMethods", [])]
    flash = [n for n in names if "flash" in n and not any(x in n for x in ("lite", "image", "tts", "live", "audio", "embedding", "exp", "8b", "thinking"))]
    def ver(n):
        import re
        m = re.search(r"(\d+)\.(\d+)", n)
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    flash.sort(key=lambda n: (ver(n), "preview" not in n, "latest" in n))
    return (flash or names)[-1].split("/", 1)[1]


def generate(model, parts, low_res=False):
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json"}}
    if low_res:
        body["generationConfig"]["mediaResolution"] = "MEDIA_RESOLUTION_LOW"
    t0 = time.time()
    for attempt in range(3):                 # the model occasionally returns broken JSON: ask again
        r = call("POST", f"models/{model}:generateContent", body)
        text = "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"])
        usage = r.get("usageMetadata", {})
        try:
            return json.loads(text), usage, round(time.time() - t0, 1)
        except ValueError:
            continue
    raise ValueError("The video reader returned unreadable notes three times.")


def read_youtube(url, model, low_res=False):
    return generate(model, [{"file_data": {"file_uri": url}}, {"text": NOTES_PROMPT}], low_res)


def read_clip(path, model, coach_model):
    data = pathlib.Path(path).read_bytes()
    mime = mimetypes.guess_type(path)[0] or "video/mp4"
    if len(data) > 18_000_000:
        sys.exit("Clip too large for this prototype (keep it under ~18 MB / about 30 seconds).")
    part = {"inline_data": {"mime_type": mime, "data": base64.b64encode(data).decode()}}
    return generate(model, [part, {"text": CLIP_PROMPT.format(model=coach_model)}])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="YouTube URL or a local video file")
    ap.add_argument("--model")
    ap.add_argument("--coach-model", default="", help="for a clip: the coach's model text")
    ap.add_argument("--low", action="store_true", help="low media resolution (cheaper)")
    a = ap.parse_args()
    model = a.model or pick_model()
    if a.target.startswith("http"):
        notes, usage, secs = read_youtube(a.target, model, a.low)
    else:
        notes, usage, secs = read_clip(a.target, model, a.coach_model)
    print(json.dumps({"model": model, "seconds": secs, "usage": usage, "notes": notes}, ensure_ascii=False, indent=1))
