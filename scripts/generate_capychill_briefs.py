#!/usr/bin/env python3
"""Maintain a rolling seven-day CapyChill album and fixed-scene production queue."""
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/capychill.json"

THEMES = [
    {
        "name": "海邊黃昏・Slow Notes by the Bay",
        "mood": "warm, unhurried, quietly optimistic",
        "palette": "peach sunset, muted ocean blue, warm walnut",
        "weather": "clear golden-hour sky and calm sea",
        "texture": "soft sea breeze and distant water ambience",
    },
    {
        "name": "雨日專注・Rain on the Glass",
        "mood": "sheltered, focused, gently introspective",
        "palette": "deep blue-grey rain, amber desk lamp, dark green plants",
        "weather": "steady rain across the same window",
        "texture": "soft rain on glass and low room tone",
    },
    {
        "name": "清晨第一杯・First Light, First Cup",
        "mood": "fresh, patient, lightly hopeful",
        "palette": "pale cream dawn, sage green, honey wood",
        "weather": "misty early morning over the same bay",
        "texture": "distant gulls used sparingly and a quiet kettle",
    },
    {
        "name": "深夜讀寫・Midnight Pages",
        "mood": "deep focus, calm solitude, never gloomy",
        "palette": "navy night, warm amber pool of light, soft moon silver",
        "weather": "clear moonlit night outside the same window",
        "texture": "subtle night room tone and faint sea wash",
    },
    {
        "name": "週末慢拍・A Very Slow Sunday",
        "mood": "easygoing, cozy, gently playful",
        "palette": "soft terracotta, cream, sun-washed blue",
        "weather": "bright lazy afternoon at the same seaside room",
        "texture": "light breeze, leaves and quiet café-like room tone without voices",
    },
    {
        "name": "陰天留白・Clouds Have Time",
        "mood": "spacious, neutral, restorative",
        "palette": "pearl grey, faded blue, warm natural wood",
        "weather": "slow overcast clouds above the same bay",
        "texture": "soft wind and distant rolling water",
    },
    {
        "name": "月光晚安・Moonlit Capy",
        "mood": "sleepy, safe, tender and low-energy",
        "palette": "indigo, moon cream, very low amber light",
        "weather": "quiet moon and sparse stars over the same sea",
        "texture": "slow waves and extremely soft night ambience",
    },
]

TRACKS = [
    ("Opening the Window", "Rhodes piano and felt piano", "simple four-chord welcome"),
    ("Steam from the Cup", "nylon guitar and soft electric piano", "small descending motif"),
    ("A Page at a Time", "felt piano and muted jazz guitar", "patient call-and-response"),
    ("Plants in the Breeze", "Rhodes, marimba accents and round bass", "light swaying motif"),
    ("Distant Little Boat", "clean guitar harmonics and warm keys", "wide spacious melody"),
    ("Capy Takes a Break", "soft piano, brushed kit and upright-style bass", "relaxed pause-and-answer phrasing"),
    ("Light Across the Desk", "vibraphone, Rhodes and tape-soft drums", "gentle repeating light motif"),
    ("The Town Turns On", "warm synth pad, electric piano and soft bass", "slowly opening harmony"),
    ("Sea After Sunset", "felt piano, distant guitar and minimal percussion", "longer notes with more space"),
    ("See You Tomorrow", "solo felt piano, warm pad and almost no drums", "quiet resolving reprise"),
]

TIME_VARIANTS = [
    ("白天版本", "Veo 3.1 Lite 測試 → Fast 定稿", "soft daylight, slow sea reflections and a light curtain breeze"),
    ("黃昏版本", "Veo 3.1 Lite 測試 → Fast 定稿", "golden light gradually warming, distant town lights beginning to glow"),
    ("夜晚版本", "Veo 3.1 Lite 測試 → Fast 定稿", "moonlit bay, steady desk lamp and subtle distant lights"),
    ("雨天版本", "Veo 3.1 Lite 測試 → Fast 定稿", "rain trails on the window, darker sea and warm sheltered interior"),
]


