#!/usr/bin/env python3
"""Generate a daily Suntravel visual-asset brief with Gemini (text only, free tier).

Output: data/suntravel.json (archive) + suntravel-discord-message.txt (Discord body).
The media (B-roll clips, Flow film, cards) is generated manually by the user in
Veo / Google Flow / Imagen from these prompts, then stored under resource/suntravel/.
"""
import json, os, sys, time
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/suntravel.json"

ROTATION = [
    "沖繩海島", "城市街景", "美食特寫", "交通移動", "飯店房景", "日出日落", "雨天室內",
]


def build_prompt(today, focus):
    return f"""You are Suntravel's B-roll and content brief writer. Create a daily visual-asset brief for {today}.
Focus package: {focus}. Return JSON only with keys: title, focus, meta, summary, items.
- title: a short Traditional-Chinese title mentioning the focus.
- focus: exactly "{focus}".
- meta: "Flow 每日選片 · 6 Lite + 2 Fast".
- summary: one Traditional-Chinese sentence on how to use this package.
- items: an array of exactly 8 objects, each with keys: type, purpose, engine, status, text.
  All items set purpose="{focus}" and status="prompt".
  * Items 1-6: type="Flow Lite", engine="Veo 3.1 Lite · 10點". text = an English text-to-video prompt for a
    5-8 second cinematic B-roll clip fitting {focus}. Each must state shot type, camera movement,
    lighting/mood, time of day, and "no on-screen text, no logos, leave room for narration".
  * Items 7-8: type="Flow Fast", engine="Veo 3.1 Fast · 20點". text = a stronger 8-second cinematic
    candidate with purposeful subject motion, camera movement, lighting, mood and pacing. These are
    the two premium candidates; make them clearly different from the Lite exploration prompts.
No artist/brand references, no copyrighted material, no recognizable real logos."""


def call_gemini(prompt, key, model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    req = Request(url, data=json.dumps({"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
    for attempt in range(1, 7):
        try:
            return json.loads(urlopen(req, timeout=90).read())
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:1200]
            if error.code in (429, 500, 502, 503, 504) and attempt < 6:
                wait = min(60, 5 * 2 ** (attempt - 1))
                print(f"Gemini {error.code} (attempt {attempt}/6); retrying in {wait}s")
                time.sleep(wait)
                continue
            (ROOT / "suntravel-error.txt").write_text(f"Gemini API request failed ({error.code}): {detail}")
            print(f"Gemini request failed ({error.code}) model={model}: {detail}")
            return None
        except URLError as error:
            if attempt < 6:
                print(f"Gemini network error {error.reason} (attempt {attempt}/6); retrying")
                time.sleep(min(60, 5 * 2 ** (attempt - 1)))
                continue
            (ROOT / "suntravel-error.txt").write_text(f"Gemini API network error: {error.reason}")
            return None


def main():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is required")
    payload = json.loads(DATA.read_text()) if DATA.exists() else {"stream": "suntravel", "briefs": []}
    today = date.today().isoformat()
    force = os.environ.get("FORCE_REGENERATE") == "1"
    existing_index = next((i for i, item in enumerate(payload["briefs"]) if item["date"] == today), None)
    brief = payload["briefs"][existing_index] if existing_index is not None else None

    current_types = [item.get("type") for item in (brief or {}).get("items", [])]
    stale_format = current_types != (["Flow Lite"] * 6 + ["Flow Fast"] * 2)
    if brief is None or force or stale_format:
        focus = ROTATION[date.today().toordinal() % len(ROTATION)]
        model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
        response = call_gemini(build_prompt(today, focus), key, model)
        if response is None:
            return
        brief = json.loads(response["candidates"][0]["content"]["parts"][0]["text"])
        if not isinstance(brief.get("items"), list) or len(brief["items"]) != 8:
            sys.exit("Gemini response did not contain exactly eight items")
        brief["date"] = today
        brief["stream"] = "suntravel"
        if existing_index is None:
            payload["briefs"].append(brief)
        else:
            payload["briefs"][existing_index] = brief
        payload["stream"] = "suntravel"
        payload["updatedAt"] = f"{today}T09:24:00+09:00"
        DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    lines = [f"**SUNTRAVEL / Flow 每日選片 · {today}**", f"**{brief['title']}** — {brief['focus']}", "每天提供 6 支 Lite＋2 支 Fast 提示詞；建議實際生成 5 Lite＋1 Fast（共 70 點）。", brief["summary"], ""]
    for i, it in enumerate(brief["items"], 1):
        lines.append(f"**{i}.** [{it['type']}·{it['engine']}] {it['text']}")
    (ROOT / "suntravel-discord-message.txt").write_text("\n".join(lines))
    print(f"Generated suntravel brief for {today}")


if __name__ == "__main__":
    main()
