#!/usr/bin/env python3
"""Build one sellable Instagram carousel product per day.

Two phases, in this order:

  Phase 1 — 百搭 Kit. Five structure-first template families that work for any
  industry (list / before-after / steps / quote / myth-buster), each shipped in three
  colourways. Five days produces one complete kit that can go on sale without waiting
  for industry research.

  Phase 2 — 行業包. The nine visual template families applied to one buyer-oriented
  industry per day, so a brand is a day of work, not nine.

Each brief is one product: one text-free master plate per colourway, the split command,
per-card copy specs, and the Canva rebuild spec. The plate carries background only —
see CAROUSEL_V2_DESIGN.md for why text cannot survive being split out of a master.
"""
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompt_blocks import CARD_NEGATIVE, CARD_RULES, PLATE_NEGATIVE, PLATE_RULES, bundle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/carousel.json"

# 3:4 is the 2026 Instagram feed and profile-grid ratio: a cover no longer gets
# cropped in the grid. See CAROUSEL_RESEARCH.md — and warn buyers that the carousel
# uploader still defaults to 4:5.
CARD_WIDTH, CARD_HEIGHT = 1080, 1440
CARD_RATIO = "3:4"
SEAM_DANGER = 80

# 8–10 cards measurably outperforms shorter sets; engagement dips after card 3 and
# recovers past card 8. Six is reserved for structures that are genuinely short.
DEFAULT_CARDS = 9

UNIVERSAL_EPOCH = date(2026, 7, 26)
INDUSTRY_EPOCH = UNIVERSAL_EPOCH + timedelta(days=5)

COLOURWAYS = [
    ("warm-neutral", "warm cream paper, espresso brown, muted sage accent"),
    ("cool-editorial", "cool off-white, deep navy, soft slate blue accent"),
    ("soft-clay", "pale oat, terracotta clay, dusty rose accent"),
]

