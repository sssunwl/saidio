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

VOICE_NEGATIVE = (
    "禁止：任何藝人、歌手、頻道、品牌、作品名稱或可辨識的引用句；受版權保護的原文、歌詞、詩句或台詞。"
    "禁止醫療、法律、投資的保證性說法（保證獲利、一定有效、永久根治），禁止恐嚇式開場與急迫話術。"
    "禁止 emoji、Markdown 記號、括號內的舞台指示、英文填充詞、網址與標籤——TTS 會照字唸出來。"
    "禁止繞口的長數字串與生僻專有名詞；禁止簡體字、日文漢字與中國大陸用語。"
    "禁止一句超過 30 字不換氣，禁止全篇同一句型重複。睡眠故事另禁：黑暗、走失、受傷、死亡、追逐等任何驚嚇元素。"
)

VOICE_RULES = (
    "1. 全篇用台灣繁體中文口語，唸得出來才算過關：寫完自己默唸一次，卡住的地方就改短。\n"
    "2. 嚴格照指定秒數與字數；中文朗讀約每秒 3.5 字，超出就刪，不要靠加快語速硬塞。\n"
    "3. 聲線只能用 VOICES.md 裡該角色已鎖定的那一個 voice，不可臨時換人；雙人稿以 [F]／[M] 標示發話者。\n"
    "4. 用標點控制節奏：短句用逗號，換氣用句號，需要停 2–4 秒的地方寫 …（停頓）…，不要用刪節號代替停頓。\n"
    "5. 開頭 5 秒內就要讓聽者知道這段在講什麼，結尾留一句可獨立成立的收束句，不接下集預告。\n"
    "6. 稿子必須自帶上下文，抽出來單獨播也聽得懂，不依賴畫面或前一段。\n"
    "7. 交付 48 kHz 單聲道 mp3／wav，語音目標 -16 LUFS，真峰值留 1 dB 以上餘裕，頭尾各留 0.3 秒靜音。\n"
    "8. 存檔時記錄工具、voice 名稱、生成日期與授權方案，檔名用 YYYYMMDD＋聲線代碼。"
)

SFX_NEGATIVE = (
    "No music, melody, harmony, chord progression, rhythmic groove or musical instrument. No human "
    "voice, whisper, breath, footstep dialogue or crowd chatter with intelligible words. No recognizable "
    "media, franchise, game or film sound design; no copyrighted or third-party samples; no sonic logo. "
    "No sudden transient, door slam, thunder crack, siren, alarm, phone notification or clipping peak. "
    "No fade-in or fade-out, no build, no one-shot event that cannot repeat, no stereo image that "
    "collapses in mono."
)

SFX_RULES = (
    "1. Deliver a steady-state ambience bed that sounds identical at 0:05 and at 0:50 — a listener must "
    "not be able to tell where the loop starts.\n"
    "2. Honour the stated duration; keep the first and last 2 seconds at matched level and spectrum so "
    "the file loops with a short crossfade and no seam.\n"
    "3. Keep the 200 Hz–4 kHz narration band open: this bed always sits under a voiceover.\n"
    "4. Layer at most three separable elements (broad bed / mid detail / occasional far accent) and keep "
    "each in its own frequency range and stereo position.\n"
    "5. Master around -20 LUFS integrated with at least 3 dB true-peak headroom — ambience is a bed, "
    "not a feature.\n"
    "6. High-pass below 30 Hz and keep it mono-compatible; most listeners are on phone speakers.\n"
    "7. Deliver stereo 48 kHz WAV where the tool allows, and log tool, generation date and licence plan "
    "before the file leaves R&D."
)

BROLL_NEGATIVE = (
    "No on-screen text, caption, subtitle, title card, logo, watermark, signature, UI element or "
    "readable signage in any language. No recognizable real brand, storefront name, product label, "
    "vehicle badge, currency or map. No identifiable human face, no crowd close-up, no children as the "
    "subject. No morphing, warping, extra limbs, melting geometry, duplicated horizon, flickering "
    "exposure or shifting colour temperature. No speed ramp, no timelapse whip, no aspect-ratio change, "
    "no letterbox bars, no split screen, no zoom-in-and-out oscillation, no handheld shake, no drone "
    "orbit that reveals a stitched background. No frozen water, static foliage, or environment that "
    "moves as one flat sheet."
)

