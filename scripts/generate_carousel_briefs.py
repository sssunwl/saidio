#!/usr/bin/env python3
"""Create one nine-day, one-industry Instagram carousel product cycle."""
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/carousel.json"
EPOCH = date(2026, 7, 23)
LOCKED_DATES = {"2026-07-23", "2026-07-24"}

INDUSTRIES = [
    "獨立咖啡店", "保養品牌", "房地產顧問", "健身教練", "旅行社",
    "牙科診所", "餐廳", "美髮沙龍", "寵物服務",
]

CAFE_DAYS = [
    (
        "品牌初識｜為什麼我們慢一點",
        [
            "封面｜一杯咖啡，也可以是今天的休息鍵",
            "Mori Café 不追求最快出杯，我們在意每一杯是否剛好適合你。",
            "豆子每天少量研磨，讓香氣不必在櫃子裡等待。",
            "牛奶、甜度與濃度都能調整，不需要勉強自己喝『標準答案』。",
            "我們保留安靜座位，也歡迎只想坐十分鐘的人。",
            "外帶杯、店內杯，同樣認真完成。",
            "今天不必完成所有事，先喝完眼前這一杯。",
            "結尾｜收藏這組，下次需要休息時回來找我們。",
        ],
    ),
    (
        "招牌商品｜三款咖啡怎麼選",
        [
            "封面｜第一次來 Mori Café，從這三杯開始",
            "晨光拿鐵｜柔和、奶香明顯，適合不喜歡苦味的人。",
            "海風美式｜乾淨清爽，尾韻帶一點柑橘感。",
            "慢曜日摩卡｜可可感較濃，像一份可以喝的甜點。",
            "想提神：選海風美式。",
            "想放鬆：選晨光拿鐵。",
            "想獎勵自己：選慢曜日摩卡。",
            "結尾｜留言告訴我們，你今天是哪一杯？",
        ],
    ),
    (
        "咖啡小知識｜酸不等於壞",
        [
            "封面｜咖啡有酸味，不代表咖啡壞了",
            "咖啡果實本來就含有自然果酸。",
            "淺焙常保留較多花香、柑橘或莓果般的明亮感。",
            "深焙通常帶出更多焦糖、堅果與可可風味。",
            "好喝的酸感應該乾淨、明亮，不會尖銳刺口。",
            "如果怕酸，可以選低酸豆、深一點的焙度或搭配牛奶。",
            "最重要的不是懂術語，而是找到自己喜歡的味道。",
            "結尾｜收藏這張，下次點咖啡就不再只說『不要酸』。",
        ],
    ),
    (
        "幕後日常｜開店前的一小時",
        [
            "封面｜你來以前，咖啡店已經醒了一小時",
            "07:00 拉開窗簾，先讓早晨進到店裡。",
            "07:10 校正磨豆機，第一杯通常不是賣給客人的。",
            "07:20 試喝濃縮，調整今天的研磨刻度。",
            "07:35 烤好第一盤可頌，店裡開始有奶油香。",
            "07:45 擦桌、補水、把每張椅子放回熟悉的位置。",
            "08:00 門打開，今天的第一句是『早安』。",
            "結尾｜你通常幾點需要第一杯咖啡？",
        ],
    ),
    (
        "情境選單｜今天需要哪一種陪伴",
        [
            "封面｜依照今天的心情點咖啡",
            "需要清醒｜雙份海風美式，不加糖。",
            "需要安慰｜溫熱晨光拿鐵，加一點肉桂。",
            "需要專注｜手沖單品，慢慢喝完一整壺。",
            "需要放空｜低咖啡因拿鐵，坐窗邊。",
            "需要慶祝｜慢曜日摩卡，加一份小甜點。",
            "沒有答案也沒關係，告訴店員你今天的感覺。",
            "結尾｜分享給那位最近很需要一杯咖啡的人。",
        ],
    ),
    (
        "空間體驗｜找到適合你的座位",
        [
            "封面｜咖啡店的座位，也有不同個性",
            "窗邊位｜適合放空、看人群與自然光拍照。",
            "長桌位｜適合工作，但記得讓肩膀休息。",
            "角落單人位｜適合讀書與安靜整理心情。",
            "戶外位｜適合天氣舒服、想帶寵物一起來的日子。",
            "吧台位｜適合想看看咖啡怎麼完成的人。",
            "沒有最佳座位，只有今天最適合你的座位。",
            "結尾｜你是窗邊派、角落派，還是吧台派？",
        ],
    ),
    (
        "品牌故事｜名字從哪裡來",
        [
            "封面｜Mori，不只是一個好聽的名字",
            "Mori 在日文裡讓人想到森林。",
            "我們想做的不是華麗的店，而是一個讓呼吸慢下來的地方。",
            "木頭、植物和低飽和色，都是為了減少視覺噪音。",
            "菜單不需要很長，每一項都應該有留下來的理由。",
            "服務不必過度熱情，但要讓人覺得被好好看見。",
            "如果你離開時比進門時放鬆一點，這個名字就有意義。",
            "結尾｜這就是 Mori Café 想成為的日常森林。",
        ],
    ),
    (
        "常見問題｜來店前先知道",
        [
            "封面｜第一次來 Mori Café？這些問題先回答你",
            "可以訂位嗎？｜平日可預約，週末保留部分現場座位。",
            "有低咖啡因嗎？｜有，可替換大部分義式咖啡。",
            "可以帶寵物嗎？｜戶外座位歡迎牽繩寵物。",
            "有插座嗎？｜長桌區有，尖峰時段請體諒共用。",
            "有植物奶嗎？｜提供燕麥奶，可詢問當日庫存。",
            "可以拍照嗎？｜可以，但請不要影響其他客人。",
            "結尾｜還想知道什麼？留言讓我們補上。",
        ],
    ),
    (
        "九日收尾｜收藏與到店行動",
        [
            "封面｜九天認識 Mori Café，今天換你來坐坐",
            "如果你喜歡安靜，平日上午是最舒服的時間。",
            "如果你喜歡陽光，下午三點前選窗邊位。",
            "如果你第一次來，從晨光拿鐵開始。",
            "如果你正在戒咖啡因，我們也準備了低咖啡因選擇。",
            "出示這篇收藏畫面，可獲得當週限定小點試吃一份。",
            "活動期間｜範例：7/23–7/31；實際販售模板時請替換。",
            "結尾｜收藏、分享，然後找一天真的來休息。",
        ],
    ),
]

