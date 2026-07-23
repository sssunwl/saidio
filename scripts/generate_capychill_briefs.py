#!/usr/bin/env python3
"""Maintain a rolling seven-day CapyChill album and fixed-scene production queue."""
import json
import os
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

VIDEO_COUNT_BY_MINUTES = {30: 6, 45: 8, 60: 10}

MOTION_VARIANTS = [
    ("基準驗收・海面與呼吸", "The capybara stays in the original writing pose without moving the pencil. Only slow breathing and one soft blink. This is the validation clip: prioritize natural ocean motion, stable anatomy and a clean loop."),
    ("安靜寫字", "The writing paw and pencil make one small, anatomically correct writing cycle covering only one short line. The wrist, claws, pencil and notebook remain clearly separated; the body does not shift."),
    ("小幅望海", "The pencil remains resting on the notebook. Only the eyes and head rotate a few degrees toward the ocean, without lifting the neck or torso, then return gently to the exact starting angle."),
    ("杯中蒸氣與窗簾", "The capybara remains almost still with slow breathing. One narrow steam ribbon rises from the mug and dissipates before reaching the character; the curtain edge sways once by only a few centimetres."),
    ("線香與小夥伴", "The capybara remains still. One thin incense smoke trail rises within its own clear air column and never overlaps the character; the sleeping companion takes one slow breath and makes one tiny ear twitch."),
    ("紙頁與海風", "The pencil remains still. Only one notebook page corner lifts slightly and settles once; two nearby plant leaves respond to the same gentle breeze. No full page turn."),
    ("輕觸耳機", "One front paw makes a very small, anatomically correct adjustment to the headphone cup, returns to the notebook, and the character resumes writing."),
    ("小寵物呼吸", "If the reference contains a small sleeping pet, only the pet's slow breathing and one ear twitch move while the capybara continues writing. Do not create a pet if absent."),
    ("線香與靜坐", "If the reference contains incense, one thin smoke trail rises continuously while the capybara sits still and breathes. Do not create incense if absent."),
    ("夜色微光", "The character remains almost still. One soft blink, slow breathing, subtle distant light shimmer and very small plant movement create a calm closing loop."),
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
        "Create one high-resolution 16:9 hand-painted storybook master frame for CapyChill, ideally 3840×2160. "
        "Preserve the exact canonical "
        "composition across the entire channel: the same warm-brown capybara sits at the same wooden desk "
        "with the center of its head at about 64% of the image width, wearing the same cream headphones, facing "
        "left toward the same notebook; the "
        "same large window, desk lamp, mug, shelves and plants stay in identical positions. Camera is locked, "
        f"eye-level, 35mm-equivalent wide view. Today’s album mood is {theme['name']}; use {theme['palette']} "
        f"with {theme['weather']}. Calm original illustration, clean natural capybara anatomy. No text, letters, "
        "numbers, logos, watermark, signature, sparkle icon or fake signage. Output one clean reference image, "
        "not a collage. Design three to five distinct animation opportunities into the still image without clutter: "
        "mug steam, curtain edge, two or three plant leaves, a thin incense stick with a small safe holder, and "
        "one tiny sleeping companion animal in a fixed bed. Each prop must have a clear resting position "
        "and must never compete with the capybara. COMPOSE FOR DUAL FORMAT: the full 16:9 frame must work as a YouTube "
        "video, and a narrow 9:16 portrait crop around the character must also work as a complete Shorts/Reels frame. "
        "The intended portrait crop spans approximately 44% to 76% of the original image width, centred near 60%. "
        "Do not draw crop guides. Inside that corridor, keep the entire head, headphones, writing paw, pencil, notebook, "
        "mug, and a tiny sleeping companion animal curled in a fixed cushion below the desk near the centre. Place the "
        "incense holder in a separate clear area just left of the notebook, with an unobstructed vertical column of air "
        "above it that never crosses the capybara silhouette, headphones, paw, mug or lamp. The portrait "
        "crop must still include a narrow slice of the window and sea, one warm light source and plant leaves, so it "
        "feels like a complete environment rather than a close-up cutout. Do not "
        "place essential storytelling details only at the far left and far right edges. Leave useful breathing room "
        "above the head and below the notebook for vertical-platform UI overlays; do not add text. This image will "
        "become an image-to-video reference, so keep clear "
        "separable layers for capybara, paws, pencil, notebook page, mug steam, incense smoke, pet, curtain, plants, "
        "window, sea, clouds and lights."
    )


