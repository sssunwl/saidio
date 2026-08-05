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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompt_blocks import blocks_for, bundle  # noqa: E402

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
    dict(id="02", name="Suzuki Hustler", seats="4", ready=True, refs=True,
         model="second-generation Suzuki Hustler kei crossover (MR52S/MR92S, 2020 onwards)",
         colour="white",
         body_note="Keep the exact square-bezel round headlamps, bold HUSTLER hood lettering, black wheel-arch cladding and roof rails shown in the photographs — the boxy retro-SUV face, not the rounder first-generation front.",
         note="影片實拍確認，車牌 35-15。全長3,395／全寬1,475／全高1,680／軸距2,460mm"),
    dict(id="03", name="Mitsubishi Delica Mini", seats="4", ready=True, refs=False,
         model="Mitsubishi Delica Mini kei tall wagon (B34A/B35A, 2023 onwards)",
         colour="",
         body_note="Keep the exact Delica Mini square face, stacked lamp units and black lower cladding shown in the photographs; it is not a Delica D:5 and not a Delica D:2.",
         note="按 4 座判定為 Delica Mini；若實際是 D:5／D:2 請改 model"),
    dict(id="04", name="Suzuki Jimny 660cc", seats="4", ready=True, refs=False,
         model="fourth-generation Suzuki Jimny kei off-roader (JB64W, 2018 onwards)",
         colour="",
         body_note="Keep the exact upright slotted grille, round headlamps, flat clamshell bonnet, square wheel arches and body-on-frame stance shown in the photographs. This is the narrow kei-class Jimny: plain arches, no flared over-fenders — that is the Sierra.",
         note="JB64W；2018 起只有這一個世代，與 05 的外觀差別只在葉子板寬度"),
    dict(id="05", name="Suzuki Jimny 1500cc", seats="4", ready=True, refs=False,
         model="fourth-generation Suzuki Jimny Sierra (JB74W, 2018 onwards, 1.5-litre)",
         colour="",
         body_note="Keep the exact black flared over-fenders, wider track and 15-inch wheels shown in the photographs. This is the wide-body Sierra, not the narrow kei Jimny.",
         note="JB74W；日規名稱是 Jimny Sierra，與 04 共用車體、差在寬葉子板"),
    dict(id="06", name="Suzuki Solio", seats="5", ready=True, refs=True,
         model="current-generation Suzuki Solio compact tall wagon (2020 onwards)",
         colour="white",
         body_note="Keep the exact chrome bar linking the swept headlamps, sliding rear doors and tall-wagon roofline shown in the photographs.",
         note="影片實拍確認，車牌 21-08。全長3,710／全寬1,625／全高1,745mm；精確底盤代號（暫定 MA36S／MA46S）待覆核，不影響開工"),
    dict(id="07", name="Toyota Sienta 二代", seats="5", ready=False, refs=False,
         model="", colour="", body_note="",
         note="NSP170G／NHP170G；拍照時答一題：前期（2015–2018，下擺黑色折線）還是後期（2018/9 起，保桿與頭燈改款）？"),
    dict(id="08", name="Honda Freed", seats="5", ready=False, refs=False,
         model="", colour="", body_note="",
         note="拍照時答一題：跟 13 一樣是三代（2024 起）還是二代 GB5／GB7（2016–2024）？若同為三代就跟 13 合併，不另開一台"),
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
    dict(id="11", name="Toyota Prius", seats="5", ready=True, refs=True,
         model="fifth-generation Toyota Prius (MXWH60, 2022 onwards, \"Hybrid Reborn\" design)",
         colour="white",
         body_note="Keep the exact extremely low coupe-like roofline, hidden rear door handle in the C-pillar, and split headlamp/DRL signature shown in the photographs — this is the 60-series, not the taller 50-series.",
         note="影片實拍確認，車牌 74-57。全長4,599／全寬1,782／全高1,420–1,435／軸距2,750mm，車高極低直接鎖定 60 系"),
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
    dict(id="14", name="Honda Stepwagon", seats="8", ready=True, refs=True,
         model="current-generation Honda Stepwagon Spada (RP6–RP8, 2022 onwards)",
         colour="dark blue",
         body_note="Keep the exact sharp split LED headlamp signature and black mesh lower grille of the Spada trim shown in the photographs, not the rounder pre-2022 face.",
         note="影片實拍確認（片內字卡即寫 Spada），車牌 37-72。全長4,800／全寬1,750／全高1,840／軸距2,890mm"),
    dict(id="15", name="Toyota Voxy 80系", seats="7", ready=True, refs=True,
         model="facelifted Toyota Voxy 80-series (ZRR80W/ZWR80W, 2017 onwards)",
         colour="dark navy",
         body_note="Keep the exact large vertical-slat chrome grille and blue-accented hybrid badge shown in the photographs — the post-2017 facelift face, not the plainer pre-2017 nose.",
         note="影片實拍確認，車牌 88-88（與 20 號車牌相同數字純屬巧合，非同一台）。全長4,695／全寬1,730／全高1,895／軸距2,850mm"),
    dict(id="16", name="Toyota Voxy 90系", seats="7–8", ready=True, refs=False,
         model="fourth-generation Toyota Voxy (R90 series, 2022 onwards)",
         colour="",
         body_note="Keep the exact full-width black grille that spans the whole nose, the slim horizontal headlamp signature, sliding-door layout and factory wheels shown in the photographs; do not draw the chrome-heavy 80-series face.",
         note="R90（ZWR90W／MZRA90W），2022/1 起，無前後期之分；7 或 8 座不影響外觀"),
    dict(id="17", name="Nissan Serena", seats="8", ready=True, refs=True,
         model="fourth-generation Nissan Serena (C28, 2022 onwards)",
         colour="white",
         body_note="Keep the exact V-Motion chrome grille and sharp T-shaped LED headlamp signature shown in the photographs — the C28 face, not the rounder C27.",
         note="影片實拍確認，車牌 77-1。全長4,765／全寬1,715／全高1,870／軸距2,870mm。"
              "⚠️ Toyota Noah 是本車款的後備代用車，不是官網另一個獨立車型，不要另開 OBcar 項目"),
    dict(id="18", name="Toyota Vellfire 20系", seats="7", ready=True, refs=True,
         model="first-generation Toyota Vellfire (ANH20W/GGH20W, 2008–2015)",
         colour="dark grey",
         body_note="Keep the exact three-slat chrome grille, twin projector headlamps and wood-trim dashboard shown in the photographs.",
         note="影片實拍確認，車牌 71-44。全長4,850／全寬1,830／全高1,890／軸距2,950mm；前期／後期改款細節兩者尺寸相同，以照片為準，不影響開工"),
    dict(id="19", name="Toyota Alphard 30系", seats="8", ready=True, refs=True,
         model="third-generation Toyota Alphard 30-series facelift, standard grade (AGH30W, 2018 onwards)",
         colour="gloss black",
         body_note="Standard-grade facelift face: plain body-colour bumper with no aero lip, exactly as photographed. This is a different physical car from 20 (SC aero, seven-seat) — do not swap their reference photos.",
         note="影片實拍確認：車牌 84-35，素色保桿無包邊，字卡寫「可容納7~8人」。與 20（車牌 88-88，SC 包邊）是不同的兩台實車"),
    dict(id="20", name="Toyota Alphard 30系", seats="7", ready=True, refs=True,
         model="third-generation Toyota Alphard 30-series facelift, seven-seat SC aero grade (AGH30W, 2018 onwards)",
         colour="gloss black",
         body_note="Facelift SC aero grade: keep the tall vertical-fin chrome grille running down into the bumper, and the chrome-edged aero lip around the front bumper and sills, exactly as photographed. Not the plain X or G bumper.",
         note="30系後期 SC（エアロボディ）＋包邊套件、7 座、黑色，車牌 88-88。影片自報規格：全長 4,945／全寬 1,850／全高 1,880–1,950／軸距 3,000mm"),
    dict(id="21", name="Toyota Alphard 40系", seats="7", ready=True, refs=True,
         model="fourth-generation Toyota Alphard (AH40 series, 2023 onwards)",
         colour="black",
         body_note="Keep the exact tall two-tier chrome mesh grille filling almost the whole nose, the slim upper lamp signature and squared shoulder line shown in the photographs. This is the 40-series: it does not have the 30-series single-tier stacked lamp cluster.",
         note="AH40（AGH40W），2023/6 起，無前後期之分。實拍照＋影片來自 footage/AL40，車牌 347 む77"),
    dict(id="22", name="Range Rover Evoque", seats="5", ready=True, refs=True,
         model="first-generation Range Rover Evoque (L538, 2011–2019)",
         colour="white",
         body_note="Keep the conventional protruding door handles and rounded wheel-arch shown in the photographs — this is the pre-facelift L538, not the later flush-handle L551.",
         note="影片自報尺寸全長4,365／軸距2,660mm，精確對應 L538 原廠數據（L551 是 4,371／2,681mm），且門把非隱藏式，判定為 L538"),
    dict(id="23", name="Porsche 718 Boxster", seats="2", ready=True, refs=True,
         model="Porsche 718 Boxster (982, 2016 onwards), soft top",
         colour="white with red leather interior",
         body_note="Soft-top convertible with the roof lowered, exactly as photographed — this is the Boxster, not the fixed-roof Cayman.",
         note="車尾徽標清楚寫「718」；全車照片皆敞篷、酒紅內裝。素材：final/OB_Porsche718_202606.mp4"),
    # 官網車隊表是 25 車型，主檔原本只有 23 —— 這兩台是漏的。
    dict(id="24", name="Honda N-One", seats="4", ready=True, refs=True,
         model="Honda N-One kei car, round headlamps with a two-tone black roof",
         colour="white with black roof",
         body_note="Keep the exact round headlamp shape, centred grille badge and black roof shown in the photographs.",
         note="影片來源：footage/1）介紹輕車三兄弟/None（白）。SS：N-One 產出優先度低，先做圖不急著做影片"),
    dict(id="25", name="Honda N-BOX", seats="4", ready=True, refs=True,
         model="Honda N-BOX kei tall wagon, standard (non-Custom) grade",
         colour="white",
         body_note="Keep the exact slim single-bar chrome grille and headlamp shape shown in the photographs; this is the standard grade, not the chrome-heavy Custom front end.",
         note="影片自報尺寸：全長3,395／全寬1,475／全高1,790／軸距2,520mm。SS：N-BOX 產出優先度低，先做圖不急著做影片。另有三兄弟版重複素材（不同色），以此為準"),
]


