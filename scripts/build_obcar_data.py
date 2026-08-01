#!/usr/bin/env python3
"""Build the public OBcar production line data deterministically."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IDENTITY = """Use all uploaded real vehicle photographs as strict immutable references. They are the single source of truth. For this demo, the subject is the exact standard-body third-generation Honda Freed shown in those photographs. Preserve its actual model year, trim, paint colour, body proportions, grille and front panel, headlights and DRLs, bumpers, factory wheels and tyres, ride height, mirrors, windows and pillars, door count and sliding-door seams, handles, fuel door, rear hatch, vertical taillights and factory badge placement exactly as photographed. Never infer a different trim from general model knowledge. Do not convert it into Freed Crosstar or add roof rails, wheel-arch cladding, aero parts, body kits, spoilers, oversized wheels, lowered suspension or accessories absent from the references."""

REFERENCE_ROLE = """REFERENCE ROLE SEPARATION: the uploaded vehicle photographs define only the vehicle identity. Any uploaded scenery photographs define only the environment, geography, road layout, coastline, architecture, weather and atmosphere. Do not copy vehicles that appear in scenery photographs and do not replace the reference Honda Freed with a background vehicle. If scenery photographs are supplied, infer one coherent three-dimensional version of that same location rather than pasting them as flat backdrops. If no scenery photograph is supplied, use the default northern Okinawa environment described below."""

DUAL_RATIO_STILL = """Create a 16:9 landscape master at the highest native resolution available. Compose it for a later 9:16 centre crop: the central 31.6 percent of the 16:9 width is the protected vertical corridor. Keep the complete vehicle, all four tyres, the attached ground shadow and essential road context inside that corridor with internal breathing room. Use physical camera distance, not wide-angle distortion, to make the vehicle fit. Keep decorative landscape outside the corridor. If a useful 16:9 composition and a complete vertical crop cannot both be achieved without making the car too small, prioritize the strong 16:9 master and flag this shot for the native 9:16 reframe prompt; never distort the car."""

DUAL_RATIO_VIDEO = """This is a 16:9 landscape master planned for a later 9:16 centre crop. Throughout the entire clip, keep the complete vehicle, all four tyres and the attached shadow inside the central 31.6 percent protected corridor with breathing room. Do not let camera motion push the vehicle outside that corridor. If the crop-safe composition makes the vehicle unacceptably small or weak, prioritize the strong 16:9 motion and flag the clip for a native 9:16 remake; never warp, squeeze or unnaturally steer the car to satisfy the crop."""

PARKING_WORLD = """DEFAULT WHEN NO SCENERY PHOTO IS PROVIDED: one fixed, spatially coherent seaside public parking area in northern Okinawa, Japan, with clean asphalt, fixed white parking lines, a low concrete seawall, calm blue-green sea, curved coastline, subtropical green hills, a few simple dark lamp posts and bright natural afternoon light. No readable signs, crowds, resort styling or vehicle on sand. The car remains locked to the same world coordinates and compass heading across the whole series. Its four tyre contact points and shadow remain attached to the exact same ground locations. Buildings, road edges, parking lines, seawall, lamp posts, hills, coastline and horizon remain fixed in world space. Reconstruct the same environment from each camera position with correct occlusion, perspective and parallax; never paste one flat background behind a rotated car."""

TEXT_RULE = """No readable Japanese or English text, place name, shop name, road-sign wording, licence plate characters, caption or watermark. Any unavoidable sign must be blank, turned away, hidden, distant or naturally out of focus. Use a plain blank white promotional licence plate. Authentic factory badges may remain only when accurately supported by the uploaded photographs."""

IMAGE_NEGATIVE = """STRICTLY FORBIDDEN: rotating the vehicle, turntable photography, changing the car's compass direction, moving tyre positions relative to parking lines, static pasted background, mirroring, impossible coastline movement, inconsistent road layout or sun direction, rotating shadow, fisheye, extreme wide-angle stretching, fake text, licence mutation, vehicle morphing, or changing body length, height, doors, headlights, taillights, trim or wheels. Output one image only; no collage or contact sheet."""

