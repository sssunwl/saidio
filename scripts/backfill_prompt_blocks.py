#!/usr/bin/env python3
"""Wrap every archived prompt in the three-part PROMPT / NEGATIVE / RULES package.

The generators bundle new prompts as they are written, but the archive still holds
lines produced before a rule existed. Whoever copies an old line out of the site
should get the same rules as someone copying today's. This script needs no API key,
so it can be re-run locally after any change to prompt_blocks.py.

Prompts the user has already produced media for are left alone: see FROZEN.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompt_blocks import blocks_for, bundle, is_bundled  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# data file -> stream key for blocks_for(). dashboard.json is the original music line.
FILES = {
    "dashboard.json": "music",
    "voiceover.json": "voiceover",
    "suntravel.json": "suntravel",
    "carousel.json": "carousel",
    "capychill.json": "capychill",
    "obcar.json": "obcar",
}

# The ten-track albums for these days are already generated and published; re-issuing
# their music prompts with new rules would only invite a pointless re-render.
FROZEN = {("capychill", "音樂", day) for day in ("2026-07-23", "2026-07-24", "2026-07-25")}


def frozen(stream, item_type, day):
    return any(stream == s and marker in (item_type or "") and day == d for s, marker, d in FROZEN)


def backfill_file(name, stream):
    path = ROOT / "data" / name
    payload = json.loads(path.read_text())
    wrapped = skipped = 0
    for brief in payload.get("briefs", []):
        day = brief.get("date", "")
        for item in brief.get("items", []):
            text = item.get("text")
            if not isinstance(text, str) or is_bundled(text):
                continue
            if frozen(stream, item.get("type"), day):
                skipped += 1
                continue
            pair = blocks_for(stream, item.get("type"))
            if pair is None:
                continue
            item["text"] = bundle(text, *pair)
            wrapped += 1
        # The music line predates items[] and stores bare prompt strings.
        prompts = brief.get("prompts")
        if isinstance(prompts, list):
            pair = blocks_for(stream, "音樂")
            for index, text in enumerate(prompts):
                if not isinstance(text, str) or is_bundled(text):
                    continue
                prompts[index] = bundle(text, *pair)
                wrapped += 1
    if wrapped:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"{name}: wrapped {wrapped}, left frozen {skipped}")
    return wrapped


def main():
    total = sum(backfill_file(name, stream) for name, stream in FILES.items())
    print(f"Backfill done: {total} prompts now carry NEGATIVE + RULES")


if __name__ == "__main__":
    main()