# ── Layer 1：CAR CARD（每條 Prompt 的開頭）──────────────────
# 車上不放人,但空駕駛座在近景會很怪。真實車廣的做法是讓玻璃反射天空——
# 玻璃讀起來是「反光」而不是「透明」,就沒有人該不該在裡面的問題。
GLASS = ("Glass: windscreen and front side windows carry a bright reflection of sky and coastline "
         "so the cabin is not legible; factory privacy glass behind the B-pillar. No occupant visible.")


def car_card(v):
    colour = f", in {v['colour']} paint" if v["colour"] else ", in its exact photographed colour"
    note = f" {v['body_note']}" if v["body_note"] else ""
    return (
        f"CAR: the exact vehicle in the uploaded photographs — {v['model']}{colour}.\n"
        "The photographs override all model knowledge and all general knowledge of this "
        "nameplate. Keep its exact face, lights, grille, wheels, badges, ride height, body "
        f"length and door layout. Do not restyle it and do not upgrade the trim level.{note}\n"
        f"{GLASS}"
    )


# ── Layer 2：場景 ───────────────────────────────────────────
# 背景太乾淨會露餡。真實照片的線索是：遠景有空氣霧、植被雜、水泥柏油有風化、
# 全場只有一個太陽方向。這段兩個場景共用。
REALISM = ("Photographic realism: atmospheric haze softens the far headland, foliage varies in "
           "species and tone, concrete and asphalt carry real weathering and repair marks, and a "
           "single consistent sun direction lights everything.")