# Structure-first families. These sell because the structure is the product: a buyer
# in any industry drops their own words into the same skeleton.
UNIVERSAL_FAMILIES = [
    {
        "id": "list-stack",
        "name": "列表款",
        "cards": 9,
        "premise": "N 個重點／N 個常見錯誤",
        "system": "numbered stack layout, oversized numerals as the dominant graphic, one rule line per item, generous left margin",
        "plate": "a continuous vertical rule running the full height near the left third, crossed by evenly spaced horizontal hairlines, with a wide calm field to the right for numbering and text",
        "roles": [
            "封面｜大數字 + 一句 hook",
            "第 1 項｜編號 + 一句陳述",
            "第 2 項｜編號 + 一句陳述",
            "第 3 項｜編號 + 一句陳述",
            "第 4 項｜編號 + 一句陳述",
            "視覺停頓｜只有一句短句與大量留白",
            "第 5 項｜編號 + 一句陳述",
            "收束｜把五項收成一句可帶走的結論",
            "品牌 CTA｜Logo + 一個明確動作",
        ],
    },
    {
        "id": "before-after",
        "name": "前後對比款",
        "cards": 8,
        "premise": "before/after、錯 vs 對",
        "system": "split-field comparison, a hard vertical or diagonal divider, one muted side and one saturated side, matching label chips",
        "plate": "a single continuous diagonal division sweeping across the whole strip, muted tone above and saturated tone below, so each card inherits a different part of the same diagonal",
        "roles": [
            "封面｜對比承諾：從 A 到 B",
            "情境｜大多數人現在的做法",
            "問題｜這樣做會付出什麼代價",
            "轉折｜換一個做法",
            "對比一｜左錯右對，各一句",
            "對比二｜左錯右對，各一句",
            "證據｜一個具體結果或數字",
            "品牌 CTA｜Logo + 一個明確動作",
        ],
    },
    {
        "id": "step-path",
        "name": "教學步驟款",
        "cards": 9,
        "premise": "Step 1…N，最容易被存檔",
        "system": "progress-path layout, a connecting line threading step markers, one step per card, small progress indicator in a fixed corner",
        "plate": "one unbroken connecting path line travelling horizontally across the entire strip with evenly spaced node dots, so the path visibly continues from card to card when swiped",
        "roles": [
            "封面｜做完會得到什麼，需要多久",
            "準備｜開始前要有的三樣東西",
            "Step 1｜動作 + 一個判斷標準",
            "Step 2｜動作 + 一個判斷標準",
            "Step 3｜動作 + 一個判斷標準",
            "視覺停頓｜一句提醒，大量留白",
            "Step 4｜動作 + 一個判斷標準",
            "常見卡點｜最容易做錯的一步",
            "品牌 CTA｜Logo + 存檔提示",
        ],
    },
    {
        "id": "quote-anchor",
        "name": "金句款",
        "cards": 6,
        "premise": "引言 + 大字，最好做、存檔率高",
        "system": "typographic poster layout, one oversized statement per card, tiny supporting caption, one repeating quiet graphic mark",
        "plate": "a large soft tonal wash drifting slowly along the whole strip with one thin baseline rule near the lower third, giving each card a different region of the same gradient",
        "roles": [
            "封面｜最強的一句話，字級最大",
            "延伸｜為什麼這句成立",
            "反面｜不這樣做會怎樣",
            "具體｜一個可以照做的小動作",
            "共鳴｜一句短句，幾乎全留白",
            "品牌 CTA｜Logo + 分享提示",
        ],
    },
    {
        "id": "myth-buster",
        "name": "誤解破除款",
        "cards": 8,
        "premise": "先講迷思 → 逐張糾正，服務業最吃這款",
        "system": "claim-and-correction layout, struck-through myth chip above a clean correction block, consistent two-tone labelling",
        "plate": "two continuous horizontal bands of different tone running the full strip, the upper band slightly darker, so every card inherits the same myth-above / correction-below structure",
        "roles": [
            "封面｜點出一個大家都信的說法",
            "迷思一｜說法 + 為什麼不成立",
            "迷思二｜說法 + 為什麼不成立",
            "迷思三｜說法 + 為什麼不成立",
            "視覺停頓｜一句定調的短句",
            "正解｜正確的判斷方式",
            "適用條件｜什麼情況才成立，避免誇大",
            "品牌 CTA｜Logo + 一個明確動作",
        ],
    },
]

# Buyer-oriented: these are the people who actually pay for Instagram templates.
# The last three stay because SS has real material to make sample sets from.
INDUSTRIES = [
    "商業教練", "房地產仲介", "攝影師", "線上課程創作者", "營養師／健身教練",
    "婚禮策劃", "美業個人工作室", "寵物服務", "獨立咖啡店",
]

DAY_STYLES = [
    {
        "id": "quiet-arch-editorial",
        "name": "靜謐拱窗編輯誌",
        "system": "asymmetrical literary editorial pages, one tall arched photo window, generous cream negative space, fine serif rules and tiny botanical marks",
        "plate": "one continuous cream field with a repeating tall arch outline motif and a single fine vertical rule travelling the whole strip",
    },
    {
        "id": "menu-modular-grid",
        "name": "模組方格",
        "system": "bold modular menu grid, espresso color blocks, product cut-outs, price-tag-like labels and crisp sans-serif hierarchy",
        "plate": "an unbroken run of modular colour blocks in two alternating tones, with a thin label rail crossing the entire strip",
    },
    {
        "id": "field-notes",
        "name": "田野筆記",
        "system": "field-notebook education pages, ruled-paper cues, annotated diagrams, underlines, numbered callouts and restrained handwritten accents",
        "plate": "continuous ruled-paper lines across the whole strip with a faint margin rule and occasional hand-drawn arrow marks",
    },
    {
        "id": "opening-hour-documentary",
        "name": "紀實時間軸",
        "system": "documentary contact sheet, timestamp labels, cinematic still frames, film perforation details and chronological reading rhythm",
        "plate": "a continuous film perforation strip along the top and bottom edges with a timecode rail running the full width",
    },
    {
        "id": "mood-menu-bands",
        "name": "色帶選單",
        "system": "playful mood-selector system, vertical color bands, pill-shaped chips, small organic icons and soft color-coded cards",
        "plate": "a long sequence of slim vertical colour bands shifting hue gradually from one end of the strip to the other",
    },
    {
        "id": "space-guide-map",
        "name": "導覽地圖",
        "system": "architectural guide pages, simplified floor-plan lines, coordinate markers, framed views and zone labels",
        "plate": "one continuous simplified floor-plan line drawing extending across the entire strip with a dotted walking path",
    },
    {
        "id": "archive-scrapbook",
        "name": "品牌剪貼簿",
        "system": "warm archival scrapbook, layered torn paper, taped photographs, botanical pressings, date stamps and restrained handwritten notes",
        "plate": "a continuous torn-paper edge running horizontally across the strip with layered warm paper tones above and below",
    },
    {
        "id": "faq-conversation-cards",
        "name": "問答卡",
        "system": "structured question-and-answer interface, alternating speech cards, accordion tabs, clear icons and high-legibility sans typography",
        "plate": "an alternating rhythm of rounded card shapes in two tones marching along the whole strip, with a thin connecting baseline",
    },
    {
        "id": "campaign-poster",
        "name": "活動海報",
        "system": "confident campaign poster, full-bleed imagery, oversized condensed headline, date badge, offer block and strong action hierarchy",
        "plate": "one bold continuous colour field with a single oversized diagonal band sweeping the full length of the strip",
    },
]

