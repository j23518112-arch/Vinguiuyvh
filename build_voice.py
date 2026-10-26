"""Synthesize every line with Kokoro TTS, write narration.wav + timeline.json.

Each caption chunk is voiced alone only to measure its length; the full line's
duration is then split in the same proportions so captions land on the words.
"""
import json, os, subprocess, sys, tempfile
import numpy as np
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(__file__))
from script import TIMELINE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "audio")
os.makedirs(OUT, exist_ok=True)
SR = 24000  # Kokoro native rate

# voice, speed, pitch (semitones), effect key
VOICES = {
    "narrator":    ("am_michael", 0.83, -0.6, None),
    "ela_whisper": ("af_nicole",  0.78, +2.6, "whisper"),
    "ela_mom":     ("af_sarah",   0.80, -0.5, "mom"),
    "radio":       ("am_eric",    0.90, -0.5, "radio"),
    "captain":     ("bm_george",  0.85, -1.5, "memory"),
    "leo":         ("af_sky",     0.92, +3.2, "kid"),
    "fisherman":   ("bm_lewis",   0.86, -2.0, "wind"),
}

FX = {
    "radio": "highpass=f=420,lowpass=f=3200,acompressor=threshold=-22dB:ratio=6:makeup=5",
    "megaphone": "highpass=f=480,lowpass=f=3400,acompressor=threshold=-24dB:ratio=8:makeup=6,aecho=0.8:0.4:220:0.2",
    "whisper": "highpass=f=250,aecho=0.8:0.6:60:0.25",
    "mom": "acompressor=threshold=-20dB:ratio=4:makeup=3,aecho=0.8:0.5:50:0.2",
    "memory": "aecho=0.8:0.7:300|600:0.35|0.2",
    "kid": "highpass=f=200",
    "wind": "acompressor=threshold=-20dB:ratio=4:makeup=3,aecho=0.8:0.6:120:0.25",
}


def pitch_shift(x, semitones):
    """Shift pitch, keep length (rubberband if available, else asetrate+atempo)."""
    if abs(semitones) < 0.01:
        return x
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
        wavfile.write(a, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
        r = 2 ** (semitones / 12)
        af = f"asetrate={int(SR*r)},aresample={SR},atempo={1/r:.5f}"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a, "-af", af, b], check=True)
        sr, y = wavfile.read(b)
        return y.astype(np.float32) / 32767


def apply_fx(x, fx_key):
    if not fx_key:
        return x
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.wav"), os.path.join(d, "b.wav")
        wavfile.write(a, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a, "-af", FX[fx_key], b], check=True)
        sr, y = wavfile.read(b)
        return y.astype(np.float32) / 32767


def main():
    from kokoro_onnx import Kokoro
    kokoro = Kokoro(os.path.join(ROOT, "models", "kokoro-v1.0.onnx"),
                    os.path.join(ROOT, "models", "voices-v1.0.bin"))

    def say(text, speaker):
        voice, speed, st, fx = VOICES[speaker]
        samples, sr = kokoro.create(text, voice=voice, speed=speed, lang="en-us")
        assert sr == SR
        x = pitch_shift(samples.astype(np.float32), st)
        return apply_fx(x, fx)

    t = 0.0
    chunks_audio = []
    tl = {"marks": {}, "lines": []}

    for item in TIMELINE:
        kind = item[0]
        if kind == "mark":
            tl["marks"][item[1]] = round(t, 3)
        elif kind == "gap":
            n = int(item[1] * SR)
            chunks_audio.append(np.zeros(n, dtype=np.float32))
            t += item[1]
        elif kind == "line":
            _, lid, spk, text, chunks = item
            x = say(text, spk)
            dur = len(x) / SR
            # measure each caption chunk alone, then split the line in those proportions
            raw = [c.replace("[", "").replace("]", "") for c in chunks]
            lens = [max(0.05, len(say(c, spk)) / SR) for c in raw]
            total = sum(lens)
            cs, cur = [], t
            for c, l in zip(chunks, lens):
                d = dur * l / total
                cs.append({"text": c, "start": round(cur, 3), "end": round(cur + d, 3)})
                cur += d
            tl["lines"].append({"id": lid, "speaker": spk, "text": text,
                                "start": round(t, 3), "end": round(t + dur, 3), "chunks": cs})
            chunks_audio.append(x)
            t += dur

    audio = np.concatenate(chunks_audio)
    peak = np.max(np.abs(audio)) or 1
    audio = audio / peak * 0.95
    wavfile.write(os.path.join(OUT, "narration.wav"), SR, (audio * 32767).astype(np.int16))
    tl["duration"] = round(t, 3)
    with open(os.path.join(OUT, "timeline.json"), "w") as f:
        json.dump(tl, f, indent=2)
    print(f"narration.wav + timeline.json written. Total length: {t:.1f}s "
          f"(target 70-80s for vote series, 80-90s for story series)")
    if t > 90:
        print("WARNING: too long. Cut a line, don't speed the voice up.")


if __name__ == "__main__":
    main()