PARKING = """Photoreal Japanese automotive advertising photograph.

The car is parked, engine off, centred in ONE marked bay of a quiet seaside public parking area in northern Okinawa: clean asphalt, two straight white bay lines, a low concrete seawall, calm blue-green sea, curved coastline, green subtropical hills, bright natural afternoon sun.

Parking geometry: the car's long axis is parallel to both bay lines, all four tyres sit well inside them, no white line runs under the body or bumpers, and the front wheels point straight ahead. Nothing else stands near the car — no wheel stop, no pole, no bollard, no people, no other vehicle."""

PARKING = f"{PARKING}\n\n{REALISM}"

PARKING_CAM = ("front-left three-quarter, about 35 degrees left of the nose, 1.1 metres high, "
               "50–65mm equivalent. Whole car, all four tyres and its attached shadow visible, "
               "car about 50 percent of frame width, level horizon.")

COAST = """Photoreal automotive advertising drone photograph.

The car drives along a coastal road in northern Okinawa — left-hand traffic, in the correct lane. Blue-green sea and a low seawall on one side, green subtropical hills on the other, clean Japanese asphalt, correct white road markings, bright afternoon light, sparse distant traffic."""

COAST = f"{COAST}\n\n{REALISM}"

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

The car itself is one unchanging physical object for the whole clip — same body, same badges, same silhouette. It is never redrawn, replaced or shown from an impossible opposite angle partway through the move; whichever side is currently facing camera stays the only side visible, changing gradually and only as far as the camera's own travel explains.

