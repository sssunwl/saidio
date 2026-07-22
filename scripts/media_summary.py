#!/usr/bin/env python3
"""Create a compact Discord summary for the latest media-generation state."""
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = [("🎵", "data/dashboard.json"), ("🗣️", "data/voiceover.json"), ("🎬", "data/suntravel.json")]
today = os.environ.get("SAIDIO_DATE", date.today().isoformat())
lines = [f"**SAIDIO / 每日媒體製作 · {today}**"]
for icon, name in files:
    payload = json.loads((ROOT / name).read_text())
    brief = next((b for b in reversed(payload.get("briefs", [])) if b.get("date") == today), None)
    items = (brief or {}).get("items", [])
    if name.endswith("dashboard.json") and brief and not items:
        items = [{"generation": {}} for _ in brief.get("prompts", [])]
    generations = [i.get("generation") for i in items if i.get("generation")]
    state = generations[0].get("status", "未執行") if generations else "未執行"
    url = next((g.get("assetUrl") for g in generations if g.get("assetUrl")), None)
    lines.append(f"{icon} **{state}**" + (f" — {url}" if url else ""))
(ROOT / "media-discord-message.txt").write_text("\n".join(lines))
