#!/usr/bin/env python3
"""Build the public OBcar production line data deterministically.

v2 (2026-08-01) — 三層極簡版。舊版每條 Prompt 5,200 字、每台車 28 條，23 台就是
300 萬字，貼都貼不完。v2 把重複的東西交回給它該待的地方：

  車款身分 → 上傳的實車照（形容詞永遠贏不過參考圖）
  場景     → 已批准的定錨圖（不再每條重建一次沖繩）
  禁止項   → negative 欄位寫一次（正文重複念 turntable / rotating 反而會招來它）

所以每條 Prompt 只剩「這一顆鏡頭」的內容，仍然自帶 PROMPT / NEGATIVE / RULES
三段，單獨複製即完整。

停車 360° 也不再需要七個角度圖：一張定錨圖 + 三段接力（每段用上一段尾幀，
Flow 的「延伸」直接支援），連續性由影片自己保證，不靠七張圖對齊。

要加車：在 VEHICLES 補 model / colour / body_note，把 ready 改成 True。
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── 車款主檔 ────────────────────────────────────────────────
# ready=True 才會產 Prompt。model 是唯一必須人工確認的欄位：寫錯世代，
# 模型就會照它的舊知識畫另一台車。colour 留空代表「以實車照為準」。
VEHICLES = [
    dict(id="01", name="Daihatsu Move Canbus", seats="4", ready=True, refs=False,
         model="third-generation Daihatsu Move Canbus kei tall wagon (LA850S, 2022 onwards)",
         colour="",
         body_note="Keep the exact Canbus round-lamp face and two-tone roof treatment shown in the photographs; do not swap between the Stripes and Theory front ends.",
         note="LA850S；待實車照確認前臉版本與車色"),
    dict(id="02", name="Suzuki Hustler", seats="4", ready=False, refs=False,
         model="", colour="", body_note="", note="世代／年式待實車照"),
    dict(id="03", name="Mitsubishi Delica Mini", seats="4", ready=True, refs=False,
         model="Mitsubishi Delica Mini kei tall wagon (B34A/B35A, 2023 onwards)",
         colour="",
         body_note="Keep the exact Delica Mini square face, stacked lamp units and black lower cladding shown in the photographs; it is not a Delica D:5 and not a Delica D:2.",
         note="按 4 座判定為 Delica Mini；若實際是 D:5／D:2 請改 model"),
    dict(id="04", name="Suzuki Jimny 660cc", seats="4", ready=False, refs=False,
         model="", colour="", body_note="", note="世代／套件待實車照"),
    dict(id="05", name="Suzuki Jimny 1500cc", seats="4", ready=False, refs=False,
         model="", colour="", body_note="", note="市場名稱（Jimny Sierra?）待確認"),
    dict(id="06", name="Suzuki Solio", seats="5", ready=False, refs=False,
         model="", colour="", body_note="", note="世代／年式待實車照"),
    dict(id="07", name="Toyota Sienta 二代", seats="5", ready=False, refs=False,
         model="", colour="", body_note="", note="前後期／套件待實車照"),
    dict(id="08", name="Honda Freed", seats="5", ready=False, refs=False,
         model="", colour="", body_note="", note="世代待確認（與 13 區分）"),
    dict(id="09", name="Toyota Yaris Cross", seats="5", ready=True, refs=False,
         model="Toyota Yaris Cross compact crossover (MXPB/MXPJ10, 2020 onwards, Japanese-market front end)",
         colour="",
         body_note="Keep the exact factory bumper, lamp graphics and wheel design shown in the photographs; do not add GR Sport or Adventure styling that is not there.",
         note="待實車照確認年式／套件"),
    dict(id="10", name="Toyota Raize", seats="5", ready=True, refs=False,
         model="Toyota Raize compact SUV (A200A/A210A, 2019 onwards)",
         colour="",
         body_note="Keep the exact Raize face, roof-rail presence or absence and wheel design shown in the photographs; it is not a RAV4 and not a Rocky-badged car.",
         note="待實車照確認年式／套件"),
    dict(id="11", name="Toyota Prius", seats="5", ready=False, refs=False,
         model="", colour="", body_note="", note="世代／年式待確認"),
    dict(id="12", name="Toyota Sienta 三代", seats="5", ready=True, refs=False,
         model="third-generation Toyota Sienta compact minivan (MXPC10/MXPL10, 2022 onwards), five-seat version",
         colour="",
         body_note="Keep the exact round-lamp face, sliding-door layout and wheel covers shown in the photographs; do not draw the boxier second-generation Sienta.",
         note="五座版；待實車照確認年式／套件"),
    dict(id="13", name="Honda Freed 三代", seats="5", ready=True, refs=True,
         model="standard-body third-generation Honda Freed e:HEV (2024 onwards)",
         colour="muted blue-grey metallic",
         body_note="Standard body, not the Crosstar version: smooth bumpers, no roof rails, no wheel-arch cladding. Keep the slim horizontal chrome trim running through the Honda emblem, the twin rectangular upper DRL modules and the exact two-tone factory wheels.",
         note="Demo 車；實車照已收；16:9 A01 v2 已批准"),
    dict(id="14", name="Honda Stepwagon", seats="8", ready=False, refs=False,
         model="", colour="", body_note="", note="世代／年式／套件待確認"),
    dict(id="15", name="Toyota Voxy 80系", seats="7", ready=False, refs=False,
         model="", colour="", body_note="", note="前後期／套件待實車照"),
    dict(id="16", name="Toyota Voxy 90系", seats="7–8", ready=False, refs=False,
         model="", colour="", body_note="", note="座椅配置／套件待確認"),
    dict(id="17", name="Nissan Serena", seats="8", ready=False, refs=False,
         model="", colour="", body_note="", note="世代／年式／套件待確認"),
    dict(id="18", name="Toyota Vellfire 20系", seats="7", ready=False, refs=False,
         model="", colour="", body_note="", note="前後期／套件待實車照"),
    dict(id="19", name="Toyota Alphard 30系", seats="8", ready=False, refs=False,
         model="", colour="", body_note="", note="8座；前後期／套件待實車照"),
    dict(id="20", name="Toyota Alphard 30系", seats="7", ready=False, refs=False,
         model="", colour="", body_note="", note="7座；外觀可能與 19 共用同一套圖"),
    dict(id="21", name="Toyota Alphard 40系", seats="7", ready=False, refs=False,
         model="", colour="", body_note="", note="套件待實車照"),
    dict(id="22", name="Range Rover", seats="5", ready=False, refs=False,
         model="", colour="", body_note="", note="完整型號待確認（Sport／Evoque／Velar？）"),
    dict(id="23", name="Porsche 718", seats="2", ready=False, refs=False,
         model="", colour="", body_note="", note="Cayman／Boxster 待確認"),
]


# ── Layer 1：CAR CARD（每條 Prompt 的開頭）──────────────────
def car_card(v):
    colour = f", in {v['colour']} paint" if v["colour"] else ", in its exact photographed colour"
    note = f" {v['body_note']}" if v["body_note"] else ""
    return (
        f"CAR: the exact vehicle in the uploaded photographs — {v['model']}{colour}.\n"
        "The photographs override all model knowledge and all general knowledge of this "
        "nameplate. Keep its exact face, lights, grille, wheels, badges, ride height, body "
        f"length and door layout. Do not restyle it and do not upgrade the trim level.{note}"
    )


# ── Layer 2：場景 ───────────────────────────────────────────
PARKING = """Photoreal Japanese automotive advertising photograph.