Photoreal Japanese car commercial, gimbal-smooth, one continuous direction, no zoom. Keep the camera moving through the last frame so the next clip can continue from it."""

ORBIT_LEGS = [
    ("P1", "前左→正左", "travelling from the front-left three-quarter round to the full left side"),
    ("P2", "正左→正後", "continuing that same leftward travel from the full left side round to the centred rear"),
    ("P3", "正後→前右", "continuing that same travel from the centred rear round the right side to the front-right three-quarter"),
]

COAST_CLIP = """Animate this photograph. The car drives forward at a steady safe speed in the same lane: wheels rolling at the correct speed, tyres attached to the road, subtle suspension movement, body following the curve of the road.

The drone keeps this photograph's framing and tracks the car through real space. Coastline, road markings and roadside poles pass naturally through frame. {move}

Whichever end of the car faces camera in the uploaded photograph — nose or tail — keeps facing camera for the whole clip. The drone stays on that side and never overtakes the car, cuts across it, or circles round to show the opposite end. Keep the cabin glass reflective and unoccupied exactly as the photograph has it.

Photoreal Japanese automotive and travel commercial, gimbal-smooth, no zoom."""

# Negative 與 RULES 已搬進 scripts/prompt_blocks.py（OBCAR_* 區塊），由鏡頭代碼查表。
# 改規則只改那裡，backfill 與這支生成器才不會各寫一份、慢慢走鐘。


def still(v, aspect, scene, cam):
    body = VERTICAL_FROM_LANDSCAPE.format(cam=cam) if aspect == "9:16" else LANDSCAPE_STILL.format(cam=cam)
    return f"{car_card(v)}\n\n{scene}\n\n{body}"


def clip_format(aspect):
    return VERTICAL_CLIP if aspect == "9:16" else LANDSCAPE_CLIP


def item(v, aspect, item_type, engine, prompt):
    """一條 Prompt。negative 與 rules 一律由 type 裡的鏡頭代碼查 prompt_blocks 決定。"""
    pair = blocks_for("obcar", item_type)
    if pair is None:
        raise ValueError(f"prompt_blocks 沒有這個鏡頭代碼的規則：{item_type}")
    return {
        "type": item_type,
        "purpose": f"{v['name']}｜{v['seats']}座" + ("" if v["refs"] else "｜⚠️ 實車照未到"),
        "engine": engine, "status": "prompt", "aspect": aspect, "vehicle": v["id"],
        "text": bundle(prompt, *pair),
    }


def vehicle_items(v, aspect):
    """一台車、一個比例＝10 條 Prompt。"""
    img_engine, vid_engine = "ChatGPT Images", "Google Flow Lite"
    out = [item(v, aspect, f"OBcar 圖・{aspect} A01 停車場定錨圖", img_engine,
                still(v, aspect, PARKING, PARKING_CAM))]
    for code, label, leg in ORBIT_LEGS:
        out.append(item(v, aspect, f"OBcar 影片・{aspect} {code} 360°環繞 {label}", vid_engine,
                        f"{ORBIT.format(leg=leg)}\n\n{clip_format(aspect)}"))
    for key, label, cam, _ in COAST_SHOTS:
        out.append(item(v, aspect, f"OBcar 圖・{aspect} R01{key} 海邊定格圖 {label}", img_engine,
                        still(v, aspect, COAST, cam)))
    for key, label, _, move in COAST_SHOTS:
        out.append(item(v, aspect, f"OBcar 影片・{aspect} R02{key} 海邊跟拍 {label}", vid_engine,
                        f"{COAST_CLIP.format(move=move)}\n\n{clip_format(aspect)}"))
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
    # 2026-08-01 補鎖：主推五款到齊。這四台的世代由車名本身唯一指定，沒有前後期歧義，
    # 所以不必等實車照就能鎖 spec —— 但實車照仍是車款身分的唯一真相，拍到才能開生成。
    "04": {"spec": "done"}, "05": {"spec": "done"},
    "16": {"spec": "done"}, "21": {"spec": "done"},
    # 2026-08-02：Okiblues 車隊實拍影片（小林影片/、footage/AL40、footage/輕車三兄弟）
    # 抽幀比對後鎖定的七台，references 也一併標 done，因為抽出來的幀就是實車照。
    "19": {"spec": "done", "references": "done"},
    "20": {"spec": "done", "references": "done"},
    "22": {"spec": "done", "references": "done"},
    "23": {"spec": "done", "references": "done"},
    "24": {"spec": "done", "references": "done"},
    "25": {"spec": "done", "references": "done"},
    "02": {"spec": "done", "references": "done"},
    "06": {"spec": "done", "references": "done"},
    "11": {"spec": "done", "references": "done"},
    "14": {"spec": "done", "references": "done"},
    "15": {"spec": "done", "references": "done"},
    "17": {"spec": "done", "references": "done"},
    "18": {"spec": "done", "references": "done"},
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
