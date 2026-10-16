"""Voice engines for the Pocket Tennis Team app (contract §11). Standard library only.

- natural: Kokoro on-device. A one-time install into <plugin data>/voice/ (venv + model files),
  then a long-lived tts_worker.py process.
- cloud: OpenAI gpt-4o-mini-tts or ElevenLabs, with the player's own API key.
- browser: handled entirely by the page.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.request

import net
import uuid
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
WORKER = APP_DIR / "tts_worker.py"
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
MODEL_FILES = [("kokoro-v1.0.onnx", 325_532_387), ("voices-v1.0.bin", 28_214_398)]
PACKAGES = ["kokoro-onnx==0.6.1", "soundfile", "misaki[en,zh]"]
DEFAULTS = {"en": "af_heart", "zh": "zf_xiaoxiao"}

NAMES = {
    "af_heart": "Heart", "af_alloy": "Alloy", "af_aoede": "Aoede", "af_bella": "Bella", "af_jessica": "Jessica",
    "af_kore": "Kore", "af_nicole": "Nicole", "af_nova": "Nova", "af_river": "River", "af_sarah": "Sarah", "af_sky": "Sky",
    "am_adam": "Adam", "am_echo": "Echo", "am_eric": "Eric", "am_fenrir": "Fenrir", "am_liam": "Liam", "am_michael": "Michael",
    "am_onyx": "Onyx", "am_puck": "Puck", "am_santa": "Santa",
    "bf_alice": "Alice", "bf_emma": "Emma", "bf_isabella": "Isabella", "bf_lily": "Lily",
    "bm_daniel": "Daniel", "bm_fable": "Fable", "bm_george": "George", "bm_lewis": "Lewis",
    "zf_xiaobei": "曉貝 Xiaobei", "zf_xiaoni": "曉妮 Xiaoni", "zf_xiaoxiao": "曉曉 Xiaoxiao", "zf_xiaoyi": "曉伊 Xiaoyi",
    "zm_yunjian": "雲健 Yunjian", "zm_yunxi": "雲希 Yunxi", "zm_yunxia": "雲夏 Yunxia", "zm_yunyang": "雲揚 Yunyang",
}
LANG = {"a": "en-US", "b": "en-GB", "z": "zh"}
CLOUD_VOICES = {
    "openai": ["coral", "nova", "sage", "shimmer", "alloy", "ash", "ballad", "echo", "fable", "onyx", "verse"],
    "elevenlabs": [{"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel"}, {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah"},
                   {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam"}, {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh"}],
}
COACH_STYLE = ("Speak like a warm, encouraging tennis coach talking to one player after practice: natural, relaxed, "
               "upbeat, never robotic.")


def voices():
    out = []
    for vid, name in NAMES.items():
        out.append({"id": vid, "name": name, "lang": LANG[vid[0]], "gender": "female" if vid[1] == "f" else "male",
                    "engine": "natural", "default": vid in DEFAULTS.values()})
    return out


def py_version(exe):
    try:
        out = subprocess.run([exe, "-c", "import sys;print(sys.version_info[0]*100+sys.version_info[1])"],
                             capture_output=True, text=True, timeout=10)
        return int(out.stdout.strip())
    except Exception:
        return 0


def find_python():
    """A Python 3.10–3.13 to build the voice environment with."""
    cands = [sys.executable]
    for n in ("python3.12", "python3.11", "python3.13", "python3.10", "python3"):
        p = shutil.which(n)
        if p:
            cands.append(p)
    cands += ["/opt/homebrew/bin/python3", "/usr/local/bin/python3",
              "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"]
    seen = set()
    for c in cands:
        if c and c not in seen and Path(c).exists():
            seen.add(c)
            v = py_version(c)
            if 310 <= v <= 313:
                return c
    return None


class VoiceManager:
    def __init__(self, data_dir):
        self.dir = Path(data_dir) / "voice"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.cache = self.dir / "cache"
        self.cache.mkdir(exist_ok=True)
        self.status = {"state": "none", "progress": 0, "message": ""}
        if self._installed():
            self.status = {"state": "ready", "progress": 100, "message": ""}
        self._lock = threading.Lock()
        self._proc = None

    # ---------- settings
    def settings(self):
        s = self._read("settings.json", {})
        s.setdefault("engine", "natural" if self.status["state"] == "ready" else "browser")
        s.setdefault("voice", DEFAULTS["en"])
        s.setdefault("speed", 1.0)
        s.setdefault("cloud", {"provider": "openai", "voice": "coral"})
        return s

    def save(self, body):
        s = self.settings()
        for k in ("engine", "voice", "speed"):
            if k in body:
                s[k] = body[k]
        cloud = body.get("cloud")
        if isinstance(cloud, dict):
            c = s.get("cloud", {})
            for k in ("provider", "voice"):
                if cloud.get(k):
                    c[k] = cloud[k]
            s["cloud"] = c
            if cloud.get("key"):
                keys = self._read("cloud.json", {})
                keys[c.get("provider", "openai")] = str(cloud["key"]).strip()
                f = self.dir / "cloud.json"
                f.write_text(json.dumps(keys), encoding="utf-8")
                os.chmod(f, 0o600)
        (self.dir / "settings.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
        return self.public()

    def public(self):
        s = self.settings()
        keys = self._read("cloud.json", {})
        prov = s["cloud"].get("provider", "openai")
        return {"engine": s["engine"], "voice": s["voice"], "speed": s["speed"], "natural": dict(self.status),
                "cloud": {"provider": prov, "voice": s["cloud"].get("voice"), "configured": bool(keys.get(prov))},
                "voices": voices(), "cloudVoices": CLOUD_VOICES, "defaults": DEFAULTS}

    def _read(self, name, default):
        try:
            return json.loads((self.dir / name).read_text(encoding="utf-8"))
        except Exception:
            return default

    # ---------- install
    def _venv_py(self):
        return self.dir / "venv" / "bin" / "python"

    def _installed(self):
        return (self._venv_py().exists() and (self.dir / ".installed").exists()
                and all((self.dir / n).exists() for n, _ in MODEL_FILES))

    def start_setup(self):
        if self.status["state"] in ("installing", "ready"):
            return self.public()
        self.status = {"state": "installing", "progress": 1, "message": "Getting ready…"}
        threading.Thread(target=self._setup, daemon=True).start()
        return self.public()

    def _setup(self):
        try:
            py = find_python()
            if not py:
                raise RuntimeError("The natural voice needs Python 3.10 or newer. Install Python from python.org, "
                                   "then try again.")
            if not self._venv_py().exists():
                self._msg(3, "Preparing the voice engine…")
                subprocess.run([py, "-m", "venv", str(self.dir / "venv")], check=True, capture_output=True, timeout=300)
            self._msg(8, "Installing the voice engine…")
            r = subprocess.run([str(self._venv_py()), "-m", "pip", "install", "-q", "--disable-pip-version-check"] + PACKAGES,
                               capture_output=True, text=True, timeout=1800)
            if r.returncode != 0:
                raise RuntimeError("Couldn't install the voice engine. Check your internet connection and try again.")
            total = sum(sz for _, sz in MODEL_FILES)
            done = 0
            for name, size in MODEL_FILES:
                target = self.dir / name
                if target.exists() and target.stat().st_size == size:
                    done += size
                    continue
                tmp = target.with_suffix(target.suffix + ".part")
                with net.urlopen(MODEL_URL + name, timeout=60) as resp, open(tmp, "wb") as fh:
                    while True:
                        chunk = resp.read(1 << 20)
                        if not chunk:
                            break
                        fh.write(chunk)
                        done += len(chunk)
                        self._msg(25 + int(65 * done / total), f"Downloading the voice ({done // 1_000_000} of {total // 1_000_000} MB)…")
                os.replace(tmp, target)
            self._msg(92, "Warming up the voice…")
            (self.dir / ".installed").write_text("1", encoding="utf-8")
            self._ensure_worker()
            self._synth("Hi, I'm your coach.", DEFAULTS["en"], 1.0, self.cache / "warmup.wav")
            self.status = {"state": "ready", "progress": 100, "message": "Natural voice is ready."}
            s = self._read("settings.json", {})
            s["engine"] = "natural"
            (self.dir / "settings.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
        except Exception as exc:
            (self.dir / ".installed").unlink(missing_ok=True)
            self.status = {"state": "error", "progress": 0, "message": str(exc)[:300]}

    def _msg(self, p, m):
        self.status = {"state": "installing", "progress": p, "message": m}

    # ---------- natural synthesis
    def _ensure_worker(self):
        if self._proc and self._proc.poll() is None:
            return
        self._proc = subprocess.Popen([str(self._venv_py()), str(WORKER), str(self.dir)], stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
        while True:                       # wait for {"ready": true}; skip any library chatter
            line = self._proc.stdout.readline()
            if not line:
                raise RuntimeError("The voice engine stopped while starting.")
            try:
                if json.loads(line).get("ready"):
                    return
            except ValueError:
                continue

    def _synth(self, text, voice, speed, out):
        with self._lock:
            self._ensure_worker()
            rid = uuid.uuid4().hex[:8]
            self._proc.stdin.write(json.dumps({"id": rid, "text": text, "voice": voice, "speed": speed, "out": str(out)}) + "\n")
            self._proc.stdin.flush()
            while True:
                line = self._proc.stdout.readline()
                if not line:
                    self._proc = None
                    raise RuntimeError("The voice engine stopped.")
                try:
                    msg = json.loads(line)
                except ValueError:
                    continue
                if msg.get("id") == rid:
                    if not msg.get("ok"):
                        raise RuntimeError(msg.get("error") or "Couldn't make that sound.")
                    return out

    # ---------- public TTS
    def tts(self, text, voice=None, speed=None):
        """Returns (bytes, content_type). Raises LookupError when the chosen engine isn't ready."""
        s = self.settings()
        engine = s["engine"]
        speed = float(speed or s.get("speed") or 1.0)
        text = " ".join(str(text or "").split())[:1200]
        if not text:
            raise ValueError("empty text")
        if engine == "natural":
            if self.status["state"] != "ready":
                raise LookupError("Natural voice isn't installed yet.")
            voice = voice if voice in NAMES else s.get("voice") if s.get("voice") in NAMES else DEFAULTS["en"]
            key = hashlib.sha1(f"natural|{voice}|{speed}|{text}".encode()).hexdigest()
            out = self.cache / f"{key}.wav"
            if not out.exists():
                self._synth(text, voice, speed, out)
            return out.read_bytes(), "audio/wav"
        if engine == "cloud":
            prov = s["cloud"].get("provider", "openai")
            key = self._read("cloud.json", {}).get(prov)
            if not key:
                raise LookupError("Add your premium voice key in Settings.")
            v = voice or s["cloud"].get("voice") or ("coral" if prov == "openai" else CLOUD_VOICES["elevenlabs"][0]["id"])
            ck = hashlib.sha1(f"cloud|{prov}|{v}|{speed}|{text}".encode()).hexdigest()
            out = self.cache / f"{ck}.mp3"
            if not out.exists():
                out.write_bytes(self._cloud(prov, key, v, speed, text))
            return out.read_bytes(), "audio/mpeg"
        raise LookupError("The browser voice is selected.")

    def _cloud(self, prov, key, voice, speed, text):
        if prov == "elevenlabs":
            req = urllib.request.Request(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
                data=json.dumps({"text": text, "model_id": "eleven_flash_v2_5",
                                 "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "speed": speed}}).encode(),
                headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
        else:
            req = urllib.request.Request(
                "https://api.openai.com/v1/audio/speech",
                data=json.dumps({"model": "gpt-4o-mini-tts", "voice": voice, "input": text, "instructions": COACH_STYLE,
                                 "response_format": "mp3", "speed": speed}).encode(),
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with net.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            raise RuntimeError("The premium voice service said no (check your key and credit)." if e.code in (401, 402, 403)
                               else f"The premium voice service failed ({e.code}).")
