#!/usr/bin/env python3
"""Generate and archive a daily Saidio music-asset brief with Gemini API."""
import json, os, sys, time
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
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
title, focus, meta, summary, prompts. prompts must be an array of exactly 10 original music prompts
that form one reusable asset package:
- Prompts 1–6: 2:30–3:00 core master tracks with natural edit points near 15, 30, 60, and 90 seconds,
  a loopable middle section, meaningful development instead of simple repetition, and a clean ending.
- Prompts 7–8: 90–120 second alternate arrangements with clean edit points and endings.
- Prompt 9: a dedicated 20–45 second functional cue such as an intro, outro, map transition, bumper,
  or information-card bed, chosen to suit the focus package.
- Prompt 10: a 2:30–3:00 experimental master that still has practical editing points and a clean ending.
Every prompt must explicitly state duration, BPM, mood, instrument constraints, arrangement, edit
points, and whether the middle is loopable. Leave room for narration and location sound where relevant.
No vocals unless clearly labelled for AI character drama, no artist or existing-song references, no
recognizable melodies, and no copyrighted samples. State that all 10 prompts are Gemini R&D in meta;
do not claim licensing rights or imply that generation has already happened."""
        model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        req = Request(url, data=json.dumps({"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseMimeType":"application/json"}}).encode(), headers={"Content-Type":"application/json", "x-goog-api-key": key})
        attempts, response = 6, None
        for attempt in range(1, attempts + 1):
            try:
                response = json.loads(urlopen(req, timeout=90).read())
                break
            except HTTPError as error:
                detail = error.read().decode("utf-8", errors="replace")[:1200]
                transient = error.code in (429, 500, 502, 503, 504)
                if transient and attempt < attempts:
                    wait = min(60, 5 * 2 ** (attempt - 1))
                    print(f"Gemini {error.code} (attempt {attempt}/{attempts}); retrying in {wait}s")
                    time.sleep(wait)
                    continue
                (ROOT / "gemini-error.txt").write_text(f"Gemini API request failed ({error.code}): {detail}")
                print(f"Gemini request failed ({error.code}) model={model}: {detail}")
                return
            except URLError as error:
                if attempt < attempts:
                    print(f"Gemini network error {error.reason} (attempt {attempt}/{attempts}); retrying")
                    time.sleep(min(60, 5 * 2 ** (attempt - 1)))
                    continue
                (ROOT / "gemini-error.txt").write_text(f"Gemini API network error: {error.reason}")
                print(f"Gemini network error model={model}: {error.reason}")
                return
        brief = json.loads(response["candidates"][0]["content"]["parts"][0]["text"])
        if not isinstance(brief.get("prompts"), list) or len(brief["prompts"]) != 10:
            sys.exit("Gemini response did not contain exactly ten prompts")
        brief["date"] = today
        if existing_index is None:
            payload["briefs"].append(brief)
        else:
            payload["briefs"][existing_index] = brief
        payload["updatedAt"] = f"{today}T09:12:00+09:00"
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