DAY_STYLES = [
    {
        "id": "quiet-arch-editorial",
        "name": "靜謐拱窗編輯誌",
        "system": "asymmetrical literary editorial pages, one tall arched photo window, generous cream negative space, fine serif rules and tiny botanical marks",
        "cover": "a tall arched coffee photograph occupies the right 44%; a quiet left-aligned headline stack sits low on the left; one thin vertical rule and a tiny leaf mark",
        "content": ["arched photo window on the left with a narrow essay column on the right", "large serif statement above a shallow panoramic photo", "two unequal cream columns separated by a fine vertical rule"],
        "closing": "small centered logo beneath a large empty arch outline, with the CTA anchored at the bottom",
    },
    {
        "id": "menu-modular-grid",
        "name": "招牌選品模組",
        "system": "bold modular menu grid, espresso color blocks, product cut-outs, price-tag-like labels and crisp sans-serif hierarchy",
        "cover": "a 2×2 modular grid: oversized headline in the upper-left block, three isolated drink cut-outs crossing the remaining blocks, rounded product labels",
        "content": ["product cut-out centered over two offset color blocks with a side label", "three stacked specification rows with a small circular drink crop", "comparison grid with bold category tabs and one cropped ingredient photo"],
        "closing": "bold espresso offer block, three small product tokens and an oversized rounded CTA button",
    },
    {
        "id": "coffee-field-notes",
        "name": "咖啡風味手記",
        "system": "field-notebook education pages, ruled-paper cues, annotated bean diagrams, underlines, numbered callouts and restrained handwritten accents",
        "cover": "an open-notebook composition viewed from above; headline on the left page, annotated coffee bean and flavor diagram on the right page",
        "content": ["numbered observation with an annotated macro photo and hand-drawn arrow", "ruled note card with three circled keywords and a bean diagram", "vertical tasting scale beside a clipped field photograph"],
        "closing": "a signed field-note page with a circled takeaway, small taped photo and handwritten-style CTA underline",
    },
    {
        "id": "opening-hour-documentary",
        "name": "開店紀實時間軸",
        "system": "documentary contact sheet, timestamp labels, cinematic still frames, film perforation details and chronological reading rhythm",
        "cover": "three horizontal cinematic frames stacked like a contact sheet, a large 07:00 timestamp crossing the frames, headline in a bottom caption strip",
        "content": ["wide documentary still with timestamp and compact caption underneath", "two-frame before-and-after contact sheet with a time code rail", "vertical timeline connecting one large and two thumbnail frames"],
        "closing": "final film frame marked 08:00 with a wide caption bar and invitation CTA",
    },
    {
        "id": "mood-menu-bands",
        "name": "心情選單色帶",
        "system": "playful mood-selector system, vertical color bands, pill-shaped mood chips, small organic icons and soft color-coded cards",
        "cover": "five slim vertical mood bands span the page; the headline floats in a cream rounded card across the middle; tiny mood icons sit along the bands",
        "content": ["one dominant vertical color band with three mood chips and a small drink cut-out", "stack of rounded choice cards with a soft organic marker", "split mood meter with two color fields and a centered recommendation"],
        "closing": "a fan of mood chips around a central rounded CTA card, without photographic framing",
    },
    {
        "id": "space-guide-map",
        "name": "座位空間導覽",
        "system": "architectural guide pages, simplified floor-plan lines, coordinate markers, framed interior views and zone labels",
        "cover": "a simplified café floor plan fills the background; three numbered location pins connect to small framed interior photos; headline sits in a map legend box",
        "content": ["one large interior frame paired with a coordinate label and mini floor-plan locator", "two stacked room views linked by a dotted walking path", "zone card with seat icons, light-direction arrow and framed detail photo"],
        "closing": "mini floor plan with the preferred seat circled, logo as a map key and CTA in a route label",
    },
    {
        "id": "brand-archive-scrapbook",
        "name": "品牌森林剪貼簿",
        "system": "warm archival scrapbook, layered torn paper, taped photographs, botanical pressings, date stamps and restrained handwritten notes",
        "cover": "one rotated archival café photo taped near the upper-left, a torn sage paper headline layer crossing the lower half, pressed leaf and date stamp",
        "content": ["layered torn-paper story card with one taped archival photo", "large typewritten quote beside a pressed botanical specimen", "two overlapping snapshots with a handwritten margin note"],
        "closing": "postcard-like closing page with stamp, small logo, pressed leaf and handwritten CTA",
    },
    {
        "id": "faq-conversation-cards",
        "name": "來店問答卡",
        "system": "structured question-and-answer interface, alternating speech cards, accordion tabs, clear icons and high-legibility sans typography",
        "cover": "three oversized staggered question bubbles surround a central headline card; a tiny coffee-cup icon acts as the conversation avatar",
        "content": ["large question tab on top and a contrasting answer card below", "two alternating speech cards with a small supporting photo circle", "accordion-style information stack with one expanded answer"],
        "closing": "an open question bubble with the CTA as the reply, plus a small centered logo avatar",
    },
    {
        "id": "campaign-poster",
        "name": "九日收尾活動海報",
        "system": "confident campaign poster, full-bleed lifestyle image, oversized condensed headline, date badge, offer block and strong action hierarchy",
        "cover": "full-bleed sunlit café photograph, oversized headline spanning nearly the full width, a high-contrast date badge and a bottom offer strip",
        "content": ["full-bleed photo with one oversized typographic statement", "bold half-photo half-offer block with a circular date badge", "large numbered benefit over a monochrome lifestyle crop"],
        "closing": "poster-like offer lockup with huge CTA, date range, logo and a single clear action block",
    },
]


