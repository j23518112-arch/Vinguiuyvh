#!/usr/bin/env bash
# usage: ./scripts/render.sh part-01
set -e
cd "$(dirname "$0")/.."
NAME="${1:-episode}"
mkdir -p renders

echo "== 1. render master =="
npx hyperframes render -o "renders/${NAME}_master.mp4" .

echo "== 2. measure loudness =="
M=$(ffmpeg -hide_banner -i "renders/${NAME}_master.mp4" -af "loudnorm=I=-14:TP=-2:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
I=$(echo "$M"  | grep '"input_i"'      | sed 's/[^-0-9.]//g')
TP=$(echo "$M" | grep '"input_tp"'     | sed 's/[^-0-9.]//g')
LRA=$(echo "$M"| grep '"input_lra"'    | sed 's/[^-0-9.]//g')
TH=$(echo "$M" | grep '"input_thresh"' | sed 's/[^-0-9.]//g')
OFF=$(echo "$M"| grep '"target_offset"'| sed 's/[^-0-9.]//g')

echo "== 3. normalize to -14 LUFS / -2 dBTP =="
ffmpeg -y -hide_banner -loglevel error -i "renders/${NAME}_master.mp4" -c:v copy \
  -af "loudnorm=I=-14:TP=-2:LRA=11:measured_I=${I}:measured_TP=${TP}:measured_LRA=${LRA}:measured_thresh=${TH}:offset=${OFF}:linear=true" \
  -ar 48000 -c:a aac -b:a 192k -movflags +faststart "renders/${NAME}_instagram.mp4"

echo "== 4. cover from title card (edit -ss to match your title card time) =="
ffmpeg -y -hide_banner -loglevel error -ss "${COVER_AT:-6.39}" -i "renders/${NAME}_instagram.mp4" -frames:v 1 -q:v 2 "renders/${NAME}_cover.jpg"

echo "== 5. last-look contact strip (~25 frames) =="
ffmpeg -y -hide_banner -loglevel error -i "renders/${NAME}_instagram.mp4" -vf "fps=1/3,scale=216:-1,tile=13x2" -frames:v 1 "renders/${NAME}_contact.jpg"

echo "Done: renders/${NAME}_instagram.mp4, ${NAME}_cover.jpg, ${NAME}_contact.jpg"