BROLL_RULES = (
    "1. State shot size, lens feel, camera movement, light direction, time of day and mood explicitly — "
    "an unstated parameter is a parameter the model invents.\n"
    "2. One clip, one continuous camera move at one constant speed. No cut inside the clip.\n"
    "3. Motion must be continuous from the first frame to the last: water, foliage, steam, traffic and "
    "cloth never freeze, reverse or pulse.\n"
    "4. Leave the middle third of the frame visually calm — narration subtitles land there.\n"
    "5. Keep the subject and its action inside the central 9:16 corridor so the same clip can be "
    "reframed for Reels without a re-render.\n"
    "6. The first and last 12 frames must be usable as cut points: no motion blur spike, no subject "
    "entering or leaving frame at the boundary.\n"
    "7. Deliver 1080p or better at 24 or 30 fps, no added grain or LUT — colour grading happens in the "
    "edit, not in the generation.\n"
    "8. Log engine, credit cost, generation date and the focus package in the filename "
    "(YYYYMMDD＋主題＋序號) before the file leaves R&D."
)

CARD_NEGATIVE = (
    "No garbled, invented, mirrored or partially-rendered Chinese glyphs; no lorem ipsum, no placeholder "
    "squiggle standing in for text, no English filler where Traditional Chinese is specified. No "
    "watermark, signature, stock-photo mark, AI-tool badge or imitation of an existing brand, designer "
    "or publication. No nine-cards-on-one-canvas, no phone or device mockup, no drop-shadowed card "
    "floating on a coloured backdrop, no surrounding white canvas, no crop marks or safe-area guides. No "
    "text, logo or key subject inside the outer safe margin or crossing a slice seam. No heavy drop "
    "shadow, bevel, glossy gradient, neon glow, 3D extruded type or 2015-era template look. No more than "
    "two type families or three brand colours. No emoji, no unlicensed icon set, no chart with invented "
    "numbers presented as real data."
)

CARD_RULES = (
    "1. Output ONE standalone card at the stated pixel size, edge to edge, with nothing outside the "
    "artboard.\n"
    "2. Keep an 80 px safe margin on all four sides; the Instagram grid thumbnail crops a 4:5 card on "
    "both sides, so anything load-bearing sits centred and inside that margin.\n"
    "3. The cover must be readable as a 160 px thumbnail: the hook needs one dominant line at 90 px or "
    "larger and a contrast ratio of at least 4.5:1 against whatever is behind it.\n"
    "4. Render only the copy roles this card is assigned. A card that does not need a logo, CTA or "
    "hashtag must not show one.\n"
    "5. Use real, legible Traditional Chinese (Taiwan usage) with punctuation, and keep body text at "
    "36 px or larger — a phone reader is holding this at arm's length.\n"
    "6. Every component must stay visually separable for rebuilding in Canva: text block, photo or "
    "diagram frame, decorative element, page number. Do not print layer-instruction labels on the card.\n"
    "7. Hold the set's brand grammar — palette, type pairing, margin, decorative device — while changing "
    "composition and information density from card to card.\n"
    "8. Body copy must be replaceable: no text baked into a photograph, no headline whose meaning "
    "depends on a decorative shape that cannot be moved."
)

