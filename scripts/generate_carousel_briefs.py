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
from prompt_blocks import (  # noqa: E402
    CARD_NEGATIVE, CARD_RULES, PLATE_NEGATIVE, PLATE_RULES, SEGMENT_PLATE_RULES, bundle,
)

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

# 行業包先跑:買家(教練/房仲/攝影師…)是真的會掏錢的人,百搭 Kit 排在後面補齊。
# 一個 14 天循環 = 9 天九個行業 + 5 天五款百搭結構。
EPOCH = date(2026, 7, 26)
CYCLE_DAYS = 14
INDUSTRY_EPOCH = EPOCH
UNIVERSAL_EPOCH = EPOCH + timedelta(days=9)

# ── 四個獨立的變化維度 ───────────────────────────────────────────────
# 每天的樣子 = 視覺語法 × 配色 × 字型配對 × 表面質感 × 故事結構。
# 各維度用互質的步長輪替(見 pick()),所以同一個組合 1,260 天內不會重複出現。
COLOURWAYS = [
    ("warm-neutral", "warm cream paper, espresso brown, muted sage accent"),
    ("cool-editorial", "cool off-white, deep navy, soft slate blue accent"),
    ("soft-clay", "pale oat, terracotta clay, dusty rose accent"),
    ("ink-and-butter", "soft butter yellow, near-black ink, warm grey accent"),
    ("sea-glass", "chalk white, deep teal, pale seafoam accent"),
    ("plum-paper", "warm grey paper, deep plum, muted apricot accent"),
    ("forest-linen", "natural linen, deep forest green, pale gold accent"),
    ("graphite-coral", "light graphite grey, off-black, warm coral accent"),
    ("dusk-lilac", "soft lilac grey, aubergine, pale peach accent"),
    ("sand-cobalt", "warm sand, strong cobalt blue, chalk white accent"),
]

SURFACES = [
    ("uncoated-paper", "matte uncoated paper grain with a barely-visible film grain"),
    ("smooth-matte", "a smooth matte finish with no visible texture and very clean edges"),
    ("laid-textile", "a fine woven textile weave under softly diffused light"),
    ("recycled-fleck", "recycled stock with tiny darker flecks and slightly irregular edges"),
    ("soft-glaze", "a soft glazed sheen with gentle highlight falloff and no harsh reflection"),
]

