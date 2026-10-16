#!/usr/bin/env python3
"""Kokoro text-to-speech worker for the Pocket Tennis Team app.

Runs inside the natural-voice virtualenv (Python 3.10+, kokoro-onnx, misaki, soundfile).
Loads the model once, then reads JSON requests from stdin, one per line:
    {"id": "...", "text": "...", "voice": "af_heart", "speed": 1.0, "out": "/abs/path.wav"}
and writes one JSON reply per line to stdout:
    {"id": "...", "ok": true} or {"id": "...", "ok": false, "error": "..."}
Pronunciation uses misaki (English US/UK, Mandarin), not espeak, which is broken on macOS.
"""

import json
import sys
from pathlib import Path


def main():
    model_dir = Path(sys.argv[1])
    import soundfile as sf
    from kokoro_onnx import Kokoro
    from misaki import en, zh

    kokoro = Kokoro(str(model_dir / "kokoro-v1.0.onnx"), str(model_dir / "voices-v1.0.bin"))
    g2p = {}

    def phonemes(voice, text):
        kind = voice[0]
        if kind not in g2p:
            if kind == "a":
                g2p[kind] = en.G2P(trf=False, british=False, fallback=None)
            elif kind == "b":
                g2p[kind] = en.G2P(trf=False, british=True, fallback=None)
            elif kind == "z":
                g2p[kind] = zh.ZHG2P()
            else:
                raise ValueError(f"voice {voice} is not supported")
        result = g2p[kind](text)
        return result[0] if isinstance(result, tuple) else result

    lang_of = {"a": "en-us", "b": "en-gb", "z": "z"}
    print(json.dumps({"ready": True}), flush=True)
    for line in sys.stdin:
        try:
            req = json.loads(line)
        except ValueError:
            continue
        rid = req.get("id")
        try:
            voice = req.get("voice") or "af_heart"
            text = str(req.get("text") or "").strip()
            if not text:
                raise ValueError("empty text")
            ph = phonemes(voice, text)
            samples, rate = kokoro.create(ph, voice=voice, speed=float(req.get("speed") or 1.0),
                                          lang=lang_of[voice[0]], is_phonemes=True)
            sf.write(req["out"], samples, rate)
            print(json.dumps({"id": rid, "ok": True}), flush=True)
        except Exception as exc:  # report and keep serving
            print(json.dumps({"id": rid, "ok": False, "error": str(exc)[:300]}), flush=True)


if __name__ == "__main__":
    main()
