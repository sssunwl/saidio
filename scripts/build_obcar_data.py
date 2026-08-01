#!/usr/bin/env python3
"""Build the public OBcar production line data deterministically."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IDENTITY = """Use all uploaded real vehicle photographs as strict immutable references. They are the single source of truth. For this demo, the subject is the exact standard-body third-generation Honda Freed e:HEV shown in those photographs, in its real muted blue-grey paint. Preserve its actual body proportions, short bonnet, roofline, wheelbase, grille and full-width glossy-black front panel, the slim horizontal chrome trim beside the Honda emblem, two rectangular upper DRL modules on each side, the exact lower projector-lamp arrangement, smooth standard bumper, exact five-pair black-and-silver factory wheels and tyres, ride height, mirrors, windows and pillars, dual sliding-door seams and handles, fuel door, rear hatch, vertical taillights, rear wiper, FREED badge, e:HEV badge and Honda badge placement. Never infer a different trim from general model knowledge. Do not convert it into Freed Crosstar or invent a grille, headlamp, wheel, roof rail, wheel-arch cladding, aero part, body kit, spoiler, oversized wheel, lowered suspension or accessory absent from the photographs."""

REFERENCE_ROLE = """REFERENCE ROLE SEPARATION: the uploaded vehicle photographs define only the vehicle identity. Any uploaded scenery photographs define only the environment, geography, road layout, coastline, architecture, weather and atmosphere. Do not copy vehicles that appear in scenery photographs and do not replace the Honda Freed with a background vehicle. If scenery photographs are supplied, infer one coherent three-dimensional version of that location rather than pasting them as flat backdrops. If no scenery photograph is supplied, use the default northern Okinawa environment described below."""

LANDSCAPE_STILL = """FORMAT AND COMPOSITION: generate a native 16:9 landscape image at the highest available resolution. Build a strong automotive-advertising composition specifically for 16:9; do not reserve a 9:16 crop corridor. Keep the complete vehicle, all four tyres and attached shadow visible with at least 8 percent outer-frame breathing room. The vehicle may occupy about 45–55 percent of the full image width. Use physical camera distance and a natural 50–65mm equivalent perspective, never wide-angle stretching."""

VERTICAL_STILL = """FORMAT AND COMPOSITION: generate a new native 9:16 vertical image at the highest available resolution; do not crop, stretch or mechanically outpaint a 16:9 image. Inside the 9:16 frame, protect a centred 4:5 action-safe zone: it uses the full frame width and the middle 70.3 percent of frame height, equivalent to 1080×1350 inside 1080×1920. The top 14.8 percent and bottom 14.8 percent are trim zones containing only expendable sky, distant scenery or empty road. Keep the complete vehicle, every tyre, attached shadow, key road direction and all important objects inside the centred 4:5 safe zone throughout. Move the physical camera farther away while preserving the same azimuth; use a natural 55–75mm equivalent perspective. Never squeeze or shorten the car to make it fit."""

LANDSCAPE_VIDEO = """FORMAT AND COMPOSITION: create a native 16:9 landscape clip. Keep the complete vehicle, all four tyres and attached shadow within 8 percent outer-frame margins throughout. Compose for 16:9 only; do not shrink the car to protect a vertical crop."""

VERTICAL_VIDEO = """FORMAT AND COMPOSITION: create a native 9:16 vertical clip, not a crop or simulated reframe. Throughout every frame, keep the complete vehicle, every tyre, attached shadow, key road direction and all important moving objects inside the centred 4:5 action-safe zone. In a 1080×1920 output this safe zone is 1080×1350, from y=285 to y=1635; the top and bottom 14.8 percent contain only expendable sky, distant scenery or empty road. The camera may travel farther from the car than in 16:9, but its physical direction and campaign timing must match."""

PARKING_WORLD = """DEFAULT WHEN NO SCENERY PHOTO IS PROVIDED: one fixed, spatially coherent seaside public parking area in northern Okinawa, Japan, with clean asphalt, one simple rectangular parking bay, two straight white bay lines, a low concrete seawall, calm blue-green sea, curved coastline, subtropical green hills and bright natural afternoon light. Keep nearby geometry simple: no wheel stop beside the car, no pole cutting the frame, no crowd, readable sign or resort styling. The vehicle is centred inside one bay; its longitudinal axis is exactly parallel to both bay lines, all four tyres are inside the lines, no white line passes under the body, front wheels point straight ahead and the car never sits across two bays. The car remains locked to the same world coordinates and compass heading across the series. Tyre contact points and shadow remain attached to the exact same ground locations. Road edges, parking lines, seawall, hills, coastline and horizon stay fixed in world space. Reconstruct the same environment from each camera position with correct occlusion, perspective and parallax; never paste a flat background behind a rotated car."""

COAST_WORLD = """DEFAULT WHEN NO SCENERY PHOTO IS PROVIDED: one geographically believable coastal road in northern Okinawa, Japan, with calm blue-green sea, curved coastline, a low concrete or stone seawall, lush subtropical hills, clean Japanese asphalt, correct white markings, left-side traffic, sparse ordinary traffic and bright natural afternoon light. No high-rise skyline, generic California or Mediterranean coastline, fantasy tropical beach or driving on sand."""

TEXT_RULE = """No readable Japanese or English text, place name, shop name, road-sign wording, licence plate characters, caption or watermark. Any unavoidable sign must be blank, turned away, hidden, distant or naturally out of focus. Use a plain blank white promotional licence plate. Authentic Honda and factory model badges may remain only when accurately supported by the uploaded vehicle photographs."""

IMAGE_NEGATIVE = """STRICTLY FORBIDDEN: rotating the vehicle, turntable photography, changing the car's compass direction, moving tyre positions relative to parking lines, parking across two bays, a line passing under the car, static pasted background, mirroring, impossible coastline movement, inconsistent road layout or sun direction, rotating shadow, fisheye, extreme wide-angle stretching, fake text, licence mutation, vehicle morphing, or changing body length, height, doors, chrome trim, headlights, taillights, badges, trim or wheels. Output one image only; no collage or contact sheet."""

