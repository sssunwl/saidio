#!/usr/bin/env python3
"""Generate a daily Saidio VOICEOVER script brief with Gemini (text only, free tier).

Output: data/voiceover.json (archive) + voiceover-discord-message.txt (Discord body).
Media (the actual TTS audio) is generated manually by the user in AI Studio / ElevenLabs
using the voices locked in VOICES.md, then stored under resource/voiceover/.
"""
import json, os, sys, time
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/voiceover.json"

# theme -> (voice code, voice profile) — mirrors VOICES.md, the source of truth.
ROTATION = [
    ("投資解說", "V-INVEST", "理性沉穩可信的男聲 (calm, rational, trustworthy male narrator)"),
    ("旅遊導覽", "V-TRAVEL-F", "活潑明亮親切的女主持 (bright upbeat friendly female host); 可雙人搭配理性男聲 V-TRAVEL-M 補資訊, 腳本以 [F]/[M] 標記"),
    ("冥想引導", "V-CALM", "溫柔緩慢氣音留白多的女聲 (soft gentle soothing female, slow, breathy); 句短, 句間以 …（停頓）… 標 2-4 秒"),
    ("睡眠故事", "V-SLEEP", "安心溫暖低沉平穩催眠感 (warm reassuring low slow storyteller); 音量不起伏, 結尾漸弱, 供全球通用兒童睡前 channel"),
]


def build_prompt(today, theme, code, profile):
    return f"""You are Saidio's voiceover script writer. Create a daily narration-script brief for {today}.
Theme: {theme}. Target voice: {code} — {profile}.
Return JSON only with keys: title, focus, meta, summary, items.
- title: a short Traditional-Chinese title for the pack, mentioning the theme.
- focus: exactly "{theme}".
- meta: "Gemini R&D · 4 腳本 + 2 音效 · 聲線 {code}".
- summary: one Traditional-Chinese sentence on how to use this pack.
- items: an array of exactly 6 objects, each with keys: type, purpose, engine, voice, status, text.
  * Items 1-4: type="旁白腳本", engine="AI Studio TTS", voice="{code}", status="prompt".
    text = a ready-to-record Traditional-Chinese narration script of 20-45 seconds
    (roughly 60-130 characters), self-contained, matching the {theme} tone. Vary the sub-topic
    across the 4 scripts. For 冥想引導 use short lines with …（停頓）… markers. For 睡眠故事 keep
    it gentle, universal, no scary content, suitable for children. For 旅遊導覽 you may write a
    two-voice script marked [F]/[M].
  * Items 5-6: type="環境音", engine="SFX", voice="", status="prompt".
    text = an English sound-design prompt for an ambience/SFX loop that fits the {theme}
    (state duration ~30-60s, loopable, no music, no copyrighted material).
All items must set purpose="{theme}". No artist or existing-song references, no copyrighted
samples. Do not claim any audio has already been generated."""


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
            (ROOT / "voiceover-error.txt").write_text(f"Gemini API request failed ({error.code}): {detail}")
            print(f"Gemini request failed ({error.code}) model={model}: {detail}")
            return None
        except URLError as error:
            if attempt < 6:
                print(f"Gemini network error {error.reason} (attempt {attempt}/6); retrying")
                time.sleep(min(60, 5 * 2 ** (attempt - 1)))
                continue
            (ROOT / "voiceover-error.txt").write_text(f"Gemini API network error: {error.reason}")
            return None


def main():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is required")
    payload = json.loads(DATA.read_text()) if DATA.exists() else {"stream": "voiceover", "briefs": []}
    today = date.today().isoformat()
    force = os.environ.get("FORCE_REGENERATE") == "1"
    existing_index = next((i for i, item in enumerate(payload["briefs"]) if item["date"] == today), None)
    brief = payload["briefs"][existing_index] if existing_index is not None else None

    if brief is None or force:
        theme, code, profile = ROTATION[date.today().toordinal() % len(ROTATION)]
        model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
        response = call_gemini(build_prompt(today, theme, code, profile), key, model)
        if response is None:
            return
        brief = json.loads(response["candidates"][0]["content"]["parts"][0]["text"])
        if not isinstance(brief.get("items"), list) or len(brief["items"]) != 6:
            sys.exit("Gemini response did not contain exactly six items")
        brief["date"] = today
        brief["stream"] = "voiceover"
        if existing_index is None:
            payload["briefs"].append(brief)
        else:
            payload["briefs"][existing_index] = brief
        payload["stream"] = "voiceover"
        payload["updatedAt"] = f"{today}T09:18:00+09:00"
        DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

    lines = [f"**SAIDIO / 旁白 · {today}**", f"**{brief['title']}** — {brief['focus']}", brief["summary"], ""]
    for i, it in enumerate(brief["items"], 1):
        tag = f"[{it['type']}·{it.get('voice') or it['engine']}]"
        lines.append(f"**{i}.** {tag} {it['text']}")
    (ROOT / "voiceover-discord-message.txt").write_text("\n".join(lines))
    print(f"Generated voiceover brief for {today}")


if __name__ == "__main__":
    main()
