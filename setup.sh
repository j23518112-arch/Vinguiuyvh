#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "== Checking tools =="
for c in node npm python3 ffmpeg; do
  command -v $c >/dev/null || { echo "Missing: $c. Please install it first."; exit 1; }
done
node -v; python3 --version; ffmpeg -version | head -1

echo "== Python packages =="
python3 -m pip install numpy scipy soundfile kokoro-onnx || \
python3 -m pip install --break-system-packages numpy scipy soundfile kokoro-onnx

echo "== Kokoro model files =="
mkdir -p models
BASE="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
[ -f models/kokoro-v1.0.onnx ] || curl -L -o models/kokoro-v1.0.onnx "$BASE/kokoro-v1.0.onnx"
[ -f models/voices-v1.0.bin ]  || curl -L -o models/voices-v1.0.bin  "$BASE/voices-v1.0.bin"

echo "== HyperFrames =="
npx --yes hyperframes --help | head -10 || echo "HyperFrames check failed; see README."

mkdir -p renders assets/audio compositions/frames
echo "Done. Next: edit SERIES.md and scripts/script.py"