# 字型配對只影響「圖卡文字」那一層(母圖永遠無字),但它是同一張版面看起來完全不同的最大變因。
TYPE_PAIRINGS = [
    ("serif-led", "a high-contrast Traditional-Chinese serif for headlines with a quiet grotesk for body"),
    ("grotesk-led", "a bold neo-grotesk for headlines with a lighter weight of the same family for body"),
    ("condensed-impact", "a tall condensed sans for headlines with a wide-set body face"),
    ("mono-accent", "a clean sans for headlines with a monospace face for labels, numbers and captions"),
    ("rounded-warm", "one soft rounded sans throughout, with weight contrast doing all the hierarchy work"),
    ("editorial-mix", "a display serif headline, a grotesk body, and small-caps labels"),
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

# 故事結構 = 這組怎麼講。與「視覺語法」正交:同一個結構套不同視覺會是完全不同的產品。
EXTRA_STRUCTURES = [
    {
        "id": "faq-concerns",
        "name": "客戶疑慮款",
        "cards": 7,
        "premise": "把成交前最擋路的問題一張一張拆掉",
        "roles": [
            "封面｜點名一個大家不好意思問的問題",
            "疑慮一｜問題 + 直球回答",
            "疑慮二｜問題 + 直球回答",
            "疑慮三｜問題 + 直球回答",
            "透明度｜明講什麼情況下不適合找你",
            "下一步｜合作或諮詢的流程長什麼樣",
            "品牌 CTA｜Logo + 一個明確動作",
        ],
    },
    {
        "id": "case-teardown",
        "name": "案例拆解款",
        "cards": 9,
        "premise": "一個真實案例，從起點拆到結果",
        "roles": [
            "封面｜結果先講，一個具體的變化",
            "起點｜客戶原本卡在哪裡",
            "診斷｜真正的問題不是他以為的那個",
            "做法一｜第一個關鍵動作",
            "做法二｜第二個關鍵動作",
            "視覺停頓｜一句話點出轉折",
            "結果｜可驗證的數字或前後對照",
            "適用條件｜什麼情況才複製得動，避免誇大",
            "品牌 CTA｜Logo + 一個明確動作",
        ],
    },
]

VISUAL_FAMILIES = [
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
    {
        "id": "swiss-grid",
        "name": "瑞士方格",
        "system": "strict international-style grid, flush-left hierarchy, thick horizontal rules, one solid accent block per page, mathematical spacing",
        "plate": "a continuous set of thick horizontal rules at fixed intervals with one solid accent band running the entire length at a constant height",
    },
    {
        "id": "riso-overprint",
        "name": "孔版疊印",
        "system": "two-ink risograph overprint, visible halftone dots, deliberate slight misregistration, paper white showing through, flat shapes",
        "plate": "two large overlapping ink fields travelling the whole strip with a halftone dot gradient in the overlap and a constant 2 mm misregistration offset",
    },
    {
        "id": "deco-frame",
        "name": "裝飾線框",
        "system": "art-deco geometry, stepped corner frames, thin repeated rules, symmetrical composition, small fan and sunburst motifs",
        "plate": "one continuous stepped border rule running along the top and bottom of the strip with evenly repeating thin vertical fluting between",
    },
    {
        "id": "gallery-label",
        "name": "展間掛牌",
        "system": "museum wall labels, very generous white space, hairline picture frames, small caption plates, centred restraint",
        "plate": "a long uninterrupted pale wall field with one hairline horizontal hanging rail crossing the entire strip at eye level",
    },
    {
        "id": "soft-gradient-panels",
        "name": "柔霧漸層",
        "system": "soft mesh-gradient fields with no hard edges, frosted translucent panels, gentle inner glow, rounded corners",
        "plate": "one slow continuous mesh gradient drifting through the palette from one end of the strip to the other, with no discrete shapes at all",
    },
    {
        "id": "paper-collage",
        "name": "紙膠拼貼",
        "system": "cut-paper collage, torn and scissor-cut edges, washi tape strips, layered shapes with soft contact shadow",
        "plate": "a continuous band of overlapping torn paper layers marching across the strip, with tape strips crossing at irregular intervals",
    },
    {
        "id": "mono-datasheet",
        "name": "等寬資料頁",
        "system": "monospace technical data sheet, thin keylines, small-caps field labels, tabular rhythm, one highlighted row",
        "plate": "a continuous fine keyline table grid running the full width with one tinted row band travelling the entire strip",
    },
    {
        "id": "broadsheet-column",
        "name": "報紙專欄",
        "system": "newspaper broadsheet columns, hairline column rules, drop caps, dense masthead-style headline stack, small photo boxes",
        "plate": "unbroken vertical column rules at even spacing across the whole strip with one heavier masthead rule near the top",
    },
    {
        "id": "ticket-stub",
        "name": "票券票根",
        "system": "ticket and boarding-pass motif, perforation dashes, stamped seals, serial numbers, tear-off end panel",
        "plate": "a continuous perforation dash line running horizontally through the strip with a repeating ticket-edge scallop along the bottom",
    },
    {
        "id": "botanical-letterpress",
        "name": "植物凸版",
        "system": "letterpress impression on heavy stock, botanical line engravings, deep debossed rules, ivory paper, restrained ornament",
        "plate": "one continuous debossed baseline rule across the strip with sparse engraved botanical stems rising at irregular intervals",
    },
    {
        "id": "luminous-nightcard",
        "name": "夜光卡",
        "system": "deep tinted ground with one luminous accent line drawn from the palette, soft glow falloff, high-contrast type wells, minimal ornament",
        "plate": "a deep tinted field with a single luminous accent line travelling the entire length of the strip, glowing softly and never breaking",
    },
]

# 結構型的五款本身就是完整的故事節奏,行業包直接借用,再加兩款服務業特別吃的。
STORY_STRUCTURES = [
    {k: family[k] for k in ("id", "name", "cards", "premise", "roles")}
    for family in UNIVERSAL_FAMILIES
] + EXTRA_STRUCTURES

INDUSTRY_TOPICS = [
    "品牌定位", "招牌服務", "知識教育", "幕後流程", "選擇指南",
    "使用情境", "品牌故事", "常見問題", "行動方案",
]


def pick(table, day_index, stride):
    """Rotate a dimension with a stride co-prime to its length.

    Each dimension advances at a different rate, so the full combination
    (visual × colour × type × surface × structure) does not repeat for years.
    """
    return table[(day_index * stride) % len(table)]


def plate_prompt(family, colour_id, palette, cards, surface=SURFACES[0]):
    """One text-free background strip that will be cut into `cards` cards."""
    strip_width = CARD_WIDTH * cards
    surface_id, surface_desc = surface
    prompt = (
        f"Create ONE wide, seamless, TEXT-FREE background plate for an Instagram carousel. "
        f"It will be machine-split into {cards} separate {CARD_RATIO} cards of {CARD_WIDTH}×{CARD_HEIGHT} px, "
        f"so compose it as one continuous horizontal strip that reads left to right "
        f"(final strip size {strip_width}×{CARD_HEIGHT}). Output the widest aspect ratio this tool "
        "supports — 16:9 is fine; the strip is fitted afterwards. "
        f"TEMPLATE FAMILY {family['id']}｜{family['name']}. Design grammar: {family['system']}. "
        f"CONTINUOUS STRUCTURE — this is the whole point of the plate: {family['plate']}. "
        f"Colourway {colour_id}: {palette}. Surface {surface_id}: {surface_desc}. "
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


SEGMENT_SIZE = 3  # cards per segment — matches most image models' native ~2.25:1 output


def segment_plate_prompt(family, colour_id, palette, cards, segment_index, segment_count,
                          surface=SURFACES[0]):
    """One text-free plate covering SEGMENT_SIZE cards, not the whole set.

    Why this exists: a 9-card strip is 6.75:1, but an image model gives roughly 2.25:1 — a
    5.17× horizontal stretch against only 1.72× vertical. That mismatch is what squashes arches
    and other round motifs sideways, on top of the blur that any 5× upscale causes. A 3-card
    segment's target ratio (2.25:1) lands close to what the model already outputs natively, so
    the stretch is close to uniform in both directions and only ~1.7× — no squash, less blur.

    Segments are generated independently (three separate calls to the image tool) and never
    share pixels at the join, so the prompt leans hard on "no directional gradient" (rule 5 in
    SEGMENT_PLATE_RULES) rather than on matching anything across calls.
    """
    strip_width = CARD_WIDTH * SEGMENT_SIZE
    surface_id, surface_desc = surface
    first_card = segment_index * SEGMENT_SIZE + 1
    last_card = min(cards, (segment_index + 1) * SEGMENT_SIZE)
    prompt = (
        f"Create ONE wide, seamless, TEXT-FREE background plate — segment {segment_index + 1} of "
        f"{segment_count} in a {cards}-card Instagram carousel set. This segment alone will be "
        f"machine-split into {SEGMENT_SIZE} separate {CARD_RATIO} cards of {CARD_WIDTH}×{CARD_HEIGHT} px "
        f"(cards {first_card}–{last_card} of the full set), so compose it as one continuous horizontal "
        f"strip that reads left to right (this segment's strip size {strip_width}×{CARD_HEIGHT}). "
        "Output the widest aspect ratio this tool supports; the strip is fitted afterwards. "
        f"TEMPLATE FAMILY {family['id']}｜{family['name']}. Design grammar: {family['system']}. "
        f"CONTINUOUS STRUCTURE — this is the whole point of the plate: {family['plate']}. "
        f"Colourway {colour_id}: {palette}. Surface {surface_id}: {surface_desc}. "
        f"Every {CARD_WIDTH} px along the strip is a cut line: keep the design either continuous across "
        f"those cuts or clear of them, and never place a self-contained motif so that it straddles one. "
        "Leave broad calm areas with no detail — headlines, body copy and logos are typeset in Canva on "
        "top of this plate, and they need somewhere quiet to land."
    )
    return bundle(prompt, PLATE_NEGATIVE, SEGMENT_PLATE_RULES)


def segment_split_command(source_names, cards):
    lines = [f"# {SEGMENT_SIZE} 段各自獨立生成、各自獨立切,不要先拼接再切"]
    for i, name in enumerate(source_names):
        first = i * SEGMENT_SIZE + 1
        last = min(cards, (i + 1) * SEGMENT_SIZE)
        lines.append(
            f"python3 scripts/split_carousel.py {name} --cards {SEGMENT_SIZE} "
            f"--out seg{i + 1}_cards/   # → 這段輸出的 01/02/03 就是卡 {first}/{first+1}/{last}"
        )
    lines.append(
        f"先看每段自己的 seam preview：紅帶是每個切點左右各 {SEAM_DANGER}px 的禁區。"
        "母圖是抽象紋理才用預設 `--fit stretch`；若有拱門、照片框等可辨識結構，改用 `--fit cover`。"
    )
    return "\n".join(lines)


def card_prompt(family, role, index, cards, context, colour_id, palette, typeset=TYPE_PAIRINGS[0]):
    """The per-card spec: what this card says and which roles it is allowed to show."""
    lead, body = role.split("｜", 1) if "｜" in role else ("", role)
    type_id, type_desc = typeset
    prompt = (
        f"Typeset card {index}/{cards} of one Instagram carousel set, {CARD_RATIO} at "
        f"{CARD_WIDTH}×{CARD_HEIGHT} px, edge to edge. Output ONE standalone card. "
        f"Context: {context}. TEMPLATE FAMILY {family['id']}｜{family['name']}; "
        f"design grammar: {family['system']}; colourway {colour_id}: {palette}; "
        f"type pairing {type_id}: {type_desc}. "
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


def canva_spec(family, cards, context, typeset=TYPE_PAIRINGS[0]):
    return (
        f"CANVA TEMPLATE SPEC｜{family['name']}（{family['id']}）｜{context}. "
        f"{CARD_WIDTH}×{CARD_HEIGHT} px、{cards} 個獨立頁面。設計語法：{family['system']}。"
        f"字型配對 {typeset[0]}：{typeset[1]}。"
        f"安全邊 80px，切點禁區左右各 {SEAM_DANGER}px。"
        "把分割出來的卡片當背景，文字全部用可編輯 Canva 文字重打，不要留任何燒進圖裡的字。"
        "圖層命名要讓買家看得懂：BACKGROUND / HEADLINE / BODY / LABEL / PHOTO FRAME / PAGE / LOGO / CTA。"
        "最多兩個字型家族、三個品牌色。"
        "⚠️ 字型只能用可外發的授權（Canva Pro 專屬字型不能用在要交付的模板）。"
        f"⚠️ 說明書要寫兩句：上傳時把比例從預設 4:5 改成 {CARD_RATIO}；"
        f"要縮成 6–8 張時，優先刪「視覺停頓」與最後一個並列項，永遠保留封面與 CTA。"
        "存成 master design，每次客製前先複製，最後產出 Brand Template 連結交付。"
    )


def universal_brief(day, family, day_index=0):
    cards = family["cards"]
    context = f"百搭 Kit｜{family['name']}（{family['premise']}）"
    # 一款百搭出三個配色 = 三個變體。配色本身也隨輪次前進,第二輪的列表款不會跟第一輪同色。
    palette_set = [pick(COLOURWAYS, day_index * 3 + slot * 3, 1) for slot in range(3)]
    typeset = pick(TYPE_PAIRINGS, day_index, 5)
    surface = pick(SURFACES, day_index, 2)
    items = [
        {
            "type": f"母圖・{colour_id}",
            "purpose": f"{cards} 張連續背景帶",
            "engine": "ChatGPT Images / Imagen",
            "status": "prompt",
            "text": plate_prompt(family, colour_id, palette, cards, surface),
        }
        for colour_id, palette in palette_set
    ]
    items.append({
        "type": "分割指令",
        "purpose": f"母圖 → {cards} 張卡片",
        "engine": "split_carousel.py",
        "status": "tool",
        "text": split_command(f"{family['id']}_{palette_set[0][0]}.png", cards),
    })
    items.extend({
        "type": f"圖卡文字・第 {index} 張",
        "purpose": family["name"],
        "engine": "Canva",
        "status": "prompt",
        "text": card_prompt(family, role, index, cards, context, *palette_set[0], typeset),
    } for index, role in enumerate(family["roles"], 1))
    items.append({
        "type": "Canva 拆件規格",
        "purpose": f"可販售模板｜{family['name']}",
        "engine": "Canva Pro",
        "status": "prompt",
        "text": canva_spec(family, cards, context, typeset),
    })
    return {
        "date": day.isoformat(),
        "stream": "carousel",
        "title": f"IG 百搭 Kit｜{family['name']}｜{cards} 張 × 3 配色",
        "focus": family["premise"],
        "meta": (
            f"百搭 {UNIVERSAL_FAMILIES.index(family) + 1}/5 套｜{cards} 張 {CARD_RATIO}｜"
            f"{'／'.join(c for c, _ in palette_set)} · {typeset[0]}"
        ),
        "summary": (
            f"「{family['name']}」是結構型模板，任何行業都能套。今天產出 3 張無文字母圖（一色一張）、"
            f"切成 {cards} 張 {CARD_WIDTH}×{CARD_HEIGHT}，再到 Canva 上字。"
            "五款做完就是一個可上架的 Kit，不必等行業研究。"
        ),
        "items": items,
    }


def industry_brief(day, day_index, industry_index, round_index):
    # One day is one finished product. Five dimensions rotate at co-prime rates, so
    # the same industry never comes back wearing the same visual, palette, type
    # pairing, surface or story rhythm — that is the whole point of the rewrite.
    industry = INDUSTRIES[industry_index % len(INDUSTRIES)]
    topic = INDUSTRY_TOPICS[round_index % len(INDUSTRY_TOPICS)]
    visual = pick(VISUAL_FAMILIES, day_index, 1)
    colour_id, palette = pick(COLOURWAYS, day_index, 3)
    typeset = pick(TYPE_PAIRINGS, day_index, 5)
    surface = pick(SURFACES, day_index, 2)
    # 7 種結構會被 14 天的循環整除,單用 day_index 會讓同一個行業每輪都拿到同一個結構。
    # 加上 round_index 打散這個共振。
    structure = pick(STORY_STRUCTURES, day_index + round_index, 3)
    cards = structure["cards"]
    # The plate prompt wants a visual grammar; the card prompts want that same grammar
    # plus the story role. Composing them here keeps both prompt builders untouched.
    look = {
        "id": f"{visual['id']}+{structure['id']}",
        "name": f"{visual['name']}・{structure['name']}",
        "system": visual["system"],
        "plate": visual["plate"],
    }
    context = f"{industry}｜{topic}｜{structure['premise']}"
    items = [{
        "type": f"母圖・{colour_id}",
        "purpose": f"{cards} 張連續背景帶",
        "engine": "ChatGPT Images / Imagen",
        "status": "prompt",
        "text": plate_prompt(look, colour_id, palette, cards, surface),
    }]
    items.append({
        "type": "分割指令",
        "purpose": f"母圖 → {cards} 張卡片",
        "engine": "split_carousel.py",
        "status": "tool",
        "text": split_command(f"{visual['id']}_{structure['id']}_{colour_id}.png", cards),
    })
    items.extend({
        "type": f"圖卡文字・第 {index} 張",
        "purpose": context,
        "engine": "Canva",
        "status": "prompt",
        "text": card_prompt(look, role, index, cards, context, colour_id, palette, typeset),
    } for index, role in enumerate(structure["roles"], 1))
    items.append({
        "type": "Canva 拆件規格",
        "purpose": f"可販售模板｜{industry}",
        "engine": "Canva Pro",
        "status": "prompt",
        "text": canva_spec(look, cards, context, typeset),
    })
    return {
        "date": day.isoformat(),
        "stream": "carousel",
        "title": f"IG 行業包｜{industry}｜{structure['name']}×{visual['name']}",
        "focus": topic,
        "meta": (
            f"第 {round_index + 1} 輪・{industry_index + 1}/{len(INDUSTRIES)} 家｜"
            f"{cards} 張 {CARD_RATIO}｜{colour_id} · {typeset[0]} · {surface[0]}"
        ),
        "summary": (
            f"買家導向行業「{industry}」。今天的組合是「{structure['name']}」的故事節奏 × "
            f"「{visual['name']}」的視覺語法 × {colour_id} 配色 × {typeset[0]} 字型配對。"
            f"一天一個產品：{cards} 張母圖 → 分割 → Canva 上字。"
        ),
        "items": items,
    }


def make_brief(day):
    """行業包先跑九天(九個買家行業),再用五天補齊百搭 Kit,十四天一循環。"""
    delta = max(0, (day - EPOCH).days)
    position = delta % CYCLE_DAYS
    round_index = delta // CYCLE_DAYS
    if position < len(INDUSTRIES):
        return industry_brief(day, delta, position, round_index)
    family = UNIVERSAL_FAMILIES[(position - len(INDUSTRIES)) % len(UNIVERSAL_FAMILIES)]
    return universal_brief(day, family, delta)


def main():
    payload = json.loads(DATA.read_text())
    by_date = {brief["date"]: brief for brief in payload.get("briefs", [])}
    start = max(date.today(), EPOCH)
    for offset in range(14):
        day = start + timedelta(days=offset)
        by_date[day.isoformat()] = make_brief(day)
    payload["briefs"] = sorted(by_date.values(), key=lambda item: item["date"])
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"Carousel queue ready: {start} → {start + timedelta(days=13)}")
    print(f"  {CYCLE_DAYS} 天一循環：{len(INDUSTRIES)} 天行業包 → 5 天百搭 Kit")
    print(f"  組合維度：{len(VISUAL_FAMILIES)} 視覺 × {len(COLOURWAYS)} 配色 × "
          f"{len(TYPE_PAIRINGS)} 字型 × {len(SURFACES)} 質感 × {len(STORY_STRUCTURES)} 結構")


if __name__ == "__main__":
    main()