INDUSTRY_ROLES = [
    "封面｜Hook：說出目標客戶心裡那句話",
    "情境｜建立他現在的處境",
    "解釋｜為什麼會這樣",
    "關鍵細節｜一個具體、可驗證的重點",
    "視覺停頓｜一句短句，大量留白",
    "比較｜兩個選擇的差別",
    "證明｜流程、案例或幕後，加上適用條件",
    "收束｜把整組收成一句結論",
    "品牌 CTA｜Logo + 一個明確動作",
]

INDUSTRY_TOPICS = [
    "品牌定位", "招牌服務", "知識教育", "幕後流程", "選擇指南",
    "使用情境", "品牌故事", "常見問題", "行動方案",
]


def plate_prompt(family, colour_id, palette, cards):
    """One text-free background strip that will be cut into `cards` cards."""
    strip_width = CARD_WIDTH * cards
    prompt = (
        f"Create ONE wide, seamless, TEXT-FREE background plate for an Instagram carousel. "
        f"It will be machine-split into {cards} separate {CARD_RATIO} cards of {CARD_WIDTH}×{CARD_HEIGHT} px, "
        f"so compose it as one continuous horizontal strip that reads left to right "
        f"(final strip size {strip_width}×{CARD_HEIGHT}). Output the widest aspect ratio this tool "
        "supports — 16:9 is fine; the strip is fitted afterwards. "
        f"TEMPLATE FAMILY {family['id']}｜{family['name']}. Design grammar: {family['system']}. "
        f"CONTINUOUS STRUCTURE — this is the whole point of the plate: {family['plate']}. "
        f"Colourway {colour_id}: {palette}. Add a soft paper texture and a barely-visible film grain. "
        f"Every {CARD_WIDTH} px along the strip is a cut line: keep the design either continuous across "
        f"those cuts or clear of them, and never place a self-contained motif so that it straddles one. "
        "Leave broad calm areas with no detail — headlines, body copy and logos are typeset in Canva on "
        "top of this plate, and they need somewhere quiet to land."
    )
    return bundle(prompt, PLATE_NEGATIVE, PLATE_RULES)


def split_command(source_name, cards):
    return (
        f"python3 scripts/split_carousel.py {source_name} --cards {cards}\n"
        f"→ 輸出 {cards} 張 {CARD_WIDTH}×{CARD_HEIGHT} 卡片 + `_seam_preview.png`。\n"
        f"先看 seam preview：紅帶是每個切點左右各 {SEAM_DANGER}px 的禁區，"
        "有裝飾或主體被切開就回頭改母圖，不要硬上。\n"
        "母圖是抽象紋理才用預設 `--fit stretch`；若母圖有拱門、照片框、物件等可辨識結構，"
        "改用 `--fit cover`（保幾何但裁掉大部分高度）。"
    )


