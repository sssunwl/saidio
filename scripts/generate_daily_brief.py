#!/usr/bin/env python3
"""Generate and archive a daily Saidio music-asset brief with Gemini API."""
import json, os, sys
from datetime import date
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/dashboard.json"
ROTATION = [
    "Japan Field Notes — Daylight", "Japan Field Notes — Winter Night", "Food Close-up / Café",
    "Travel Guide Utility", "Investing Explainer", "AI Character Drama", "Study / Sleep seed pack",
]

def main():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is required")
    payload = json.loads(DATA.read_text())
    today = date.today().isoformat()
    force = os.environ.get("FORCE_REGENERATE") == "1"
    brief = next((item for item in payload["briefs"] if item["date"] == today), None)
    existing_index = next((i for i, item in enumerate(payload["briefs"]) if item["date"] == today), None)
    if brief and not force:
        print("Brief already exists for today; preparing Discord delivery")
    else:
        focus = ROTATION[date.today().toordinal() % len(ROTATION)]
        prompt = f"""You are Saidio's music asset librarian. Create a daily asset brief for {today}.
Focus package: {focus}. Saidio currently validates an investment channel first, while building a
travel Field Notes system and banking assets for AI character drama. Return JSON only with keys:
title, focus, meta, summary, prompts. prompts must be an array of exactly 6 original music prompts.
Each prompt must state duration, BPM, instruments, arrangement, no vocals unless clearly labelled
for AI character drama, no artist references, and a clean ending or loop point. State whether this
is R&D (Gemini) or production (Eleven/Suno) in meta. Do not claim licensing rights."""
        model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        req = Request(url, data=json.dumps({"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseMimeType":"application/json"}}).encode(), headers={"Content-Type":"application/json", "x-goog-api-key": key})
        try:
            response = json.loads(urlopen(req, timeout=90).read())
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:1200]
            (ROOT / "gemini-error.txt").write_text(f"Gemini API request failed ({error.code}): {detail}")
            print(f"Gemini request failed ({error.code}) model={model}: {detail}")
            return
        brief = json.loads(response["candidates"][0]["content"]["parts"][0]["text"])
        if not isinstance(brief.get("prompts"), list) or len(brief["prompts"]) != 6:
            sys.exit("Gemini response did not contain exactly six prompts")
        brief["date"] = today
        if existing_index is None:
            payload["briefs"].append(brief)
        else:
            payload["briefs"][existing_index] = brief
        payload["updatedAt"] = f"{today}T09:00:00+09:00"
        DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    message = "\n".join([
        f"**SAIDIO / {today}**",
        f"**{brief['title']}** — {brief['focus']}",
        brief["summary"],
        "",
        *[f"**{i + 1}.** {item}" for i, item in enumerate(brief["prompts"])],
    ])
    (ROOT / "daily-discord-message.txt").write_text(message)
    print(f"Generated brief for {today}")

if __name__ == "__main__":
    main()
