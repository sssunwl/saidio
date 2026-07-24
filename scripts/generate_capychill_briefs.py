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
        "texture": "soft sea breeze and distant water ambience",
        "setting": "an open seaside writing alcove with a wide bay window and a warm walnut desk",
        "surface": "warm walnut writing desk",
        "focus_x": 64,
        "crop": "44% to 76%",
        "story": "a quiet sunset journaling session before evening",
        "activity": "writing a short gratitude note in an open cream notebook",
        "props": "a dark ceramic coffee mug, one shell paperweight, a folded postcard and a slim sandalwood incense holder placed away from the character silhouette",
        "companion": "a tiny ginger cat curled in a light oatmeal cushion below the desk",
        "base_motion": "several small ocean wave bands travel toward shore, fine ripples change continuously, and the golden reflection shimmers softly without reversing",
        "primary_motion": "one narrow coffee-steam ribbon rises and dissipates in clear air without crossing the character",
        "secondary_motion": "the curtain edge and two plant leaves sway once in the same gentle sea breeze",
        "gaze_target": "the sunset over the bay",
        "light_motion": "the golden reflection changes softly with the water while the indoor lamp remains steady",
    },
    {
        "name": "雨日專注・Rain on the Glass",
        "mood": "sheltered, focused, gently introspective",
        "palette": "deep blue-grey rain, amber desk lamp, dark green plants",
        "texture": "soft rain on glass and low room tone",
        "setting": "a glass greenhouse study corner surrounded by deep green plants and a rain-darkened garden",
        "surface": "a narrow moss-green iron and wood worktable",
        "focus_x": 42,
        "crop": "24% to 56%",
        "story": "a sheltered deep-focus work session during steady rain",
        "activity": "reviewing two handwritten index cards beside an open notebook, pencil resting safely on the page",
        "props": "a deep green tea mug, a small brass focus timer, two cream index cards and a compact cedar incense holder",
        "companion": "a tiny lop-eared rabbit asleep in a dark moss knitted basket under the table",
        "base_motion": "rain trails move continuously downward on the greenhouse glass, small drops merge naturally, and puddle rings expand once outside; nothing rises or reverses",
        "primary_motion": "tea steam rises in one narrow ribbon while the brass timer remains physically still",
        "secondary_motion": "two wet fern leaves bend slightly under droplets and return slowly",
        "gaze_target": "the rain running down the greenhouse glass",
        "light_motion": "steady amber lamp light reflects faintly in the wet glass without flickering",
    },
    {
        "name": "清晨第一杯・First Light, First Cup",
        "mood": "fresh, patient, lightly hopeful",
        "palette": "pale cream dawn, sage green, honey wood",
        "texture": "distant gulls used sparingly and a quiet kettle",
        "setting": "a small coastal cottage kitchen breakfast nook with an open window and pale dawn light",
        "surface": "a honey-wood breakfast counter",
        "focus_x": 58,
        "crop": "40% to 72%",
        "story": "a fresh morning planning ritual",
        "activity": "writing a simple three-item plan on a clean notebook page",
        "props": "a pale blue mug, a tiny toast plate, a round kettle and a wooden calendar block without readable text",
        "companion": "a tiny cream-coloured hamster dozing in a sage fabric nest on a lower shelf",
        "base_motion": "thin morning mist drifts outside, kettle steam rises steadily, and a small curtain edge moves with fresh air",
        "primary_motion": "the mug gives off one soft steam ribbon while all liquid remains contained and unchanged",
        "secondary_motion": "one herb sprig and the curtain edge sway gently together",
        "gaze_target": "the first pale light outside the kitchen window",
        "light_motion": "dawn light brightens by less than three percent across the full clip without pulsing",
    },
    {
        "name": "深夜讀寫・Midnight Pages",
        "mood": "deep focus, calm solitude, never gloomy",
        "palette": "navy night, warm amber pool of light, soft moon silver",
        "texture": "subtle night room tone and faint sea wash",
        "setting": "a compact midnight library loft with tall bookshelves, a sloped window and an amber reading lamp",
        "surface": "a low dark-oak library table",
        "focus_x": 66,
        "crop": "48% to 80%",
        "story": "a calm midnight reading and annotation session",
        "activity": "reading an open book with one paw resting beside a fountain pen",
        "props": "a navy tea mug, two neatly stacked books, a brass bookmark and a narrow hinoki incense holder in a clear side area",
        "companion": "a tiny dormouse asleep under a small indigo blanket in a shelf nook",
        "base_motion": "moonlit clouds drift extremely slowly beyond the sloped window and a few dust motes cross the lamp beam",
        "primary_motion": "one page corner lifts slightly and settles without turning the page",
        "secondary_motion": "a thin hinoki smoke trail rises within its own clear air column and never overlaps the character",
        "gaze_target": "the moonlit sloped window",
        "light_motion": "the amber reading lamp remains steady while moonlight shifts almost imperceptibly with the clouds",
    },
    {
        "name": "週末慢拍・A Very Slow Sunday",
        "mood": "easygoing, cozy, gently playful",
        "palette": "soft terracotta, cream, sun-washed blue",
        "texture": "light breeze, leaves and quiet café-like room tone without voices",
        "setting": "a sunny rooftop garden studio with planter boxes, open sky and distant low-rise rooftops",
        "surface": "a round weathered picnic table",
        "focus_x": 46,
        "crop": "28% to 60%",
        "story": "an easy Sunday sketching break",
        "activity": "making a tiny plant sketch in the notebook",
        "props": "a cream cocoa mug, one small pastry plate, a blank postcard and three coloured pencils held safely in a cup",
        "companion": "a tiny yellow duckling asleep in a shallow woven basket beside a planter",
        "base_motion": "rooftop grasses and small leaves sway in a light breeze while two distant clouds drift slowly",
        "primary_motion": "a small wind chime makes one gentle swing without colliding or changing shape",
        "secondary_motion": "cocoa steam rises once and a postcard corner lifts a few millimetres before settling",
        "gaze_target": "the open rooftop sky",
        "light_motion": "soft sunlight passes through leaves, creating slow stable shadow movement on the table",
    },
    {
        "name": "陰天留白・Clouds Have Time",
        "mood": "spacious, neutral, restorative",
        "palette": "pearl grey, faded blue, warm natural wood",
        "texture": "soft wind and distant rolling water",
        "setting": "a circular lighthouse reading room with curved windows overlooking an overcast sea",
        "surface": "a built-in pale-wood writing console following the curved wall",
        "focus_x": 62,
        "crop": "44% to 76%",
        "story": "a spacious reset with no pressure to finish",
        "activity": "leaving a mostly blank notebook open while holding the pencil still",
        "props": "a grey-blue herbal tea mug, one smooth stone, a folded linen cloth and a small brass compass",
        "companion": "a tiny white ferret curled in a pearl-grey cushion below the console",
        "base_motion": "broad overcast clouds move slowly, distant water rolls in low bands, and the lighthouse beam crosses the far wall only once at constant speed",
        "primary_motion": "herbal tea steam rises gently without crossing the character or window",
        "secondary_motion": "the folded linen edge and one hanging cord move slightly in the same draft",
        "gaze_target": "the broad grey horizon beyond the curved window",
        "light_motion": "the distant lighthouse beam creates one slow controlled pass; no flashes or pulses",
    },
    {
        "name": "月光晚安・Moonlit Capy",
        "mood": "sleepy, safe, tender and low-energy",
        "palette": "indigo, moon cream, very low amber light",
        "texture": "slow waves and extremely soft night ambience",
        "setting": "a cosy open-front canvas tent beside a moonlit lake, with pine silhouettes and a low lantern",
        "surface": "a low folding camp table",
        "focus_x": 55,
        "crop": "37% to 69%",
        "story": "a gentle final note before sleep",
        "activity": "writing one last short line before closing the notebook",
        "props": "a moon-cream warm milk mug, a closed storybook, a soft cloth bookmark and a safe covered lantern",
        "companion": "a tiny brown hedgehog asleep under a moon-cream miniature blanket in a padded basket",
        "base_motion": "small lake ripples move outward naturally, pine tips sway slightly, and three distant fireflies drift independently without blinking in sync",
        "primary_motion": "warm milk steam rises in one faint ribbon and dissipates before reaching the character",
        "secondary_motion": "the tent flap moves once and the hedgehog blanket rises subtly with one slow breath",
        "gaze_target": "the moonlit lake outside the tent",
        "light_motion": "the covered lantern glows steadily while moonlight shimmers softly on the lake",
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


def motion_variants(theme):
    return [
        ("基準驗收・場景動態", "The capybara holds the original pose. Only slow breathing and one soft blink. Prioritize the scene's mandatory environmental motion, stable anatomy and a clean loop."),
        ("主角活動", f"The capybara performs one very small cycle of today's activity: {theme['activity']}. Paws and objects remain anatomically separated; the torso does not shift."),
        ("短暫觀察", f"Only the eyes and head rotate a few degrees toward {theme['gaze_target']}, without lifting the neck or torso, then return gently to the starting angle."),
        ("主要小物", f"The capybara remains nearly still. {theme['primary_motion']}"),
        ("小夥伴", f"The capybara remains still. {theme['companion']} shows one slow breath and one tiny species-appropriate movement, then returns to rest."),
        ("次要環境", f"The capybara and companion remain still. {theme['secondary_motion']}"),
        ("輕觸耳機", "One front paw makes a very small anatomically correct adjustment to the headphone cup, returns to its resting position, and stops."),
        ("閉眼休息", "The capybara closes its eyes peacefully for one second, takes one visible slow breath, then returns to the exact starting expression."),
        ("光影版本", f"The character remains almost still. {theme['light_motion']}"),
        ("安靜收尾", "The character stays calm with one soft blink and slow breathing; all scene motion continues at the same physical speed for a gentle closing loop."),
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
        "Preserve only the channel identity: the same warm-brown capybara design, cream headphones, relaxed eyes, "
        "natural anatomy and hand-painted storybook rendering. Do not reuse another day's room, furniture layout or "
        f"character position. TODAY'S ORIGINAL SETTING: {theme['setting']}. Place the capybara at {theme['surface']} "
        f"with the centre of its head near {theme['focus_x']}% of image width. Camera is locked, eye-level and calm, "
        f"using a 35mm-equivalent wide view appropriate to this setting. Today’s album is {theme['name']}; use "
        f"{theme['palette']}. TODAY'S STORY: {theme['story']}. The capybara is {theme['activity']}. Include these "
        f"scene-specific props: {theme['props']}. Include {theme['companion']}. Make the following physical motion "
        f"opportunities clearly visible and spatially separated: {theme['base_motion']}; {theme['primary_motion']}; "
        f"{theme['secondary_motion']}. Calm original illustration, clean natural capybara anatomy. No text, letters, "
        "numbers, logos, watermark, signature, sparkle icon or fake signage. Output one clean reference image, "
        "not a collage. Each prop must have a clear resting position "
        "and must never compete with the capybara. COMPOSE FOR DUAL FORMAT: the full 16:9 frame must work as a YouTube "
        "video, and a narrow 9:16 portrait crop around the character must also work as a complete Shorts/Reels frame. "
        f"The intended portrait crop spans approximately {theme['crop']} of the original width, centred near "
        f"{theme['focus_x']}%. Do not draw crop guides. Inside that corridor keep the entire head, headphones, primary "
        "paw action, main working surface, companion, one key prop and enough of today's environment to tell where the "
        "scene takes place. Keep smoke, steam and moving objects in independent clear air paths that never cross the "
        "character silhouette or other solid objects. Leave breathing room above the head and below the main action "
        "for vertical-platform UI overlays. This image will become an image-to-video reference, so use clean separable "
        "visual layers for the character, companion, foreground props, moving environmental elements and background."
    )


def video_prompt(theme, label, motion):
    return (
        f"8-second 16:9 image-to-video from the selected CapyChill master frame. {label}. "
        "STATIC STRUCTURE: locked camera; architecture, furniture, solid props and room geometry do not move. Preserve "
        "the character's identity, proportions and silhouette. No cut, zoom, pan or artificial parallax. MANDATORY "
        f"BASE ENVIRONMENT MOTION THROUGHOUT THE ENTIRE CLIP: {theme['base_motion']}. Motion remains slow, subtle and "
        "physically consistent—never frozen, reversed, pulsing, teleporting or moving as one flat sheet. "
        f"CHARACTER/PROP ACTION FOR THIS CLIP ONLY: {motion} All other optional props and the companion stay still "
        "unless this clip explicitly names them. Preserve the exact weather shown in the reference; do not invent "
        "additional rain, snow, smoke, fire, wind or lighting effects. End close to the opening pose and environmental "
        "motion phase for a gentle loop; "
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
    variants = motion_variants(theme)
    items.extend({
        "type": f"影片 Prompt・{label}",
        "purpose": "固定構圖微動畫",
        "engine": "Veo 3.1 Lite 測試 → Fast 定稿",
        "status": "prompt",
        "text": video_prompt(theme, label, motion),
    } for label, motion in variants[:video_count])
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
    # Refresh yesterday as well so prompt-rule fixes reach the most recent completed album.
    for offset in range(-1, 7):
        day = start + timedelta(days=offset)
        by_date[day.isoformat()] = make_brief(day, target_minutes)
    payload["briefs"] = sorted(by_date.values(), key=lambda item: item["date"])
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"CapyChill {target_minutes}-minute queue ready: {start - timedelta(days=1)} through {start + timedelta(days=6)}")


if __name__ == "__main__":
    main()