def card_prompt(family, role, index, cards, context, colour_id, palette):
    """The per-card spec: what this card says and which roles it is allowed to show."""
    lead, body = role.split("｜", 1) if "｜" in role else ("", role)
    prompt = (
        f"Typeset card {index}/{cards} of one Instagram carousel set, {CARD_RATIO} at "
        f"{CARD_WIDTH}×{CARD_HEIGHT} px, edge to edge. Output ONE standalone card. "
        f"Context: {context}. TEMPLATE FAMILY {family['id']}｜{family['name']}; "
        f"design grammar: {family['system']}; colourway {colour_id}: {palette}. "
        f"This card's storytelling role is 「{lead or '內容'}」 and nothing else. "
        f"Copy to set (Traditional Chinese, Taiwan usage):\n{body}\n"
        f"Show only the copy roles this role needs. "
        + (
            "This is the cover: it must survive as a 160 px thumbnail, so one dominant line, "
            "and the logo may appear here. "
            if index == 1 else
            "Logo, CTA and hashtags belong on the cover and the final card — do not repeat them here. "
            if index < cards else
            "This is the closing card: logo, one clear CTA and the hashtag line all belong here. "
        )
        + f"Reserve {SEAM_DANGER} px of quiet space on the left and right edges: this card sits next to "
        "its siblings in a swipe, and anything touching the edge reads as sliced."
    )
    return bundle(prompt, CARD_NEGATIVE, CARD_RULES)


def canva_spec(family, cards, context):
    return (
        f"CANVA TEMPLATE SPEC｜{family['name']}（{family['id']}）｜{context}. "
        f"{CARD_WIDTH}×{CARD_HEIGHT} px、{cards} 個獨立頁面。設計語法：{family['system']}。"
        f"安全邊 80px，切點禁區左右各 {SEAM_DANGER}px。"
        "把分割出來的卡片當背景，文字全部用可編輯 Canva 文字重打，不要留任何燒進圖裡的字。"
        "圖層命名要讓買家看得懂：BACKGROUND / HEADLINE / BODY / LABEL / PHOTO FRAME / PAGE / LOGO / CTA。"
        "最多兩個字型家族、三個品牌色。"
        "⚠️ 字型只能用可外發的授權（Canva Pro 專屬字型不能用在要交付的模板）。"
        f"⚠️ 說明書要寫兩句：上傳時把比例從預設 4:5 改成 {CARD_RATIO}；"
        f"要縮成 6–8 張時，優先刪「視覺停頓」與最後一個並列項，永遠保留封面與 CTA。"
        "存成 master design，每次客製前先複製，最後產出 Brand Template 連結交付。"
    )


def universal_brief(day, family):
    cards = family["cards"]
    context = f"百搭 Kit｜{family['name']}（{family['premise']}）"
    items = [
        {
            "type": f"母圖・{colour_id}",
            "purpose": f"{cards} 張連續背景帶",
            "engine": "ChatGPT Images / Imagen",
            "status": "prompt",
            "text": plate_prompt(family, colour_id, palette, cards),
        }
        for colour_id, palette in COLOURWAYS
    ]
    items.append({
        "type": "分割指令",
        "purpose": f"母圖 → {cards} 張卡片",
        "engine": "split_carousel.py",
        "status": "tool",
        "text": split_command(f"{family['id']}_warm-neutral.png", cards),
    })
    items.extend({
        "type": f"圖卡文字・第 {index} 張",
        "purpose": family["name"],
        "engine": "Canva",
        "status": "prompt",
        "text": card_prompt(family, role, index, cards, context, *COLOURWAYS[0]),
    } for index, role in enumerate(family["roles"], 1))
    items.append({
        "type": "Canva 拆件規格",
        "purpose": f"可販售模板｜{family['name']}",
        "engine": "Canva Pro",
        "status": "prompt",
        "text": canva_spec(family, cards, context),
    })
    return {
        "date": day.isoformat(),
        "stream": "carousel",
        "title": f"IG 百搭 Kit｜{family['name']}｜{cards} 張 × 3 配色",
        "focus": family["premise"],
        "meta": f"百搭 {UNIVERSAL_FAMILIES.index(family) + 1}/5 套｜{cards} 張 {CARD_RATIO}｜3 配色",
        "summary": (
            f"「{family['name']}」是結構型模板，任何行業都能套。今天產出 3 張無文字母圖（一色一張）、"
            f"切成 {cards} 張 {CARD_WIDTH}×{CARD_HEIGHT}，再到 Canva 上字。"
            "五款做完就是一個可上架的 Kit，不必等行業研究。"
        ),
        "items": items,
    }