CAMERAS = [
    ("01", "前左定錨圖", "Front-left three-quarter view. Camera azimuth about 35 degrees left of the vehicle's forward direction, radius about 7.5 metres, height 1.1 metres, 55mm full-frame equivalent. This is the master scene anchor."),
    ("02", "正左側", "Perfect left-side profile. Camera perpendicular to the left side, radius about 8 metres, height 1.2 metres, 60mm full-frame equivalent. Wheels align naturally in perspective."),
    ("03", "後左45°", "Rear-left three-quarter view. Camera azimuth about 145 degrees from the vehicle's forward direction, radius about 7.5 metres, height 1.1 metres, 55mm full-frame equivalent."),
    ("04", "正後", "Perfect centred rear view. Camera aligned with the longitudinal centre line, radius about 8 metres, height 1.15 metres, 60mm full-frame equivalent. Rear design is symmetrical."),
    ("05", "後右45°", "Rear-right three-quarter view. Camera azimuth about 215 degrees from the vehicle's forward direction, radius about 7.5 metres, height 1.1 metres, 55mm full-frame equivalent."),
    ("06", "正右側", "Perfect right-side profile. Camera perpendicular to the right side, radius about 8 metres, height 1.2 metres, 60mm full-frame equivalent. Preserve all visible door seams and handles."),
    ("07", "前右45°", "Front-right three-quarter view. Camera azimuth about 325 degrees from the vehicle's forward direction, radius about 7.5 metres, height 1.1 metres, 55mm full-frame equivalent."),
]

COAST_CLIPS = [
    ("09", "10", "高空接近", "High wide aerial establishing view, about 45 metres above and 35 metres behind the car, camera diagonally toward the ocean side, 35mm equivalent. The vehicle is clearly identifiable but the sweeping Okinawa coastline initially dominates.", "Begin wide and high. The drone descends and flies gently closer while tracking the car, ending in a medium-high rear three-quarter view. The apparent size change comes only from physical approach, never digital zoom."),
    ("11", "12", "海側平行跟拍", "Elevated ocean-side tracking view, about 8 metres above and 14 metres from the car, 50mm equivalent. Show a complete side profile with a slight front three-quarter angle; the car is the main subject and the sea remains visible behind it.", "Fly parallel to the vehicle on the ocean side at a stable safe distance. Move slightly forward during the final third, ending with a gentle elevated front three-quarter view. Do not orbit or cross the driving lane."),
    ("13", "14", "低空後方拉遠", "Low rear three-quarter tracking view, about 2.2 metres above and 9 metres behind the car, 65mm equivalent. Emphasize the rear design, taillights and wheels while retaining visible coastline and road ahead.", "Begin in a low rear three-quarter tracking view. During the second half, climb gently and fly backward to reveal more road, sea and green hills. The car continues at constant speed and becomes smaller only through physical camera travel."),
]


def image_prompt(camera):
    return f"""【PROMPT】
{IDENTITY}

{REFERENCE_ROLE}

{PARKING_WORLD}

CAMERA POSITION:
{camera}

{DUAL_RATIO_STILL}

Keep the exact same time of day, sun direction, weather, cloud type, colour temperature, exposure and road condition across all seven views. Use premium photorealistic Japanese automotive advertising photography, natural reflections, a level horizon and physically correct tyre placement.

{TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
{IMAGE_NEGATIVE}

【RULES｜產出規則】
1. Upload the same approved vehicle reference pack and the approved Step 01 anchor for every angle.
2. From Step 02 onward, also upload the immediately previous approved angle.
3. Only the physical camera position changes; vehicle, ground contacts, environment and sunlight stay fixed.
4. Generate one image, approve identity and world continuity, then proceed to the next angle.
5. The protected 9:16 corridor is a composition guide, not permission to squeeze or resize the car."""


