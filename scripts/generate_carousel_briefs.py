#!/usr/bin/env python3
"""Create one nine-day, one-industry Instagram carousel product cycle."""
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/carousel.json"
EPOCH = date(2026, 7, 23)

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


def image_prompt(industry, topic, slide_no, raw):
    kicker, headline, body = split_copy(raw, slide_no)
    layout = [
        "hero cover: headline in the upper-left, large coffee photograph in the lower-right",
        "editorial split: photograph on left 42%, text on right 58%",
        "editorial split: text on left 58%, photograph on right 42%",
        "number-led layout with a large translucent numeral behind the copy",
        "centered quote card with a small still-life photograph at the bottom",
        "three-level information card with a narrow vertical photograph strip",
        "full-bleed lifestyle photograph with a cream paper text panel",
        "checklist or conclusion card with a quiet top-right photograph",
        "brand closing card with centered CTA and small logo lockup",
    ][slide_no - 1]
    return (
        f"Generate exactly ONE standalone Instagram carousel card, slide {slide_no} of 9. "
        "Do not create a collage, contact sheet, grid, multiple cards, phone mockup or surrounding white canvas. "
        "Output aspect ratio 4:5, 1080×1350, edge-to-edge. This card belongs to a coordinated nine-card system for "
        f"{industry}, topic “{topic}”. Visual system: editorial lifestyle photography, warm cream paper texture, "
        "espresso brown and muted sage, soft morning sunlight, restrained organic shapes, subtle film grain, "
        "consistent 80px safe margin. Use the same brand world as the other cards but make this composition distinct. "
        f"Layout: {layout}. Render this Traditional-Chinese sample copy as visible, professionally typeset text:\n"
        f"LOGO：Mori Café\n小主題／KICKER：{kicker}\n大主題／HEADLINE：{headline}\n"
        f"內文／BODY：{body}\nMOOD：今天不必很快，也能好好前進。\n"
        f"CTA：{'收藏・分享・來店坐坐' if slide_no == 9 else '向左滑看下一張 →'}\n"
        f"HASHTAG：#MoriCafe #咖啡日常 #慢生活\n頁碼：{slide_no}/9\n"
        "Keep every component visually separable for later rebuilding in Canva: [LOGO], [KICKER], [HEADLINE], "
        "[BODY], [MOOD], [CTA], [HASHTAG], [PAGE_NO], [PHOTO] and [DECORATIVE_ELEMENT]. Do not print the square-bracket "
        "labels themselves; they describe layers. Use real legible Traditional Chinese, not random glyphs or fake text. "
        "No watermark, signature or imitation of an existing brand/designer."
    )


def canva_spec():
    return (
        "CANVA TEMPLATE SPEC｜1080×1350 px, 9 separate pages. Safe margin 80 px. Rebuild each generated reference "
        "with named editable layers: LOGO, KICKER, HEADLINE, BODY, MOOD, CTA, HASHTAG, PAGE_NO, PHOTO and "
        "DECORATIVE_ELEMENT. Use at most two font families and three brand colors. Build page 1 cover, pages 2–8 "
        "alternating education/story layouts, page 9 CTA. Use the generated cards only as layout references; replace "
        "their baked text with editable Canva text and replace photography with its own frame. "
        "Save as a master design, duplicate before each client edit, then create a Brand Template link for customers."
    )


def make_brief(day, cycle, day_index):
    industry = INDUSTRIES[cycle % len(INDUSTRIES)]
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
            "text": image_prompt(industry, topic, index + 1, slide),
        }
        for index, slide in enumerate(slides)
    ]
    return {
        "date": day.isoformat(),
        "stream": "carousel",
        "title": f"IG Carousel 九日包｜{industry} Day {day_index + 1}",
        "focus": topic,
        "meta": "9 張獨立 4:5 圖卡 · 每張一條 Prompt＋完整範文排版",
        "summary": f"本輪 9 天鎖定「{industry}」。每一天都有 9 張分開生成、視覺一致但版式不同的完整圖卡，不產生九宮格。",
        "items": image_items + [
            {"type": "Canva 拆件規格", "purpose": "可販售模板", "engine": "Canva Pro", "status": "prompt", "text": canva_spec()},
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
        by_date[day.isoformat()] = make_brief(day, cycle, day_index)
    payload["briefs"] = sorted(by_date.values(), key=lambda item: item["date"])
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"Carousel cycle ready: {INDUSTRIES[cycle % len(INDUSTRIES)]}, {cycle_start} through {cycle_start + timedelta(days=8)}")


if __name__ == "__main__":
    main()