def industry_brief(day, industry_index, round_index):
    # One day is one finished product, so the industry advances daily. Each round of
    # nine covers every industry on one topic, and the visual family is offset by the
    # round so the same industry does not come back looking identical.
    industry = INDUSTRIES[industry_index % len(INDUSTRIES)]
    topic = INDUSTRY_TOPICS[round_index % len(INDUSTRY_TOPICS)]
    style = DAY_STYLES[(industry_index + round_index) % len(DAY_STYLES)]
    cards = DEFAULT_CARDS
    context = f"{industry}｜{topic}"
    items = [
        {
            "type": f"母圖・{colour_id}",
            "purpose": f"{cards} 張連續背景帶",
            "engine": "ChatGPT Images / Imagen",
            "status": "prompt",
            "text": plate_prompt(style, colour_id, palette, cards),
        }
        for colour_id, palette in COLOURWAYS[:1]
    ]
    items.append({
        "type": "分割指令",
        "purpose": f"母圖 → {cards} 張卡片",
        "engine": "split_carousel.py",
        "status": "tool",
        "text": split_command(f"{style['id']}_{industry}.png", cards),
    })
    items.extend({
        "type": f"圖卡文字・第 {index} 張",
        "purpose": context,
        "engine": "Canva",
        "status": "prompt",
        "text": card_prompt(style, role, index, cards, context, *COLOURWAYS[0]),
    } for index, role in enumerate(INDUSTRY_ROLES, 1))
    items.append({
        "type": "Canva 拆件規格",
        "purpose": f"可販售模板｜{industry}",
        "engine": "Canva Pro",
        "status": "prompt",
        "text": canva_spec(style, cards, context),
    })
    return {
        "date": day.isoformat(),
        "stream": "carousel",
        "title": f"IG 行業包｜{industry}｜{style['name']}",
        "focus": topic,
        "meta": f"第 {round_index + 1} 輪・{industry_index + 1}/9 家｜{cards} 張 {CARD_RATIO}",
        "summary": (
            f"買家導向行業「{industry}」，今天用「{style['name']}」這套設計語法做一組完整可賣的 {cards} 張。"
            "一天一個產品：母圖 → 分割 → Canva 上字，不再九天磨一個品牌。"
        ),
        "items": items,
    }


def make_brief(day):
    """Phase 1 is the universal kit; everything after that is industry packs."""
    if day < INDUSTRY_EPOCH:
        offset = max(0, (day - UNIVERSAL_EPOCH).days)
        return universal_brief(day, UNIVERSAL_FAMILIES[offset % len(UNIVERSAL_FAMILIES)])
    delta = (day - INDUSTRY_EPOCH).days
    return industry_brief(day, delta % len(INDUSTRIES), delta // len(INDUSTRIES))


def main():
    payload = json.loads(DATA.read_text())
    by_date = {brief["date"]: brief for brief in payload.get("briefs", [])}
    start = max(date.today(), UNIVERSAL_EPOCH)
    for offset in range(14):
        day = start + timedelta(days=offset)
        by_date[day.isoformat()] = make_brief(day)
    payload["briefs"] = sorted(by_date.values(), key=lambda item: item["date"])
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"Carousel queue ready: {start} → {start + timedelta(days=13)}")
    print(f"  百搭 Kit {UNIVERSAL_EPOCH} → {INDUSTRY_EPOCH - timedelta(days=1)}，之後進行業包")


if __name__ == "__main__":
    main()