ORBIT_VIDEO = f"""【PROMPT】
Use the uploaded start frame and end frame as strict visual anchors. Create one continuous 10-second photorealistic drone-camera segment between them for Google Flow Lite.

{IDENTITY}

IMPORTANT PHYSICAL RULE: the Honda Freed is a fixed real-world object parked on the ground. Its four tyre contact points, parking lines and attached shadow remain locked to the exact same physical coordinates throughout. The car does not translate, rotate, pivot, slide, float or turn to face the camera. Wheels do not roll and steering does not change. This is NOT a rotating turntable product shot.

Only the physical camera travels through real three-dimensional space like a stabilized cinematic drone. The complete 30-second orbit is divided into three 10-second arcs in one continuous direction. Clip A uses 01 front-left as start and 03 rear-left as end, physically passing the left side near approved view 02. Clip B uses 03 rear-left as start and 05 rear-right as end, physically passing behind the car near approved view 04. Clip C uses 05 rear-right as start and 01 front-left as end, physically passing the right side and front near approved views 06 and 07. Upload only the matching start and end frames for each generation. Never take the reverse or shorter path if it breaks this stated orbit direction.

Use real camera translation, a gentle curved path, approximately 0.9–2 metres camera height, a natural 45–60mm equivalent perspective and physically correct foreground/background parallax. Parking lines, nearby posts, coastline and background shift through perspective. No digital zoom, teleportation, movement through the car or sudden reversal. First and final frames closely match the supplied anchors, with gentle motion continuing through the final frame.

{DUAL_RATIO_VIDEO}

Preserve the same parking bay, asphalt, lines, seawall, coastline, sea, hills, buildings, sky, sunlight and shadows. {TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
No turntable shot, car rotating toward camera, pivoting or spinning, sliding over parking lines, wheels moving relative to asphalt, independent shadow rotation, static background while car angle changes, fake 2D image rotation, digital pan across a still, zoom-only movement, warped geometry, wheel morphing, camera teleportation, text or licence characters.

【RULES｜產出規則】
1. Generate exactly three 10-second Flow Lite clips using the same prompt and these frame pairs: A 01→03 via the left side, B 03→05 via the rear, C 05→01 via the right side and front.
2. The background must show real parallax caused by physical camera travel; the car stays fixed to the ground.
3. Keep direction, speed and camera height compatible at clip boundaries for editing.
4. Inspect the 16:9 clip before making 9:16. Crop only if the complete car remains in the protected corridor throughout.
5. If any frame fails the crop test, use the native 9:16 still and orbit prompts instead of forcing the crop.
6. Edit A+B+C in that order. Straight cuts give about 30 seconds; two short 0.3-second crossfades give about 29.4 seconds."""


def coast_still(camera_view):
    return f"""【PROMPT】
{IDENTITY}

{REFERENCE_ROLE}

DEFAULT WHEN NO SCENERY PHOTO IS PROVIDED: a geographically believable coastal road in northern Okinawa, Japan, with calm blue-green sea, curved coastline, low concrete or stone seawall, lush subtropical hills, clean Japanese asphalt, correct white road markings, left-side traffic, sparse ordinary traffic and bright natural afternoon light. No high-rise skyline, generic California or Mediterranean coastline, fantasy tropical beach or driving on sand.

CAMERA VIEW:
{camera_view}

Show the complete vehicle and sufficient road ahead. Use realistic reflections, attached road shadow, restrained colour and premium photorealistic Japanese automotive-commercial styling.

{DUAL_RATIO_STILL}

{TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
No wrong generation or trim, vehicle morphing, altered paint, redesigned wheels, extra doors, wrong-side driving, car on sand, urban skyline, distorted road, impossible sea placement, fisheye, text, licence characters, caption or watermark.

【RULES｜產出規則】
1. The uploaded vehicle photos override all model knowledge.
2. Keep the full car and road direction readable inside the protected vertical corridor.
3. Approve identity, left-side traffic and road geometry before animation.
4. If the car becomes too small for the intended 16:9 ad, keep the strong wide master and plan a native 9:16 reframe."""