def nine_slides(slides, industry):
    """Always return nine useful cards, including a branded closing card."""
    result = list(slides[:8])
    while len(result) < 8:
        result.append(f"內容｜補充一個與{industry}主題直接相關、可實行的重點。")
    result.append("品牌收尾｜Mori Café · Slow coffee, soft days.｜#MoriCafe #咖啡日常 #慢生活")
    return result


def split_copy(raw, slide_no):
    if "｜" in raw:
        lead, body = raw.split("｜", 1)
    else:
        lead, body = ("重點", raw)
    if slide_no == 1:
        return "TODAY'S PAUSE", body, "讓日常慢一點，也讓選擇更適合自己。"
    if slide_no == 9:
        return "MORI CAFÉ", "Slow coffee, soft days.", "收藏這組內容，下次需要休息時再回來。"
    return lead.upper(), body, "一個小選擇，也能改變今天的節奏。"

CONTENT_STRUCTURES = {
    2: "an establishing page with one dominant image or diagram and a short context caption anchored below",
    3: "a 60/40 explanatory split with one clear fact and one supporting visual; no repeated cover composition",
    4: "a focused detail page with one oversized keyword or number and a small evidence image",
    5: "a visual breathing-space page: one short statement or mood line with generous negative space and one quiet image",
    6: "a comparison or choice page using two clearly separated options, labels or visual states",
    7: "a proof, process or behind-the-scenes page with one main visual and two concise annotations",
    8: "a recap or bridge page that resolves the story and gives one reason to continue to the final card",
}


