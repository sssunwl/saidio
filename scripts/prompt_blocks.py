#!/usr/bin/env python3
"""Shared PROMPT / NEGATIVE / RULES blocks for every SAIDIO prompt.

Whoever copies a single item out of the site or Discord must get the whole
package in one paste — the prompt itself, what is forbidden, and the production
rules. So the blocks live in the generated text, not in the UI. Add or fix a
rule here and every line picks it up on the next run.
"""

HEAD_PROMPT = "【PROMPT】"
HEAD_NEGATIVE = "【NEGATIVE PROMPT｜禁止項】"
HEAD_RULES = "【RULES｜產出規則】"


def bundle(prompt, negative, rules):
    """Compose one self-contained prompt package."""
    return "\n".join([
        HEAD_PROMPT, prompt.strip(), "",
        HEAD_NEGATIVE, negative.strip(), "",
        HEAD_RULES, rules.strip(),
    ])


def is_bundled(text):
    return isinstance(text, str) and HEAD_PROMPT in text and HEAD_NEGATIVE in text and HEAD_RULES in text


_FIELD_LABELS = {"bpm": "BPM", "id": "", "type": ""}


def flatten_prompt(raw):
    """Gemini answers with a paragraph some days and a structured object on others.

    Everything downstream — the site, Discord, generate_media.py — expects one
    string, so collapse the object form into readable lines and keep the track
    title on the first line where the UI looks for it.
    """
    if isinstance(raw, str):
        return raw
    if not isinstance(raw, dict):
        return str(raw)
    head = str(raw.get("type") or "Music prompt").strip().rstrip(".")
    if raw.get("id"):
        head = f"Track {raw['id']} — {head}"
    lines = [f"{head}."]
    for key, value in raw.items():
        label = _FIELD_LABELS.get(key, key.replace("_", " ").capitalize())
        if not label or value in (None, "", [], {}):
            continue
        text = ", ".join(str(v) for v in value) if isinstance(value, list) else str(value)
        lines.append(f"{label}: {text}")
    return "\n".join(lines)


_NO_VOCALS = "No vocals, lyrics, vocal chops, vocal-like samples or spoken word. "
# The AI character drama package is the one place a vocal take is the point of the asset.
_DRAMA_VOCALS = (
    "No vocals except a character take this prompt explicitly labels as such; no borrowed lyrics, no "
    "vocal chops standing in for a melody. "
)

_MUSIC_NEGATIVE_BODY = (
    "No recognizable, borrowed or "
    "quoted melody; no artist, band, song, franchise or signature-style reference; no copyrighted or "
    "third-party samples; no branded sonic logo. No dramatic drop, EDM build, riser, white-noise sweep, "
    "sidechain pumping or heavy sub-bass below 40 Hz. No piercing highs, harsh transients, clipping or "
    "brickwall limiting. No tempo drift, key change, mid-track silence gap, abrupt cold stop or "
    "fade-out ending."
)

MUSIC_NEGATIVE = _NO_VOCALS + _MUSIC_NEGATIVE_BODY


def music_negative(allow_labelled_vocals=False):
    return (_DRAMA_VOCALS if allow_labelled_vocals else _NO_VOCALS) + _MUSIC_NEGATIVE_BODY

MUSIC_RULES = (
    "1. All harmonic and melodic material must be newly composed and generic enough for a reusable "
    "commercial library.\n"
    "2. Honour the stated duration, BPM, mood and instrument list exactly; do not add instruments "
    "outside that list.\n"
    "3. Leave clean edit points near 0:15, 0:30, 1:00 and 1:30 so the track can be cut down for "
    "shorter edits.\n"
    "4. The middle section must loop seamlessly on itself — same tempo, no unresolved tail — so it can "
    "be extended for long-form video.\n"
    "5. Keep the mid-range centre clear for narration; master around -14 LUFS integrated with at least "
    "1 dB true-peak headroom.\n"
    "6. End with a natural 4–6 second decay tail: not a fade-out, not a hard cut.\n"
    "7. Deliver stereo 48 kHz WAV where the tool allows. Log tool, generation date and licence plan "
    "before the file leaves R&D."
)