def coast_video(camera_motion):
    return f"""【PROMPT】
Animate the supplied approved coastal still into one continuous 10-second premium photorealistic automotive drone shot for Google Flow Lite.

{IDENTITY}

The exact Honda Freed drives forward at a safe, steady speed along the northern Okinawa coastal road in the correct left-side lane. Wheels rotate at the correct speed, tyres remain attached to the road, the body follows the lane and suspension shows subtle realistic movement. The car does not slide sideways, rotate independently, drift, change lanes or accelerate aggressively.

The drone maintains the reference view while physically tracking through real three-dimensional space: stabilized forward motion, gently changing distance, smooth altitude control and natural parallax. Coastline, markings and lamp posts pass naturally. No sudden zoom, teleportation, stationary-car orbit or turntable effect. Keep sea, coastline, seawall, green hills, daylight, traffic direction and horizon physically stable.

CAMERA MOTION FOR THIS CLIP:
{camera_motion}

{DUAL_RATIO_VIDEO}

{TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
No sideways slide, independent car rotation, drifting, lane change, wrong-side traffic, wheel slip, floating tyres, body or wheel morphing, colour change, changing vehicle length, extra doors, sudden zoom, camera teleportation, readable signs, licence characters, caption or watermark.

【RULES｜產出規則】
1. Generate exactly 10 seconds and approve the 16:9 master first.
2. Test a centre 9:16 crop across every frame, not only the first frame.
3. Direct crop is approved only if the complete car, shadow and useful road context remain visible throughout.
4. If crop QA fails, use the native 9:16 coastal still and video prompts.
5. The final coastal film uses three 10-second clips in order: high aerial approach, ocean-side parallel tracking, low rear pull-away. Straight cuts give about 30 seconds; two 0.3-second crossfades give about 29.4 seconds."""


NATIVE_VERTICAL_STILL = f"""【PROMPT】
Use the approved 16:9 image and all real vehicle photographs as strict references. Reconstruct the same shot as a native 9:16 vertical composition; do not crop, stretch or outpaint the 16:9 pixels mechanically.

{IDENTITY}

{REFERENCE_ROLE}

Preserve the same physical scene, car identity, time, light, weather, road layout and intended camera angle. Move the physical camera farther away or adjust its height slightly so the complete vehicle, all four tyres, attached shadow and essential road context fit naturally inside 9:16 with 8 percent safe margins. Maintain a natural 50–70mm equivalent perspective and realistic parallax. For parking angles, the car remains fixed to the same parking lines. For the coastal shot, preserve correct left-side traffic and the same direction of travel.

{TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
No simple crop, squeeze, stretch, fisheye, enlarged wheelbase, shortened body, missing car end, new trim, changed background geography, wrong-side traffic, text or licence characters.

【RULES｜產出規則】
1. Use this only when the centre crop from 16:9 fails composition QA.
2. Match the approved 16:9 creative intent, but solve the vertical layout through physical camera placement.
3. Output one native 9:16 image at the highest available resolution."""