def card_copy(raw, slide_no):
    """Give each slide only the copy elements its storytelling role needs."""
    lead, body = raw.split("｜", 1) if "｜" in raw else ("", raw)
    page = f"頁碼：{slide_no}/9"
    if slide_no == 1:
        return (
            "LOGO：Mori Café\n"
            f"小主題／KICKER：{lead or '今日主題'}\n"
            f"大主題／HEADLINE：{body}\n"
            "滑動提示／SWIPE CUE：向左滑，慢慢看完 →\n"
            f"{page}"
        )
    if slide_no in (2, 3, 4):
        label = {2: "先從這裡開始", 3: "值得注意", 4: "一個關鍵細節"}[slide_no]
        return f"段落標籤／SECTION：{lead or label}\n重點文字／STATEMENT：{body}\n{page}"
    if slide_no == 5:
        return f"停頓句／PAUSE LINE：{body}\n{page}"
    if slide_no in (6, 7):
        label = lead or ("怎麼選" if slide_no == 6 else "再看近一點")
        return f"段落標籤／SECTION：{label}\n內容／CONTENT：{body}\n{page}"
    if slide_no == 8:
        return f"收束句／TAKEAWAY：{body}\n輕提示／SOFT PROMPT：值得的話，先收藏起來。\n{page}"
    return (
        "LOGO：Mori Café\n"
        "品牌句／BRAND LINE：Slow coffee, soft days.\n"
        "CTA：收藏這組內容，下次需要休息時再回來。\n"
        "HASHTAG：#MoriCafe #咖啡日常 #慢生活\n"
        f"{page}"
    )


def image_prompt(industry, topic, slide_no, raw, style):
    if slide_no == 1:
        layout = style["cover"]
    elif slide_no == 9:
        layout = style["closing"]
    else:
        accent = style["content"][(slide_no - 2) % len(style["content"])]
        layout = f"{CONTENT_STRUCTURES[slide_no]}; family-specific treatment: {accent}"
    copy = card_copy(raw, slide_no)
    return (
        f"Generate exactly ONE standalone Instagram carousel card, slide {slide_no} of 9. "
        "Output only this single 4:5 card, never nine cards on one canvas, never a phone mockup and never surrounding "
        "white canvas. A grid, contact-sheet rhythm or multi-frame layout is allowed only when today's named template "
        "family explicitly requests it; it must still remain one standalone card. "
        "Output aspect ratio 4:5, 1080×1350, edge-to-edge. This card belongs to a coordinated nine-card system for "
        f"{industry}, topic “{topic}”. TEMPLATE FAMILY {style['id']}｜{style['name']} (one of nine deliberately "
        "different template families). Keep Mori Café's brand DNA consistent, but never reuse another day's cover "
        "grid, photo mask, information rhythm or decorative device. Family-specific design system: "
        f"{style['system']}. Shared brand palette: warm cream paper texture, "
        "espresso brown and muted sage, soft morning sunlight, restrained organic shapes, subtle film grain, "
        "consistent 80px safe margin, Traditional-Chinese serif paired with a clean sans-serif. "
        f"Layout: {layout}. Render only the copy roles assigned to this slide—do not add Logo, Mood, CTA or hashtags "
        f"when they are not listed below. Professionally typeset this Traditional-Chinese sample copy:\n{copy}\n"
        "Keep every visible component visually separable for later rebuilding in Canva, including its text roles, "
        "page number, photo or diagram and decorative elements. Do not print layer-instruction labels. Use real "
        "legible Traditional Chinese, not random glyphs or fake text. "
        "No watermark, signature or imitation of an existing brand/designer."
    )