CAMERAS = [
    ("01", "前左定錨圖", "Front-left three-quarter view. Camera azimuth about 35 degrees left of the vehicle's forward direction and height about 1.1 metres. This is the master scene anchor."),
    ("02", "正左側", "Perfect left-side profile. Camera perpendicular to the left side and height about 1.2 metres. Wheels align naturally in perspective."),
    ("03", "後左45°", "Rear-left three-quarter view. Camera azimuth about 145 degrees from the vehicle's forward direction and height about 1.1 metres."),
    ("04", "正後", "Perfect centred rear view. Camera aligned with the longitudinal centre line and height about 1.15 metres. Rear design is symmetrical."),
    ("05", "後右45°", "Rear-right three-quarter view. Camera azimuth about 215 degrees from the vehicle's forward direction and height about 1.1 metres."),
    ("06", "正右側", "Perfect right-side profile. Camera perpendicular to the right side and height about 1.2 metres. Preserve all visible door seams and handles."),
    ("07", "前右45°", "Front-right three-quarter view. Camera azimuth about 325 degrees from the vehicle's forward direction and height about 1.1 metres."),
]

COAST_CLIPS = [
    ("09", "10", "高空接近", "High wide aerial establishing view, about 45 metres above and 35 metres behind the car, diagonally toward the ocean side. The car is identifiable while the Okinawa coastline initially dominates.", "Begin wide and high. Descend and fly gently closer while tracking the car, ending in a medium-high rear three-quarter view. Apparent size changes only through physical approach, never digital zoom."),
    ("11", "12", "海側平行跟拍", "Elevated ocean-side tracking view, about 8 metres above and 14 metres from the car. Show a complete side profile with a slight front three-quarter angle; the car is the main subject and sea remains visible.", "Fly parallel on the ocean side at a stable safe distance. Move slightly forward in the final third, ending with a gentle elevated front three-quarter view. Do not orbit or cross the driving lane."),
    ("13", "14", "低空後方拉遠", "Low rear three-quarter tracking view, about 2.2 metres above and 9 metres behind the car. Emphasize rear design, taillights and wheels while retaining coastline and road ahead.", "Begin low at the rear three-quarter view. During the second half, climb gently and fly backward to reveal more road, sea and hills. The car keeps constant speed and becomes smaller only through camera travel."),
]


def ratio_still(aspect):
    return LANDSCAPE_STILL if aspect == "16:9" else VERTICAL_STILL


def ratio_video(aspect):
    return LANDSCAPE_VIDEO if aspect == "16:9" else VERTICAL_VIDEO