The car is parked, engine off, centred in ONE marked bay of a quiet seaside public parking area in northern Okinawa: clean asphalt, two straight white bay lines, a low concrete seawall, calm blue-green sea, curved coastline, green subtropical hills, bright natural afternoon sun.

Parking geometry: the car's long axis is parallel to both bay lines, all four tyres sit well inside them, no white line runs under the body or bumpers, and the front wheels point straight ahead. Nothing else stands near the car — no wheel stop, no pole, no bollard, no people, no other vehicle."""

PARKING_CAM = ("front-left three-quarter, about 35 degrees left of the nose, 1.1 metres high, "
               "50–65mm equivalent. Whole car, all four tyres and its attached shadow visible, "
               "car about 50 percent of frame width, level horizon.")

COAST = """Photoreal automotive advertising drone photograph.

The car drives along a coastal road in northern Okinawa — left-hand traffic, in the correct lane. Blue-green sea and a low seawall on one side, green subtropical hills on the other, clean Japanese asphalt, correct white road markings, bright afternoon light, sparse distant traffic."""

COAST_SHOTS = [
    ("a", "高空遠景",
     "high aerial, about 60 metres above and behind the car on the ocean side, 24mm equivalent. "
     "The coastline is the main subject and the car reads small but clearly identifiable.",
     "The drone descends and closes in, ending in a medium rear three-quarter tracking view. The car grows because the drone physically flies closer, never by zooming."),
    ("b", "海側平行",
     "about 8 metres above the road, flying parallel to the car on the ocean side, 50mm equivalent, "
     "full side profile turning into a slight front three-quarter. The car is the main subject.",
     "The drone holds parallel, then eases forward into an elevated front three-quarter tracking view, staying outside the driving lane."),
    ("c", "低空後方",
     "about 1.8 metres above the road and 6 metres behind the car, 70mm equivalent, rear three-quarter, "
     "compressed perspective, coastline beside the car.",
     "The drone climbs and drifts backwards, opening out to a wide coastal view while the car keeps its steady speed."),
]