NATIVE_VERTICAL_ORBIT = f"""【PROMPT】
Use the approved native 9:16 start and end frames as strict anchors. Create one continuous 10-second native 9:16 vertical version of the same stationary-vehicle orbit segment for Google Flow Lite.

{IDENTITY}

The car, all tyre contact points, parking lines and attached shadow remain completely fixed. Only the stabilized physical drone camera translates through the same three-dimensional parking environment. Preserve real parallax, one continuous orbit direction, compatible speed and natural 50–70mm perspective. Keep the complete car and shadow inside 8 percent vertical safe margins throughout. No turntable rotation, digital zoom, crop simulation, teleportation or geometry morphing.

{TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
No vehicle rotation, pivot, slide, wheel movement, shadow drift, static flat background, fake 2D rotation, zoom-only movement, squeeze, fisheye, text or licence characters.

【RULES｜產出規則】
1. Use this only for orbit segments that fail 16:9-to-9:16 crop QA.
2. Use the corresponding native vertical adjacent-angle frames.
3. Match the approved 16:9 segment's direction and 10-second timing so both specifications feel like one campaign."""


NATIVE_VERTICAL_COAST = f"""【PROMPT】
Animate the approved native 9:16 coastal still into one continuous 10-second native vertical automotive drone shot for Google Flow Lite.

{IDENTITY}

The exact Honda Freed drives steadily in the correct left-side lane along the same northern Okinawa coast. Wheels and suspension move naturally; tyres remain attached to the road. The drone tracks physically with smooth forward motion and real parallax. Keep the complete vehicle, attached shadow and enough road ahead inside 8 percent safe margins throughout. Preserve the 16:9 master's time, light, coastline, driving direction and commercial tone, but solve the composition for vertical viewing through physical camera placement.

{TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
No crop simulation, sideways slide, wrong lane, independent rotation, wheel slip, distorted body, sudden zoom, teleportation, text, licence characters or watermark.

【RULES｜產出規則】
1. Use this only when the 16:9 coastal master fails centre-crop QA.
2. Output native 9:16 at the highest available resolution and exactly 10 seconds.
3. Match the corresponding approved 16:9 clip's camera motion, action, speed and identity rather than inventing a new campaign shot."""


VEHICLES = [
    ("01", "Daihatsu Move Canbus", "4", "世代／年式待實車照"),
    ("02", "Suzuki Hustler", "4", "世代／年式待實車照"),
    ("03", "Mitsubishi Delica", "4", "完整型號／世代待確認"),
    ("04", "Suzuki Jimny 660cc", "4", "世代／套件待實車照"),
    ("05", "Suzuki Jimny 1500cc", "4", "市場名稱／世代待確認"),
    ("06", "Suzuki Solio", "5", "世代／年式待實車照"),
    ("07", "Toyota Sienta 二代", "5", "前後期／套件待實車照"),
    ("08", "Honda Freed", "5", "世代待確認"),
    ("09", "Toyota Yaris Cross", "5", "年式／套件待實車照"),
    ("10", "Toyota Raize", "5", "年式／套件待實車照"),
    ("11", "Toyota Prius", "5", "世代／年式待確認"),
    ("12", "Toyota Sienta 三代", "5", "年式／套件待實車照"),
    ("13", "Honda Freed 三代", "5", "Demo；實車照待上傳"),
    ("14", "Honda Stepwagon", "8", "世代／年式／套件待確認"),
    ("15", "Toyota Voxy 80系", "7", "前後期／套件待實車照"),
    ("16", "Toyota Voxy 90系", "7–8", "座椅配置／套件待確認"),
    ("17", "Nissan Serena", "8", "世代／年式／套件待確認"),
    ("18", "Toyota Vellfire 20系", "7", "前後期／套件待實車照"),
    ("19", "Toyota Alphard 30系", "8", "8座；前後期／套件待實車照"),
    ("20", "Toyota Alphard 30系", "7", "7座；前後期／套件待實車照"),
    ("21", "Toyota Alphard 40系", "7", "套件待實車照"),
    ("22", "Range Rover", "5", "完整型號／世代待確認"),
    ("23", "Porsche 718", "2", "Cayman／Boxster待確認"),
]

DEFAULT_TASKS = {k: "todo" for k in (
    "spec references anchor169 angles169 orbitClips169 orbitMaster169 orbitCropQa orbit916 "
    "coastStill169 coastClip169 coastMaster169 coastCropQa coast916 finalQa"
).split()}