PLATE_NEGATIVE = (
    "NO TEXT OF ANY KIND — no letters, words, numbers, page numbers, headlines, captions, labels, "
    "lorem ipsum, fake glyphs, handwriting or signage in any language. No logo, watermark, signature or "
    "AI-tool badge. No human figure, face, hand, animal or recognizable branded product. No card "
    "borders, frames, crop marks, seam guides, gutters, drop-shadowed panels or anything that reads as "
    "a divided grid of separate cards. No phone mockup, no presentation slide, no surrounding canvas. "
    "NO PHOTOGRAPHY ANYWHERE ON THE PLATE — no photographic landscape, interior, sky, foliage, texture "
    "photo or photo-realistic fill, not even faint, tinted, cropped inside a frame or used as a corner "
    "accent. Photo windows must be left EMPTY: draw the frame outline only and leave the inside as the "
    "plain paper ground. Photographs are placed in Canva afterwards at full resolution, because the "
    "plate is stretched to fit the strip afterwards and any photograph in it smears into pulp. "
    "No high-detail focal subject and no illustrated centrepiece — a plate is a stage, not a picture. "
    "No hard vignette, heavy noise, neon glow or blown-out highlight that would fight typography."
)

PLATE_RULES = (
    "1. This plate is a background only. Text is typeset on top of it later, so more than half of the "
    "surface must stay quiet enough to read 36 px body copy against.\n"
    "2. Compose as one continuous strip. Any structural element — rule, band, path, torn edge, gradient "
    "— must run unbroken from the left edge to the right edge.\n"
    "3. Self-contained motifs must not straddle a cut line. Either repeat them on a rhythm that clears "
    "the cuts, or let the design be genuinely continuous instead.\n"
    "4. Keep contrast low and even along the whole strip: a plate that is dark at one end and pale at "
    "the other produces cards that no longer look like a set.\n"
    "5. Hold one palette and one texture for the entire plate. Colour variation is delivered as a "
    "separate colourway plate, not as drift inside one plate.\n"
    "6. Output the widest aspect ratio the tool offers at the highest available resolution; the strip is "
    "fitted and cut afterwards by scripts/split_carousel.py.\n"
    "7. Detail level matters more than pixel count here: the plate is stretched several times its "
    "generated width, which soft texture survives and fine structure does not.\n"
    "8. PRE-COMPRESS THE GEOMETRY. You can only output about 2.25:1 but the strip is 6.75:1, so "
    "everything you draw is stretched roughly 3× wider afterwards. Draw every arch, frame, circle or "
    "motif THREE TIMES NARROWER than it should finally look — a tall narrow arch here becomes a "
    "correctly-proportioned arch on the card. Horizontal rules and bands are unaffected.\n"
    "9. ONE MOTIF PER CARD, evenly spaced. If the set is N cards, place exactly N repeats across the "
    "strip, each centred in its own 1/N slice, so no card inherits a motif that has drifted off-centre "
    "or been split between two cards.\n"
    "10. No vertical dividing rules between the repeats. A vertical line at a cut turns the swipe into "
    "a row of bordered panels, which is the one thing the plate must never look like."
)