# ── 畫幅 ────────────────────────────────────────────────────
LANDSCAPE_STILL = ("Camera: {cam}\n\nBlank white promotional plate. No readable text or signage "
                   "anywhere.\nNative 16:9, highest available resolution.")

VERTICAL_FROM_LANDSCAPE = """Use the uploaded approved 16:9 frame as the scene reference: same parking area or same stretch of coast, same time of day, same sun direction, same weather, same camera azimuth, same car position and heading. Only the framing changes.

Rebuild that same moment as a NEW native 9:16 vertical photograph. Do not crop, stretch or outpaint the 16:9 image — move the physical camera back instead, keeping the same angle.

Camera: {cam} Step back far enough that the whole car, all four tyres, its attached shadow and the sea horizon sit inside the centred 4:5 action-safe zone — in 1080×1920 that zone is 1080×1350, from y=285 to y=1635. The top and bottom 14.8 percent may be cropped by platform UI, so they hold only expendable sky, distant scenery or empty road.

Blank white promotional plate. No readable text or signage anywhere.
Native 9:16, highest available resolution."""

LANDSCAPE_CLIP = ("Native 16:9 clip, 10 seconds. Keep the whole car, all four tyres and its attached "
                  "shadow inside 8 percent outer margins throughout.")

VERTICAL_CLIP = """Native 9:16 clip, 10 seconds — a real vertical render, not a crop or a reframe. In every frame keep the whole car, all four tyres, its attached shadow and the road direction inside the centred 4:5 action-safe zone (1080×1350 inside 1080×1920, from y=285 to y=1635). The top and bottom 14.8 percent hold only expendable sky, scenery or empty road. The camera may sit farther from the car than in 16:9, but travels in the same direction with the same timing."""

# ── Layer 3：鏡頭 ───────────────────────────────────────────
ORBIT = """The parked car stays exactly where it is: engine off, wheels straight, tyres glued to the same points on the asphalt, attached shadow anchored to the same ground.

Only the camera moves. A stabilised drone slides smoothly leftwards through real three-dimensional space around the car, {leg}, holding 4–5 metres distance and about 1.2 metres height.

Real parallax does all the work: the bay lines converge in a new direction, the seawall, coastline and hills shift behind the car as the camera travels, and reflections move across the paint.

Photoreal Japanese car commercial, gimbal-smooth, one continuous direction, no zoom. Keep the camera moving through the last frame so the next clip can continue from it."""

ORBIT_LEGS = [
    ("P1", "前左→正左", "travelling from the front-left three-quarter round to the full left side"),
    ("P2", "正左→正後", "continuing that same leftward travel from the full left side round to the centred rear"),
    ("P3", "正後→前右", "continuing that same travel from the centred rear round the right side to the front-right three-quarter"),
]

COAST_CLIP = """Animate this photograph. The car drives forward at a steady safe speed in the same lane: wheels rolling at the correct speed, tyres attached to the road, subtle suspension movement, body following the curve of the road.

The drone keeps this photograph's framing and tracks the car through real space. Coastline, road markings and roadside poles pass naturally through frame. {move}

Photoreal Japanese automotive and travel commercial, gimbal-smooth, no zoom."""

# ── Negative（每種一行，只寫一次）───────────────────────────
NEG_STILL = ("text, signage, japanese characters, licence plate characters, watermark, caption, collage, "
             "multiple views, extra vehicles, people, wheel stop, pole in frame, fisheye, wide-angle stretching, "
             "altered wheels, altered headlights, altered badges, roof rails, wheel-arch cladding, body kit, "
             "lowered stance, car parked across two bays, wrong generation, wrong trim level")