def video_prompt(theme, label, motion):
    weather_rule = (
        "Keep all rain moving continuously downward at natural gravity speed; raindrops must never rise, reverse, "
        "freeze, crawl sideways or pulse."
        if "Rain" in theme["name"]
        else "Preserve the clear weather in the reference; do not create rain, snow, storms or new weather effects."
    )
    return (
        f"8-second 16:9 image-to-video from the selected CapyChill master frame. {label}. "
        "STATIC STRUCTURE: locked camera; window frame, desk, shelves, lamp hardware, furniture, headphones and room "
        "geometry do not move. Preserve the character's identity, proportions and silhouette. No cut, zoom, pan or "
        "parallax. MANDATORY BASE ENVIRONMENT MOTION THROUGHOUT THE ENTIRE CLIP: the ocean is visibly alive, not a "
        "still photograph. Several small wave bands travel naturally toward shore; fine ripples change continuously; "
        "the golden reflection on the water shimmers softly in response to those ripples. Motion remains slow, subtle "
        "and physically consistent—never frozen, reversed, pulsing or moving as one flat sheet. Distant clouds drift "
        "less than one percent of the frame width. CHARACTER/PROP ACTION FOR THIS CLIP ONLY: "
        f"{motion} {weather_rule} The mug is still unless this clip explicitly mentions steam. The incense is unlit "
        "and produces no smoke unless this clip explicitly mentions incense. The companion sleeps completely still "
        "unless this clip explicitly mentions it. End close to the opening pose and ocean phase for a gentle loop; "
        "a short crossfade will be added in editing, so do not force an abrupt rewind. No new objects, morphing, extra "
        "limbs, floating pencil, liquid volume change, smoke through objects, moving furniture, sudden light pulse, "
        "text, logo or dialogue. Keep the action and primary moving prop inside the planned 9:16 crop corridor."
    )


def make_brief(day, target_minutes=30):
    theme = THEMES[(day - date(2026, 7, 23)).days % len(THEMES)]
    video_count = VIDEO_COUNT_BY_MINUTES.get(target_minutes, VIDEO_COUNT_BY_MINUTES[30])
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
        "engine": "Veo 3.1 Lite 測試 → Fast 定稿",
        "status": "prompt",
        "text": video_prompt(theme, label, motion),
    } for label, motion in MOTION_VARIANTS[:video_count])
    return {
        "date": day.isoformat(),
        "stream": "capychill",
        "title": f"CapyChill 每日專輯｜{theme['name']}",
        "focus": "10 首 × 約 3 分鐘＝約 30–35 分鐘",
        "meta": f"固定海邊書桌母場景 · 10 音樂＋1 概念圖＋{video_count} 段微動畫",
        "summary": f"本批目標 {target_minutes} 分鐘，安排 {video_count} 段不同微動作。先只生成第 1 條基準驗收片；確認海浪、倒影、角色結構與循環正常後，才生成其餘項目。規則：30 分鐘＝6 段；45 分鐘＝8 段；60 分鐘＝10 段。",
        "items": items,
    }


def main():
    payload = json.loads(DATA.read_text())
    start = date.today()
    target_minutes = int(os.getenv("CAPY_TARGET_MINUTES", "30"))
    if target_minutes not in VIDEO_COUNT_BY_MINUTES:
        raise ValueError("CAPY_TARGET_MINUTES must be 30, 45 or 60")
    by_date = {brief["date"]: brief for brief in payload.get("briefs", [])}
    for offset in range(7):
        day = start + timedelta(days=offset)
        by_date[day.isoformat()] = make_brief(day, target_minutes)
    payload["briefs"] = sorted(by_date.values(), key=lambda item: item["date"])
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"CapyChill {target_minutes}-minute queue ready: {start} through {start + timedelta(days=6)}")


if __name__ == "__main__":
    main()