# A 9-card plate is stretched 5.17× horizontally against 1.72× vertically — the mismatch itself
# squashes arches and other round geometry sideways, on top of the blur plain upscaling causes.
# A 3-card segment's target ratio (3:4 × 3 cards wide) lands within a few percent of what most
# image models natively output, so the stretch is close to uniform in both directions: no more
# squash, and only one clean ~1.7× upscale instead of a lopsided 5×. Rule 8 (pre-compress the
# geometry 3× narrower) is gone because there is nothing left to compensate for.
SEGMENT_PLATE_RULES = (
    "1. This plate is a background only. Text is typeset on top of it later, so more than half of the "
    "surface must stay quiet enough to read 36 px body copy against.\n"
    "2. Compose as one continuous strip. Any structural element — rule, band, path, torn edge, gradient "
    "— must run unbroken from the left edge to the right edge of THIS segment.\n"
    "3. Self-contained motifs must not straddle a cut line. Either repeat them on a rhythm that clears "
    "the cuts, or let the design be genuinely continuous instead.\n"
    "4. Keep contrast low and even along the whole segment: one end darker than the other makes "
    "neighbouring segments visibly mismatched when placed side by side.\n"
    "5. Hold one palette and one texture for the entire segment — the same ones used in the other "
    "segments of this set. Do not introduce a gradient, vignette or lighting direction that would make "
    "this segment identifiable as \"the left one\" or \"the right one\": every segment must look like an "
    "interchangeable slice of the same infinite pattern, because segments are generated independently "
    "and never touch pixel-for-pixel at the join.\n"
    "6. Output the widest aspect ratio the tool offers at the highest available resolution.\n"
    "7. ONE MOTIF PER CARD in this segment, evenly spaced, each centred in its own 1/3 slice of this "
    "segment — not drifted off-centre, not split across a cut.\n"
    "8. No vertical dividing rules between the repeats. A vertical line at a cut turns the swipe into "
    "a row of bordered panels, which is the one thing the plate must never look like."
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


# ── OBcar（Okiblues 車隊）────────────────────────────────────
# v2 鐵則第 3 條：禁止詞只寫一次，放 negative 欄。正文只寫「要什麼」——擴散模型
# 讀到 turntable / rotating 會先把那個概念帶進潛空間再嘗試壓抑，念越多次越容易招來它。
# 所以這裡三條 negative 各自只有一行，不再依鏡頭疊加。
OBCAR_STILL_NEGATIVE = (
    "text, signage, japanese characters, licence plate characters, watermark, caption, collage, "
    "multiple views, extra vehicles, people, wheel stop, pole in frame, fisheye, wide-angle stretching, "
    "altered wheels, altered headlights, altered badges, roof rails, wheel-arch cladding, body kit, "
    "lowered stance, car parked across two bays, wrong generation, wrong trim level, "
    "visible driver, visible passenger, clear see-through windscreen exposing empty seats, "
    "lit cabin interior, oversaturated water, uniform plastic-looking foliage, CG render look, "
    "video-game lighting, HDR halo, airless over-clean background"
)

OBCAR_ORBIT_NEGATIVE = (
    "turntable, rotating car, car pivoting, wheels turning, car sliding, car drifting, frozen background, "
    "background without parallax, digital zoom, camera passing through the car, sudden reversal, "
    "morphing bodywork, changing wheels, double exposure, ghosting, transparent overlapping car, "
    "two versions of the car blended together, car flipping to face the opposite direction mid-clip, "
    "front and rear of the car visible at the same time, instant viewpoint jump, viewpoint teleport, "
    "car identity swap, redrawn car body, visible driver, visible passenger, "
    "clear see-through windscreen exposing empty seats, oversaturated water, "
    "uniform plastic-looking foliage, CG render look, HDR halo, text"
)

OBCAR_COAST_NEGATIVE = (
    "car sliding sideways, drifting, changing lanes, sudden acceleration, wobbling horizon, digital zoom, "
    "orbiting a stationary car, turntable, morphing bodywork, changing wheels, changing colour, "
    "right-side traffic, readable road signs, licence plate characters, captions, "
    "drone overtaking the car, camera circling to the opposite end of the car, "
    "rear view turning into a front view, front view turning into a rear view, "
    "car flipping to face the opposite direction mid-clip, instant viewpoint jump, "
    "visible driver, visible passenger, clear see-through windscreen exposing empty seats, "
    "oversaturated water, uniform plastic-looking foliage, CG render look, HDR halo"
)

# 這一線的 RULES 是給操作者看的驗收步驟，不是給模型的指令：每條都停在「這關過了才往下」。
OBCAR_RULES = {
    "anchor169": ("1. 每次都上傳同一組實車照，這是車款唯一真相。\n"
                  "2. 一次只生一張；先批准車款身分與停車幾何再往下。\n"
                  "3. 批准後這張就是本車的場景主定錨，之後每個鏡頭都要附上它。"),
    "anchor916": ("1. 上傳「已批准的 16:9 A01」＋同一組實車照。\n"
                  "2. 原生重生 9:16，不要裁 16:9，也不要外擴。\n"
                  "3. 全車、四輪、陰影、海平線都要落在中央 4:5 內才算過。"),
    "orbit_first": ("1. 首幀＝已批准的 A01；只生 10 秒。\n"
                    "2. 先驗三件事：車沒轉、輪胎沒滑、背景有真實視差。\n"
                    "3. 這段過了才做 P2，不要三段一起生。\n"
                    "4. 工具吐出來的長度要是 10 秒；如果它自己跳到 20 秒以上（代表工具把三段一次做完了），"
                    "整段當失敗丟掉重下，不要剪短將就——一次要求鏡頭轉太大角度，模型最容易用「換一台朝別的方向的車」"
                    "頂替真的繞過去，10 秒內的疊影瞬變通常就是這樣來的。"),
    "orbit_next": ("1. 首幀＝上一段的尾幀（Flow 直接按「延伸」最穩）。\n"
                   "2. 只生 10 秒，方向不可反轉，速度與高度要接得上。\n"
                   "3. P1+P2+P3 直接剪接約 30 秒；要柔一點就加兩個 0.3 秒疊化。\n"
                   "4. 同上：長度必須是 10 秒，跳太長直接重下。逐段生成、逐段驗收，"
                   "是唯一能防住「頭尾疊影瞬變」的做法。"),
    "coast_still": ("1. 上傳同一組實車照；三張定格圖要同一天光、同一段海岸。\n"
                    "2. 一次只生一張，先批准車款與車道方向（左側通行）。\n"
                    "3. 三張都批准後才開始動畫化。"),
    "coast_clip": ("1. 上傳對應的已批准定格圖，只生 10 秒。\n"
                   "2. 車速穩定、不變換車道；靠近或拉遠必須是實體飛行，不是變焦。\n"
                   "3. 成片順序固定：高空接近 → 海側平行 → 低空拉遠。\n"
                   "4. 驗收先看車頭車尾：定格圖是車尾就整段都要是車尾。Flow 很愛自己繞到車頭，"
                   "看到轉向直接重下，不要將就。\n"
                   "5. 玻璃要是反光的，看得進車廂就是失敗——空駕駛座在近景會很怪。"),
}


def obcar_blocks(item_type):
    """OBcar 靠鏡頭代碼決定規則，不靠生成器自己記得傳哪一組。

    代碼寫在 item 的 type 裡（A01／P1–P3／R01a-c／R02a-c），所以 build_obcar_data.py
    與 backfill 查的是同一張表；日後加鏡頭只要在這裡補一行。
    """
    label = item_type or ""
    if "A01" in label:
        return OBCAR_STILL_NEGATIVE, OBCAR_RULES["anchor916" if "9:16" in label else "anchor169"]
    if "P1" in label:
        return OBCAR_ORBIT_NEGATIVE, OBCAR_RULES["orbit_first"]
    if "P2" in label or "P3" in label:
        return OBCAR_ORBIT_NEGATIVE, OBCAR_RULES["orbit_next"]
    if "R01" in label:
        return OBCAR_STILL_NEGATIVE, OBCAR_RULES["coast_still"]
    if "R02" in label:
        return OBCAR_COAST_NEGATIVE, OBCAR_RULES["coast_clip"]
    return None


# One mapping from an item's stream + type to its blocks, so the generators and the
# backfill script can never drift apart on which rules a given prompt gets.
def blocks_for(stream, item_type):
    """Return (negative, rules) for an item, or None when it carries no media prompt."""
    label = item_type or ""
    if stream == "voiceover":
        if "環境音" in label or "音效" in label:
            return SFX_NEGATIVE, SFX_RULES
        return VOICE_NEGATIVE, VOICE_RULES
    if stream == "suntravel":
        return BROLL_NEGATIVE, BROLL_RULES
    if stream == "carousel":
        if "Canva" in label or "分割" in label:
            return None
        if "母圖" in label:
            return PLATE_NEGATIVE, PLATE_RULES
        return CARD_NEGATIVE, CARD_RULES
    if stream == "capychill":
        if "音樂" in label:
            return MUSIC_NEGATIVE, CAPY_MUSIC_RULES
        if "概念圖" in label:
            return IMAGE_NEGATIVE, IMAGE_RULES
        if "影片" in label:
            return VIDEO_NEGATIVE, VIDEO_RULES
        return None
    if stream == "music":
        return MUSIC_NEGATIVE, MUSIC_RULES
    if stream == "obcar":
        return obcar_blocks(label)
    return None
