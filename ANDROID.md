# Using the kit from an Android phone

Rendering needs Node, ffmpeg, Python and a headless Chrome. That does not run reliably
inside Termux, so use a cloud dev environment and control it from Chrome on your phone.

## Option A: GitHub Codespaces (recommended)

1. Create a free GitHub account and a new private repository.
2. In Chrome, turn on "Desktop site" (menu > Desktop site) so GitHub's upload page works.
3. Unzip stickman-story-kit.zip on your phone (Files app) and upload the files to the repo
   (Add file > Upload files). Keep the `.devcontainer` folder: it installs everything.
4. Tap Code > Codespaces > Create codespace. The first build takes several minutes.
   It installs ffmpeg, Python packages, the Kokoro model, and Claude Code.
5. In the terminal at the bottom of the editor, run `claude` and sign in. Then paste the
   prompts from PROMPTS.md.
6. When a render finishes, open `renders/` in the file explorer, long-press the
   `*_instagram.mp4`, and choose Download. Then post it from your phone.

Notes:
- Stop the codespace when you are done; free usage is limited per month (check GitHub's
  current free allowance).
- Landscape orientation makes the editor much easier to use on a phone.

## Option B: Claude Code on the web

If your plan includes Claude Code on the web, connect the repo there. The environment must
be able to reach npm, PyPI and GitHub (for the Kokoro model files). If it can't, use Option A.

## Not recommended: Termux

numpy/scipy, onnxruntime (Kokoro) and headless Chrome are hard or impossible to install on
Termux, and rendering 2,300 frames would be very slow on a phone.
