# Copy-paste prompts (paste into Claude Code in this folder, adjust the [brackets])

## 1. Set up the series
Set up a HyperFrames project for a vertical story video: 1080x1920, 30 fps, 70-80 seconds. Flat 2D look, thick dark outlines, round-headed stickman characters, black silhouette monsters with glowing eyes. Make a reusable drawing kit in assets/lf/kit.js with functions for a character, a monster, a hand, rain and a camera helper. Write a series bible in SERIES.md from this premise: [premise].

## 2. Story -> script
Here's the story for Part [N]: [beats]. Turn it into scripts/script.py as a timeline of marks, gaps and lines. Split each line into 2-4 word caption chunks with the key word in [brackets]. Open with a 2-second cold open from the scariest moment, then "Most of you said... [winner]". End with this choice: [question] - [option A] / [option B].

## 3. Voices
Synthesize every line with Kokoro TTS. Narrator: am_michael, speed 0.83. [Character]: [voice], [speed], pitch [+/-st], with [effect]. Write narration.wav and timeline.json with the start and end of every line, chunk and mark.

## 4. Sound
Generate music.wav and sfx.wav in Python from timeline.json: a low dark drone, soft rain with no high hiss, and these effects at these marks: [list]. Duck effects under every line. Then check that each line is at least 10 dB above music + effects in the 300-4000 Hz band and fix any that aren't.

## 5. Scenes
Build scene [id] from these beats: [beats]. Read every time from the timeline, keep each frame a pure function of time, keep faces between y 330 and 1140, captions at 1140-1360, nothing important in the bottom 20%.

## 6. Review -> render
Run the check, then snapshot every 2 seconds and show me the contact sheet. Fix anything hard to read at phone size. Then render, normalize to -14 LUFS with -2 dB true peak, and save a cover from the title card.

## Review checklist
- Arm crossing a face -> point it outward or draw the near arm under the head
- Character hidden by a prop -> re-aim camera or move the prop
- Empty sky/floor -> tighter camera or add a far town/crowd
- Something visible too early -> set it off-screen at time 0
- HUD text overflow -> shorter label, wider panel
- Accent colour on a busy background -> brighter accent, heavier caption outline
- Too many people in a shot -> cut to 3-4
- Rule of thumb: every beat should read in under a second with the sound off
