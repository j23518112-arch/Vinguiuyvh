# Stickman Story Kit

Starter project for vertical (1080x1920, 30 fps) narrated stickman story videos,
built from the "How I Make Stickman Story Videos" workflow.

Pipeline: story -> script -> voices -> sound -> look -> scenes -> review -> render -> post

## 1. One-time setup (on your computer)

Requirements: Node.js 20+, Python 3.10+, ffmpeg.

    ./setup.sh

This installs the Python packages (numpy, scipy, kokoro-onnx), downloads the
Kokoro model files into `models/`, and checks that `npx hyperframes` works.

If the Kokoro download URLs change, get `kokoro-v1.0.onnx` and `voices-v1.0.bin`
from the kokoro-onnx GitHub releases page and put them in `models/`.

## 2. Make an episode

1. Edit `SERIES.md` (premise, cast, world rules, palette).
2. Write the story in plain words and approve it BEFORE building anything.
3. Edit `scripts/script.py` (the TIMELINE).
4. `python scripts/build_voice.py`   -> assets/audio/narration.wav + timeline.json
5. `python scripts/build_audio.py`   -> assets/audio/music.wav + sfx.wav (+ voice-clarity check)
6. Build scenes in `compositions/frames/` (copy `_scene_template.html`).
7. `python scripts/build_index.py`   -> index.html (scene slots + audio)
8. `npx hyperframes check`, then snapshot and review the contact sheet.
9. `./scripts/render.sh part-01`     -> renders/part-01_instagram.mp4 + cover.jpg

## 3. Using Claude Code

Open this folder in Claude Code and paste the prompts from `PROMPTS.md`, filling in the [brackets].

## Note

`assets/lf/kit.js` is a starter drawing kit (person, zombie, hand, rain, camera).
Ask Claude Code to extend it (clock, hillView, rooftop, etc.) as your story needs.
HyperFrames' exact composition attributes can change between versions. If `npx hyperframes check`
complains, tell Claude Code to adapt `index.html` and the scene template to the current docs.