def build():
    image_items = [{
        "type": f"OBcar 圖・Step {number} {label}",
        "purpose": "Freed 三代 Demo｜16:9 主圖＋9:16 保護框",
        "engine": "ChatGPT Images",
        "status": "prompt",
        "text": image_prompt(camera),
    } for number, label, camera in CAMERAS]

    coast_items = []
    for still_step, video_step, label, camera, motion in COAST_CLIPS:
        coast_items.extend([
            {"type": f"OBcar 圖・Step {still_step} 海邊{label}定格", "purpose": "Freed 三代 Demo｜16:9 主圖＋9:16 保護框", "engine": "ChatGPT Images", "status": "prompt", "text": coast_still(camera)},
            {"type": f"OBcar 影片・Step {video_step} 海邊{label}", "purpose": "Flow Lite｜10秒｜30秒成片第 1–3 段", "engine": "Google Flow Lite", "status": "prompt", "text": coast_video(motion)},
        ])

    items = image_items + [
        {"type": "OBcar 影片・Step 08 360°三段環繞", "purpose": "Flow Lite｜同一 Prompt 重用 3 組首尾幀｜每段10秒", "engine": "Google Flow Lite", "status": "prompt", "text": ORBIT_VIDEO},
    ] + coast_items + [
        {"type": "OBcar 圖・Step 15 原生9:16重構", "purpose": "只有裁切 QA 失敗才使用｜停車或海邊定格", "engine": "ChatGPT Images", "status": "prompt", "text": NATIVE_VERTICAL_STILL},
        {"type": "OBcar 影片・Step 16 原生9:16定點環繞", "purpose": "只有裁切 QA 失敗的360°段才使用｜10秒", "engine": "Google Flow Lite", "status": "prompt", "text": NATIVE_VERTICAL_ORBIT},
        {"type": "OBcar 影片・Step 17 原生9:16海邊跟拍", "purpose": "只有裁切 QA 失敗的海邊段才使用｜10秒", "engine": "Google Flow Lite", "status": "prompt", "text": NATIVE_VERTICAL_COAST},
    ]

    tracker_vehicles = []
    for ident, name, seats, note in VEHICLES:
        tasks = {"spec": "review"} if ident == "13" else {}
        tracker_vehicles.append({"id": ident, "name": name, "seats": seats, "note": note, "tasks": tasks})

    return {
        "updatedAt": "2026-08-01T16:31:00+09:00",
        "tracker": {"defaultTasks": DEFAULT_TASKS, "vehicles": tracker_vehicles},
        "briefs": [{
            "date": "2026-08-01",
            "stream": "obcar",
            "title": "Freed 三代 Demo｜兩支約30秒成片",
            "focus": "ChatGPT 生圖 → Flow Lite 每段10秒×3 → 16:9／9:16 雙規格",
            "meta": "7 張定點角度＋3 段完整環繞｜3 張海邊定格＋3 段跟拍｜兩種比例 QA",
            "summary": "每條 Prompt 都是可單獨複製的完整包，內含 Negative Prompt 與 Rules。Step 01–07 用 ChatGPT Images 生成同一停車場景；Step 08 用 01→03、03→05、05→01 三組首尾幀各生成 10 秒，合成約 30 秒完整 360°。Step 09–14 是三組海邊定格與 10 秒 Flow Lite 跟拍，合成另一支約 30 秒影片。有風景照就作為環境參考；沒有則使用 Prompt 內預設的沖繩海邊停車場或北部海岸道路。所有鏡頭先做 16:9 並保護中央 9:16 走廊；直式裁切逐幀通過才交付，否則使用 Step 15–17 原生 9:16 重構。",
            "items": items,
        }],
    }


if __name__ == "__main__":
    target = ROOT / "data" / "obcar.json"
    target.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {target}")