def image_prompt(camera, aspect, prefix):
    return f"""【PROMPT】
{IDENTITY}

{REFERENCE_ROLE}

{PARKING_WORLD}

CAMERA POSITION:
{camera}

{ratio_still(aspect)}

Keep the exact same time of day, sun direction, weather, cloud type, colour temperature, exposure and road condition across all seven {aspect} views. Use premium photorealistic Japanese automotive advertising photography, natural reflections, a level horizon and physically correct tyre placement.

{TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
{IMAGE_NEGATIVE}

【RULES｜產出規則】
1. Upload the same approved vehicle reference pack for every image.
2. Use the approved {prefix}01 image as the scene anchor for all later {aspect} parking angles.
3. From {prefix}02 onward, also upload the immediately previous approved {aspect} angle.
4. Only physical camera position changes; vehicle, ground contacts, environment and sunlight remain fixed.
5. Generate one image, approve vehicle identity, parking alignment and world continuity, then continue."""


def orbit_video(aspect, prefix):
    return f"""【PROMPT】
Use the uploaded native {aspect} start frame and end frame as strict visual anchors. Create one continuous 10-second native {aspect} photorealistic drone-camera segment for Google Flow Lite.

{IDENTITY}

IMPORTANT PHYSICAL RULE: the Honda Freed is a fixed real-world object parked on the ground. Its four tyre contact points, parking lines and attached shadow remain locked to the exact same coordinates. The car does not translate, rotate, pivot, slide, float or turn to face camera. Wheels do not roll and steering does not change. This is NOT a rotating turntable shot.

The 30-second orbit is divided into three 10-second arcs in one direction. Clip A uses {prefix}01 front-left as start and {prefix}03 rear-left as end, passing the left side near approved view {prefix}02. Clip B uses {prefix}03 as start and {prefix}05 rear-right as end, passing behind near {prefix}04. Clip C uses {prefix}05 as start and {prefix}01 as end, passing the right side and front near {prefix}06 and {prefix}07. Upload only the matching start and end frames for each generation. Never take a reverse path that breaks this direction.

Only the physical stabilized drone camera translates through real three-dimensional space. Use a gentle curve, natural perspective and physically correct foreground/background parallax. Parking lines, coastline and background shift through perspective. No digital zoom, teleportation, movement through the car or sudden reversal. First and final frames closely match the anchors.

{ratio_video(aspect)}

Preserve the same parking bay, asphalt, lines, seawall, coast, sea, hills, sky, sunlight and shadows. {TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
No turntable shot, car rotating toward camera, pivoting, spinning, sliding over lines, wheel movement relative to asphalt, independent shadow rotation, static background while car angle changes, fake 2D rotation, digital pan, zoom-only movement, warped geometry, wheel morphing, camera teleportation, text or licence characters.

【RULES｜產出規則】
1. Generate exactly three 10-second clips with frame pairs A {prefix}01→{prefix}03 via left, B {prefix}03→{prefix}05 via rear, C {prefix}05→{prefix}01 via right and front.
2. Real background parallax is mandatory; the car remains fixed to the ground.
3. Keep direction, speed and height compatible at clip boundaries.
4. Edit A+B+C in order. Straight cuts give about 30 seconds; two 0.3-second crossfades give about 29.4 seconds.
5. This is a native {aspect} output; do not crop or simulate the other aspect ratio."""


def coast_still(camera_view, aspect):
    return f"""【PROMPT】
{IDENTITY}

{REFERENCE_ROLE}

{COAST_WORLD}

CAMERA VIEW:
{camera_view}

Show the complete vehicle and sufficient road ahead. Use realistic reflections, attached road shadow, restrained colour and premium photorealistic Japanese automotive-commercial styling.

{ratio_still(aspect)}

{TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
No wrong generation or trim, vehicle morphing, altered paint, missing chrome trim, redesigned lights or wheels, extra doors, wrong-side driving, car on sand, urban skyline, distorted road, impossible sea placement, fisheye, text, licence characters, caption or watermark.

【RULES｜產出規則】
1. Uploaded vehicle photos override all model knowledge.
2. Preserve correct left-side traffic, complete vehicle identity and road geometry.
3. Generate and approve one native {aspect} image before animation.
4. Match the corresponding other-ratio shot's action, time, weather and campaign identity, but solve composition natively for {aspect}."""