NEG_ORBIT = ("turntable, rotating car, car pivoting, wheels turning, car sliding, car drifting, frozen background, "
             "background without parallax, digital zoom, camera passing through the car, sudden reversal, "
             "morphing bodywork, changing wheels, text")
NEG_COAST = ("car sliding sideways, drifting, changing lanes, sudden acceleration, wobbling horizon, digital zoom, "
             "orbiting a stationary car, turntable, morphing bodywork, changing wheels, changing colour, "
             "right-side traffic, readable road signs, licence plate characters, captions")

# ── Rules（給人看的操作規則）────────────────────────────────
RULES = {
    "anchor169": "1. 每次都上傳同一組實車照，這是車款唯一真相。\n2. 一次只生一張；先批准車款身分與停車幾何再往下。\n3. 批准後這張就是本車的場景主定錨，之後每個鏡頭都要附上它。",
    "anchor916": "1. 上傳「已批准的 16:9 A01」＋同一組實車照。\n2. 原生重生 9:16，不要裁 16:9，也不要外擴。\n3. 全車、四輪、陰影、海平線都要落在中央 4:5 內才算過。",
    "orbit_first": "1. 首幀＝已批准的 A01；只生 10 秒。\n2. 先驗三件事：車沒轉、輪胎沒滑、背景有真實視差。\n3. 這段過了才做 P2，不要三段一起生。",
    "orbit_next": "1. 首幀＝上一段的尾幀（Flow 直接按「延伸」最穩）。\n2. 只生 10 秒，方向不可反轉，速度與高度要接得上。\n3. P1+P2+P3 直接剪接約 30 秒；要柔一點就加兩個 0.3 秒疊化。",
    "coast_still": "1. 上傳同一組實車照；三張定格圖要同一天光、同一段海岸。\n2. 一次只生一張，先批准車款與車道方向（左側通行）。\n3. 三張都批准後才開始動畫化。",
    "coast_clip": "1. 上傳對應的已批准定格圖，只生 10 秒。\n2. 車速穩定、不變換車道；靠近或拉遠必須是實體飛行，不是變焦。\n3. 成片順序固定：高空接近 → 海側平行 → 低空拉遠。",
}


def bundle(prompt, negative, rules):
    """每條 Prompt 都自帶三段，單獨複製即完整。"""
    return "\n".join(["【PROMPT】", prompt.strip(), "",
                      "【NEGATIVE PROMPT｜禁止項】", negative.strip(), "",
                      "【RULES｜產出規則】", rules.strip()])


def still(v, aspect, scene, cam):
    body = VERTICAL_FROM_LANDSCAPE.format(cam=cam) if aspect == "9:16" else LANDSCAPE_STILL.format(cam=cam)
    return f"{car_card(v)}\n\n{scene}\n\n{body}"


def clip_format(aspect):
    return VERTICAL_CLIP if aspect == "9:16" else LANDSCAPE_CLIP


def vehicle_items(v, aspect):
    """一台車、一個比例＝10 條 Prompt。"""
    tag = f"{v['name']}｜{v['seats']}座" + ("" if v["refs"] else "｜⚠️ 實車照未到")
    img_engine, vid_engine = "ChatGPT Images", "Google Flow Lite"
    out = [{
        "type": f"OBcar 圖・{aspect} A01 停車場定錨圖",
        "purpose": tag, "engine": img_engine, "status": "prompt", "aspect": aspect, "vehicle": v["id"],
        "text": bundle(still(v, aspect, PARKING, PARKING_CAM), NEG_STILL,
                       RULES["anchor916" if aspect == "9:16" else "anchor169"]),
    }]
    for index, (code, label, leg) in enumerate(ORBIT_LEGS):
        out.append({
            "type": f"OBcar 影片・{aspect} {code} 360°環繞 {label}",
            "purpose": tag, "engine": vid_engine, "status": "prompt", "aspect": aspect, "vehicle": v["id"],
            "text": bundle(f"{ORBIT.format(leg=leg)}\n\n{clip_format(aspect)}", NEG_ORBIT,
                           RULES["orbit_first" if index == 0 else "orbit_next"]),
        })
    for key, label, cam, _ in COAST_SHOTS:
        out.append({
            "type": f"OBcar 圖・{aspect} R01{key} 海邊定格圖 {label}",
            "purpose": tag, "engine": img_engine, "status": "prompt", "aspect": aspect, "vehicle": v["id"],
            "text": bundle(still(v, aspect, COAST, cam), NEG_STILL, RULES["coast_still"]),
        })
    for key, label, _, move in COAST_SHOTS:
        out.append({
            "type": f"OBcar 影片・{aspect} R02{key} 海邊跟拍 {label}",
            "purpose": tag, "engine": vid_engine, "status": "prompt", "aspect": aspect, "vehicle": v["id"],
            "text": bundle(f"{COAST_CLIP.format(move=move)}\n\n{clip_format(aspect)}", NEG_COAST,
                           RULES["coast_clip"]),
        })
    return out


