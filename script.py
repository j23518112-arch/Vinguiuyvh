"""The script is a timeline.

Items:
  ("mark", name)                      a named moment (scene start, a door falls...)
  ("gap", seconds)                    silence
  ("line", id, speaker, text, chunks) who says what; chunks = 2-4 word captions,
                                      the [bracketed] word lights up in the accent colour
"""

# speaker keys (see build_voice.py for the voice settings)
N = "narrator"
W = "ela_whisper"

TIMELINE = [
    ("mark", "s0_cold"),                      # cold open starts
    ("line", "l00", W, "It's on the rope!", ["IT'S ON THE [ROPE!]"]),
    ("gap", 0.35),

    ("mark", "s1_open"),
    ("line", "l01", N, "Most of you said...", ["MOST OF YOU [SAID...]"]),
    ("line", "l02", N, "Jump with her.", ["[JUMP WITH HER.]"]),
    ("gap", 1.0),

    ("mark", "s2_title"),
    ("gap", 1.0),

    ("mark", "s3_scene"),
    ("line", "l03", N, "The boat hits the water.", ["THE BOAT HITS", "[WATER.]"]),
    ("gap", 0.4),

    ("mark", "s4_choice"),
    ("line", "l04", N, "Do you run, or hide?", ["DO YOU [RUN,]", "OR [HIDE?]"]),
    ("gap", 1.0),

    ("mark", "s5_end"),
    ("gap", 2.0),
]

# Sound effects placed at marks: (mark_name, effect_name, offset_seconds)
SFX = [
    ("s2_title", "whoosh", 0.0),
    ("s3_scene", "splash", 0.0),
    ("s5_end",   "impact",  0.0),
]
