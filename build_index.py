"""Generate index.html (scene slots + 3 audio tracks + captions) from timeline.json.

Scene files in compositions/frames/ named sNN-*.html are mounted in order; each scene
starts at the mark whose name starts with the same sNN prefix (e.g. s03_scene).
Captions are written from the chunk times. Re-run after any script change.
NOTE: HyperFrames attribute names can change between versions; if `npx hyperframes check`
complains, ask Claude Code to adapt this generator to the current docs.
"""
import glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tl = json.load(open(os.path.join(ROOT, "assets", "audio", "timeline.json")))
dur = tl["duration"] + 0.5

# scene start = mark that begins with the same sNN prefix
starts = {}
for name, t in tl["marks"].items():
    m = re.match(r"s(\d+)_", name)
    if m: starts[m.group(1)] = t

scenes = sorted(glob.glob(os.path.join(ROOT, "compositions", "frames", "s[0-9][0-9]-*.html")))
slots = []
keys = sorted(starts, key=lambda k: starts[k])
for f in scenes:
    num = re.match(r"s(\d+)-", os.path.basename(f)).group(1)
    if num not in starts:
        print(f"warning: no mark starting with s{num}_ for {os.path.basename(f)}"); continue
    i = keys.index(num)
    end = starts[keys[i + 1]] if i + 1 < len(keys) else dur
    rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
    slots.append(f'    <div data-composition-src="{rel}" data-start="{starts[num]}" data-duration="{round(end - starts[num], 3)}"></div>')

caps = []
for ln in tl["lines"]:
    for c in ln["chunks"]:
        txt = c["text"].replace('"', "&quot;")
        caps.append(f'    <div class="cap" data-start="{c["start"]}" data-duration="{round(c["end"] - c["start"], 3)}" data-text="{txt}"></div>')

html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Episode</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script src="assets/lf/kit.js"></script>
<script>window.__timeline = {json.dumps(tl)};</script>
<style>html,body{{margin:0;background:#0B1220}}</style>
</head><body>
  <div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-duration="{round(dur, 3)}">
{chr(10).join(slots)}
{chr(10).join(caps)}
    <audio data-start="0" data-duration="{round(dur, 3)}" data-volume="1.0"  src="assets/audio/narration.wav"></audio>
    <audio data-start="0" data-duration="{round(dur, 3)}" data-volume="0.32" src="assets/audio/music.wav"></audio>
    <audio data-start="0" data-duration="{round(dur, 3)}" data-volume="0.75" src="assets/audio/sfx.wav"></audio>
  </div>
</body></html>
"""
open(os.path.join(ROOT, "index.html"), "w").write(html)
print(f"index.html written: {len(slots)} scene(s), {len(caps)} caption chunk(s), {dur:.1f}s")