def coast_video(camera_motion, aspect):
    return f"""【PROMPT】
Animate the supplied approved native {aspect} coastal still into one continuous 10-second native {aspect} photorealistic automotive drone shot for Google Flow Lite.

{IDENTITY}

The exact Honda Freed drives at a safe steady speed along the northern Okinawa coast in the correct left-side lane. Wheels rotate correctly, tyres stay attached to road, body follows the lane and suspension moves subtly. The car does not slide, rotate independently, drift, change lanes or accelerate aggressively.

The stabilized drone tracks through real three-dimensional space with physical forward motion, smooth altitude and natural parallax. Coastline, markings and posts pass naturally. No sudden zoom, teleportation, stationary-car orbit or turntable effect. Sea, coast, seawall, hills, daylight, traffic direction and horizon remain stable.

CAMERA MOTION FOR THIS CLIP:
{camera_motion}

{ratio_video(aspect)}

{TEXT_RULE}

【NEGATIVE PROMPT｜禁止項】
No sideways slide, independent rotation, drifting, lane change, wrong-side traffic, wheel slip, floating tyres, body or wheel morphing, colour change, changing vehicle length, extra doors, sudden zoom, camera teleportation, readable signs, licence characters, caption or watermark.

【RULES｜產出規則】
1. Generate exactly 10 seconds as a native {aspect} clip.
2. The final coastal film uses three clips in order: high aerial approach, ocean-side parallel tracking, low rear pull-away.
3. Match the corresponding other-ratio clip's action, speed, light and identity while solving composition natively for {aspect}.
4. Straight cuts give about 30 seconds; two 0.3-second crossfades give about 29.4 seconds."""


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
    ("13", "Honda Freed 三代", "5", "Demo；參考照已收到；16:9定錨待重生"),
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

TASK_FIELDS = (
    "spec references anchor169 angles169 orbitClips169 orbitMaster169 coastStills169 coastClips169 coastMaster169 "
    "anchor916 angles916 orbitClips916 orbitMaster916 coastStills916 coastClips916 coastMaster916 finalQa"
).split()
DEFAULT_TASKS = {key: "todo" for key in TASK_FIELDS}


def ratio_items(aspect, prefix):
    items = [{
        "type": f"OBcar 圖・{aspect} {prefix}{number} {label}",
        "purpose": f"Freed 三代 Demo｜原生 {aspect}",
        "engine": "ChatGPT Images",
        "status": "prompt",
        "aspect": aspect,
        "text": image_prompt(camera, aspect, prefix),
    } for number, label, camera in CAMERAS]
    items.append({
        "type": f"OBcar 影片・{aspect} {prefix}08 360°三段環繞",
        "purpose": f"原生 {aspect}｜Flow Lite｜3組首尾幀×10秒",
        "engine": "Google Flow Lite", "status": "prompt", "aspect": aspect,
        "text": orbit_video(aspect, prefix),
    })
    for still_no, video_no, label, camera, motion in COAST_CLIPS:
        items.extend([
            {"type": f"OBcar 圖・{aspect} {prefix}{still_no} 海邊{label}定格", "purpose": f"Freed 三代 Demo｜原生 {aspect}", "engine": "ChatGPT Images", "status": "prompt", "aspect": aspect, "text": coast_still(camera, aspect)},
            {"type": f"OBcar 影片・{aspect} {prefix}{video_no} 海邊{label}", "purpose": f"原生 {aspect}｜Flow Lite｜10秒", "engine": "Google Flow Lite", "status": "prompt", "aspect": aspect, "text": coast_video(motion, aspect)},
        ])
    return items


def build():
    items = ratio_items("16:9", "L") + ratio_items("9:16", "V")
    tracker_vehicles = []
    for ident, name, seats, note in VEHICLES:
        tasks = {"spec": "done", "references": "done", "anchor169": "review"} if ident == "13" else {}
        tracker_vehicles.append({"id": ident, "name": name, "seats": seats, "note": note, "tasks": tasks})
    return {
        "updatedAt": "2026-08-01T17:20:00+09:00",
        "tracker": {"defaultTasks": DEFAULT_TASKS, "vehicles": tracker_vehicles},
        "briefs": [{
            "date": "2026-08-01", "stream": "obcar",
            "title": "Freed 三代 Demo｜16:9＋9:16雙母版",
            "focus": "每個比例各14條｜ChatGPT生圖 → Flow Lite 3×10秒 → 約30秒成片",
            "meta": "16:9：7定點圖＋1環繞Prompt＋3海邊圖＋3海邊片｜9:16：完全對應；重要內容鎖在4:5安全區",
            "summary": "每條 Prompt 都可單獨複製，並自帶 Negative Prompt 與 Rules。16:9和9:16不再互相裁切，而是共享車款身分、場景、光線與運鏡方向後，各自原生生成14條。9:16的完整車身、四輪、陰影、道路方向與重要物件，在每一幀都必須留在中央4:5安全區；1080×1920時就是y=285至1635，上下只放可裁掉的天空、遠景或空道路。兩個比例的360°都用三段10秒閉合一圈；海邊片都用高空接近、海側平行、低空拉遠三段10秒。",
            "items": items,
        }],
    }


if __name__ == "__main__":
    target = ROOT / "data" / "obcar.json"
    target.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {target}")
