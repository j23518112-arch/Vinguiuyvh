"""Generate music.wav and sfx.wav from timeline.json, then run the voice-clarity check.

Rules: no sound libraries; every sound is shaped noise + sine waves.
Music ~0.32 (ducked under speech), effects ~0.75 (ducked harder under whispers).
Voice must be >= 10 dB louder than music + effects in the 300-4000 Hz band.
"""
import json, os, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.dirname(__file__))
from script import SFX

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets", "audio")
SR = 24000
rng = np.random.default_rng(7)  # fixed seed: same sounds every run


def noise(sec): return rng.standard_normal(int(sec * SR)).astype(np.float32)
def lp(x, f): return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
def hp(x, f): return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)
def decay(x, rate): return x * np.exp(-np.arange(len(x)) / SR * rate)
def sine(f, sec): return np.sin(2 * np.pi * f * np.arange(int(sec * SR)) / SR).astype(np.float32)
def norm(x, peak=1.0): return x / (np.max(np.abs(x)) + 1e-9) * peak


def reverb(x, amt=0.5):
    out = np.concatenate([x, np.zeros(int(0.6 * SR), dtype=np.float32)])
    for d, g in [(0.029, 0.5), (0.047, 0.4), (0.071, 0.3), (0.113, 0.2)]:
        k = int(d * SR)
        out[k:k + len(x)] += x * g * amt
    return out


# ---------- effects ----------
def soft_rain(n):
    """Band-limited wash + muffled drops. No high hiss: people heard it as crackle."""
    wash = lp(bp(noise(n), 250, 2200), 1600) * 0.5
    clicks = np.zeros(int(n * SR), dtype=np.float32)
    idx = (np.abs(np.sin(np.arange(int(n * SR // 400)) * 12.9898) * 43758.5453) % 1)  # hash, no randomness
    clicks[(idx * (len(clicks) - 1)).astype(int)] = 1.0
    drops = lp(bp(clicks, 500, 2500), 1800) * 1.2
    return wash + drops


def whoosh():
    n = noise(0.7)
    env = np.sin(np.linspace(0, np.pi, len(n))) ** 2
    return bp(n, 300, 3000) * env * 0.8


def splash():
    n = noise(1.0)
    return lp(bp(n, 200, 2500), 2000) * decay(np.ones_like(n), 5) * 1.0


def impact():
    s = sine(48, 1.2) * decay(np.ones(int(1.2 * SR), dtype=np.float32), 3.5)
    return norm(s + lp(noise(1.2), 300) * decay(np.ones(int(1.2 * SR), dtype=np.float32), 8) * 0.5, 0.9)


def ratchet_click():
    x = bp(noise(0.35), 900, 4500) * decay(np.ones(int(0.35 * SR), dtype=np.float32), 110)
    x = x + (sine(780, 0.35) + sine(1650, 0.35)) * decay(np.ones(int(0.35 * SR), dtype=np.float32), 60) * 0.2
    return reverb(x, 0.9)


EFFECTS = {"whoosh": whoosh, "splash": splash, "impact": impact, "ratchet_click": ratchet_click}


def drone(sec):
    t = np.arange(int(sec * SR)) / SR
    d = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(55, 0.5), (82.5, 0.25), (110.5, 0.12)])
    pad = lp(noise(sec), 400) * 0.3 * (0.6 + 0.4 * np.sin(2 * np.pi * t / 9))
    return (d + pad).astype(np.float32)


def duck_curve(total, tl, depth_speech=0.35, depth_whisper=0.2):
    g = np.ones(int(total * SR), dtype=np.float32)
    for ln in tl["lines"]:
        a, b = int((ln["start"] - 0.05) * SR), int((ln["end"] + 0.15) * SR)
        depth = depth_whisper if "whisper" in ln["speaker"] else depth_speech
        g[max(0, a):b] = np.minimum(g[max(0, a):b], depth)
    k = int(0.06 * SR)  # smooth
    return np.convolve(g, np.ones(k) / k, mode="same")


def place(buf, x, at):
    s = int(at * SR)
    e = min(len(buf), s + len(x))
    buf[s:e] += x[: e - s]


def band_db(x, lo=300, hi=4000):
    y = bp(x, lo, hi)
    return 20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-9)


def main():
    tl = json.load(open(os.path.join(A, "timeline.json")))
    total = tl["duration"] + 0.5
    n = int(total * SR)

    music = drone(total) * 0.32 + soft_rain(total)[:n] * 0.15
    music *= duck_curve(total, tl, 0.55, 0.4)

    sfx = np.zeros(n, dtype=np.float32)
    for mark, name, off in SFX:
        if mark not in tl["marks"]:
            print(f"skip {name}: mark {mark} not found"); continue
        t0 = tl["marks"][mark] + off
        place(sfx, norm(EFFECTS[name](), 0.75), t0)
        tl.setdefault("sfx", {})[f"{mark}:{name}"] = round(t0, 3)
    sfx *= duck_curve(total, tl, 0.3, 0.15)

    wavfile.write(os.path.join(A, "music.wav"), SR, (norm(music, 0.8) * 32767).astype(np.int16))
    wavfile.write(os.path.join(A, "sfx.wav"), SR, (np.clip(sfx, -1, 1) * 32767).astype(np.int16))
    json.dump(tl, open(os.path.join(A, "timeline.json"), "w"), indent=2)

    # ---- voice-clarity check ----
    sr, voice = wavfile.read(os.path.join(A, "narration.wav"))
    voice = voice.astype(np.float32) / 32767
    bed = music[:n] + sfx[:n]
    bad = 0
    for ln in tl["lines"]:
        a, b = int(ln["start"] * SR), int(ln["end"] * SR)
        if b - a < SR * 0.1: continue
        diff = band_db(voice[a:b]) - band_db(bed[a:b])
        status = "ok " if diff >= 10 else "FAIL"
        if diff < 10: bad += 1
        print(f"{status} {ln['id']:>5}  voice is {diff:5.1f} dB over music+fx")
    print("All lines clear." if not bad else
          f"{bad} line(s) under 10 dB: move the effect into the pause before the line, or turn it down.")


if __name__ == "__main__":
    main()