TASK_FIELDS = (
    "spec references anchor169 orbitClips169 orbitMaster169 coastStills169 coastClips169 coastMaster169 "
    "anchor916 orbitClips916 orbitMaster916 coastStills916 coastClips916 coastMaster916 finalQa"
).split()
DEFAULT_TASKS = {key: "todo" for key in TASK_FIELDS}

# 已知進度：Freed 三代規格鎖定、實車照齊、16:9 定錨 v2 已批准；其餘 ready 車款規格已鎖，等實車照。
TASK_OVERRIDES = {
    "13": {"spec": "done", "references": "done", "anchor169": "done", "orbitClips169": "doing"},
    "01": {"spec": "done"}, "03": {"spec": "done"}, "09": {"spec": "done"},
    "10": {"spec": "done"}, "12": {"spec": "done"},
}


def build():
    ready = [v for v in VEHICLES if v["ready"]]
    briefs = [{
        "date": "2026-08-01", "stream": "obcar",
        "title": f"{v['name']}｜16:9 主線＋9:16 衍生",
        "focus": "每比例 10 條｜A01 定錨 → 3 段接力 360° → 3 張海邊定格 → 3 段海邊跟拍",
        "meta": ("16:9 先做完並批准，9:16 再用批准的 16:9 當場景參考原生重生，兩個比例才會是同一個空間。"
                 f"車款鎖定：{v['note']}"),
        "summary": ("v2 三層 Prompt：車款交給實車照、場景交給批准的定錨圖、禁止項只在 negative 欄寫一次。"
                    "停車 360° 不再需要七角度圖——一張 A01 加三段接力，每段用上一段的尾幀，連續性由影片自己保證。"
                    "每條仍自帶 PROMPT／NEGATIVE／RULES，單獨複製即完整。"),
        "items": vehicle_items(v, "16:9") + vehicle_items(v, "9:16"),
    } for v in ready]

    tracker_vehicles = [{
        "id": v["id"], "name": v["name"], "seats": v["seats"], "note": v["note"],
        "tasks": TASK_OVERRIDES.get(v["id"], {}),
    } for v in VEHICLES]

    return {
        "updatedAt": "2026-08-01T21:00:00+09:00",
        "tracker": {"defaultTasks": DEFAULT_TASKS, "vehicles": tracker_vehicles},
        "briefs": briefs,
    }


def vehicle_sheet():
    """車款主檔的公開版本。VEHICLES 是唯一真相,這裡只是導出,避免兩份資料走鐘。"""
    return {
        "project": "OBcar Project",
        "updatedAt": build()["updatedAt"],
        "deliverablesPerVehicle": ["stationary_360_drone", "okinawa_coastal_driving_drone"],
        "assetsPerVehiclePerAspect": {"stills": 4, "clips": 6},
        "vehicles": [{
            "id": v["id"], "name": v["name"], "seats": v["seats"],
            "model": v["model"], "colour": v["colour"],
            "hasReferencePhotos": v["refs"], "promptsGenerated": v["ready"], "note": v["note"],
        } for v in VEHICLES],
    }


if __name__ == "__main__":
    data = build()
    target = ROOT / "data" / "obcar.json"
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sheet = ROOT / "projects" / "obcar" / "vehicles.json"
    sheet.write_text(json.dumps(vehicle_sheet(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    items = [i for b in data["briefs"] for i in b["items"]]
    print(f"wrote {target} + {sheet}: {len(data['briefs'])} 台車 / {len(items)} 條 Prompt / "
          f"{sum(len(i['text']) for i in items):,} 字")