def canva_spec(style):
    return (
        f"CANVA TEMPLATE SPEC｜Template family: {style['name']} ({style['id']}). 1080×1350 px, 9 separate pages. "
        f"Family design grammar: {style['system']}. Safe margin 80 px. Rebuild each generated reference "
        "with named editable layers based on what that page actually uses; do not force LOGO, MOOD, CTA or HASHTAG "
        "onto every page. Use at most two font families and three brand colors. Build page 1 as the hook; pages 2–4 "
        "establish and explain; page 5 creates visual breathing room; pages 6–7 compare or prove; page 8 recaps; "
        "page 9 carries the brand and CTA. Use the generated cards only as layout references; replace "
        "their baked text with editable Canva text and replace photography with its own frame. "
        "Save as a master design, duplicate before each client edit, then create a Brand Template link for customers."
    )


def make_brief(day, cycle, day_index):
    industry = INDUSTRIES[cycle % len(INDUSTRIES)]
    style = DAY_STYLES[day_index]
    if cycle == 0:
        topic, slides = CAFE_DAYS[day_index]
    else:
        topics = ["品牌定位", "招牌服務", "知識教育", "幕後流程", "選擇指南", "使用情境", "品牌故事", "常見問題", "行動方案"]
        topic = topics[day_index]
        slides = [
            f"封面｜{industry}九日內容包：{topic}",
            f"問題｜客戶在接觸{industry}時最常遇到的困難",
            "觀點｜品牌對這個問題的清楚立場",
            "方法一｜一個可以立刻實行的步驟",
            "方法二｜降低客戶理解門檻的具體例子",
            "證明｜流程、細節、案例或常見結果",
            "提醒｜避免誇大承諾，加入適用條件",
            "結尾｜收藏、分享或預約下一步；替換成品牌真實 CTA",
        ]
    slides = nine_slides(slides, industry)
    image_items = [
        {
            "type": f"IG 圖組・第 {index + 1} 張",
            "purpose": topic,
            "engine": "ChatGPT Images",
            "status": "prompt",
            "text": image_prompt(industry, topic, index + 1, slide, style),
        }
        for index, slide in enumerate(slides)
    ]
    return {
        "date": day.isoformat(),
        "stream": "carousel",
        "title": f"IG Carousel 九日包｜{industry} Day {day_index + 1}｜{style['name']}",
        "focus": topic,
        "meta": f"第 {day_index + 1}/9 套｜{style['name']} · 9 張獨立 4:5 圖卡",
        "summary": f"本輪 9 天鎖定「{industry}」，九天使用九套不重複設計系統。今天是「{style['name']}」：同品牌色彩、字體與 Logo 語言，但封面、圖片框、資訊層級及裝飾均與其他天不同。",
        "items": image_items + [
            {"type": "Canva 拆件規格", "purpose": f"可販售模板｜{style['name']}", "engine": "Canva Pro", "status": "prompt", "text": canva_spec(style)},
        ],
    }


def main():
    payload = json.loads(DATA.read_text())
    today = date.today()
    delta = max(0, (today - EPOCH).days)
    cycle = delta // 9
    cycle_start = EPOCH + timedelta(days=cycle * 9)
    by_date = {brief["date"]: brief for brief in payload.get("briefs", [])}
    for day_index in range(9):
        day = cycle_start + timedelta(days=day_index)
        if day.isoformat() in LOCKED_DATES and day.isoformat() in by_date:
            continue
        by_date[day.isoformat()] = make_brief(day, cycle, day_index)
    payload["briefs"] = sorted(by_date.values(), key=lambda item: item["date"])
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"Carousel cycle ready: {INDUSTRIES[cycle % len(INDUSTRIES)]}, {cycle_start} through {cycle_start + timedelta(days=8)}")


if __name__ == "__main__":
    main()