def music_prompt(theme, index, track):
    title, instruments, motif = track
    bpm = 70 + (index % 4) * 2
    return (
        f'Track {index + 1}/10 — "{title}". Create a 3:00–3:30 instrumental lo-fi track for one '
        f'cohesive 30-minute CapyChill album titled "{theme["name"]}". Mood: {theme["mood"]}. '
        f'{bpm} BPM, 4/4, {instruments}, warm restrained bass and soft brushed or tape-muted drums. '
        f'Composition: {motif}; introduce a small variation after 60 seconds, a calm B section near '
        f'1:30, then return to the main motif. Mix for long listening: no vocals, no spoken words, '
        f'no dramatic drops, no piercing highs, no recognizable melody, no artist imitation. '
        f'Leave gentle headroom and end cleanly with a 4–6 second natural tail. Environmental texture: '
        f'{theme["texture"]}, very low in the mix. This track must feel related to the other nine tracks '
        f'without reusing the same lead melody.'
    )


def image_prompt(theme):
    return (
        "Create a 16:9 hand-painted storybook master frame for CapyChill. Preserve the exact canonical "
        "composition across the entire channel: the same warm-brown capybara sits at the same wooden desk "
        "on the right third, wearing the same cream headphones, facing left toward the same notebook; the "
        "same large window, desk lamp, mug, shelves and plants stay in identical positions. Camera is locked, "
        f"eye-level, 35mm-equivalent wide view. Today’s album mood is {theme['name']}; use {theme['palette']} "
        f"with {theme['weather']}. Calm original illustration, clean natural capybara anatomy. No text, letters, "
        "numbers, logos, watermark, signature, sparkle icon or fake signage. Output one clean reference image, "
        "not a collage. This image will become an image-to-video reference, so keep clear separable layers for "
        "capybara, desk objects, curtain, plants, window, sea, clouds and lights."
    )


def video_prompt(theme, label, motion):
    return (
        f"MODEL PLAN: generate one 8-second draft with Veo 3.1 Lite; use Veo 3.1 Fast only after the draft "
        f"preserves the reference correctly. {label}: Image-to-video from the selected CapyChill canonical "
        f"reference. Lock the camera and preserve every pixel-level layout relationship: same room, same desk, "
        f"same capybara size and position, same objects, no cuts, no zoom, no pan. Motion only: natural slow "
        f"breathing, one soft blink, one tiny ear twitch, minimal pencil-writing motion, subtle mug steam; "
        f"{motion}. Make first and last frame visually compatible for looping. No new objects, no morphing, "
        f"no extra limbs, no moving furniture, no text, no logos, no sound dialogue."
    )


def make_brief(day):
    theme = THEMES[(day - date(2026, 7, 23)).days % len(THEMES)]
    items = [
        {
            "type": "專輯音樂",
            "purpose": "30 分鐘 YouTube Lo-fi 長片",
            "engine": "Gemini 音樂生成",
            "status": "prompt",
            "text": music_prompt(theme, i, track),
        }
        for i, track in enumerate(TRACKS)
    ]
    items.append({
        "type": "專輯概念圖",
        "purpose": "固定場景 reference",
        "engine": "ChatGPT Images",
        "status": "prompt",
        "text": image_prompt(theme),
    })
    items.extend({
        "type": f"影片 Prompt・{label}",
        "purpose": "固定構圖微動畫",
        "engine": engine,
        "status": "prompt",
        "text": video_prompt(theme, label, motion),
    } for label, engine, motion in TIME_VARIANTS)
    return {
        "date": day.isoformat(),
        "stream": "capychill",
        "title": f"CapyChill 每日專輯｜{theme['name']}",
        "focus": "10 首 × 約 3 分鐘＝約 30–35 分鐘",
        "meta": "固定海邊書桌母場景 · 10 音樂＋1 概念圖＋4 影片版本",
        "summary": "每日預設：10 首做約 30–35 分鐘。長度換算：30 分鐘＝8–10 首；45 分鐘＝12–14 首；60 分鐘＝15–18 首。選定概念圖後，只以同一 reference 製作白天、黃昏、夜晚與雨天微動畫。",
        "items": items,
    }


def main():
    payload = json.loads(DATA.read_text())
    start = date.today()
    by_date = {brief["date"]: brief for brief in payload.get("briefs", [])}
    for offset in range(7):
        day = start + timedelta(days=offset)
        by_date[day.isoformat()] = make_brief(day)
    payload["briefs"] = sorted(by_date.values(), key=lambda item: item["date"])
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"CapyChill queue ready: {start} through {start + timedelta(days=6)}")


if __name__ == "__main__":
    main()