CAPY_MUSIC_RULES = MUSIC_RULES + (
    "\n8. This track belongs to one ten-track album: share the palette, room tone and tempo family with "
    "its siblings, but never reuse the same lead melody.\n"
    "9. It will be played under a static long-form video for 30+ minutes — nothing may draw attention "
    "to itself or startle a listener who has stopped watching."
)

IMAGE_NEGATIVE = (
    "No text, letters, numbers, logos, watermark, signature, UI icon, sparkle icon, fake signage or "
    "subtitles. No collage, grid, split panel, multiple views or character sheet. No mitten paws, "
    "fused toes, blob hands, missing or extra digits, extra limbs, human hands, distorted face or "
    "melted anatomy. No photorealism, 3D render, plastic sheen, heavy grain, lens flare, HDR glow, "
    "tilted horizon or dramatic camera angle. No crop guides, safe-area markers, borders or frames. "
    "No additional characters, crowds or brand-name products."
)

IMAGE_RULES = (
    "1. PAW ANATOMY IS MANDATORY: draw both front paws with visibly separated toes and distinct "
    "knuckles, readable at 100% zoom, never rounded mitten shapes or fused blobs. Each paw stays fully "
    "in frame and must not merge into the desk, mug, notebook or its own fur.\n"
    "2. Every part that will move later — paws, fingers, ears, eyelids, head — must be drawn "
    "unoccluded with a clear edge against its background. An image-to-video model refuses to animate "
    "anatomy it cannot read, and a fused paw is the single most common cause of a stiff, dead-looking "
    "clip.\n"
    "3. Keep the channel identity fixed: the same warm-brown capybara, cream headphones, relaxed eyes, "
    "hand-painted storybook rendering, calm eye-level locked camera.\n"
    "4. Keep smoke, steam, rain and every moving element in its own clear air path that never crosses "
    "the character silhouette or another solid object.\n"
    "5. Build the frame in separable layers — character / companion / foreground props / moving "
    "environment / background — because this image becomes an image-to-video reference.\n"
    "6. Output one single clean image at the stated aspect ratio and the highest resolution available."
)

VIDEO_NEGATIVE = (
    "No frozen scene, static rain, stiff or locked paws, held frames, or environment moving as one "
    "flat sheet. No cut, zoom, pan, dolly, parallax, camera shake or aspect change. No morphing, extra "
    "limbs, identity drift, new objects, floating pencil, liquid volume change, smoke passing through "
    "solid objects, moving furniture or shifting room geometry. No added rain, snow, smoke, fire, "
    "wind, sparkle, bloom or sudden light pulse beyond the reference frame. No text, caption, logo, "
    "watermark, dialogue or speed ramp."
)

VIDEO_RULES = (
    "1. The camera is locked; architecture, furniture and solid props hold their exact position and "
    "scale for the whole clip.\n"
    "2. Environmental motion is mandatory and continuous from the first frame to the last — it may "
    "never freeze, reverse, pulse or teleport.\n"
    "3. Paws are never frozen. Even in an otherwise still clip the front paws shift and re-grip very "
    "slightly, with every toe staying separated; do not ask for zero paw movement.\n"
    "4. Only the elements this clip names may move; the companion and all other props stay at rest.\n"
    "5. Preserve the exact weather, time of day and light level of the reference frame.\n"
    "6. Finish close to the opening pose and the same phase of environmental motion. A short crossfade "
    "is added in editing, so do not force an abrupt rewind.\n"
    "7. Keep the character, the primary action and the main moving prop inside the planned 9:16 crop "
    "corridor.\n"
    "8. Generation setting — in Flow use 「帧」/frames mode with the same master frame as both the "
    "first and the last frame: that closes the loop and forces net zoom to zero more reliably than any "
    "wording.\n"
    "9. Post: remove the Veo watermark with delogo=x=1845:y=1024:w=72:h=44, then build the seamless "
    "loop with an xfade of about 1.2 s before looping the clip out to album length."
)
