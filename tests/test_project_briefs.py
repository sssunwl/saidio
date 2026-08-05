import importlib.util
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


capychill = load_script("generate_capychill_briefs")
carousel = load_script("generate_carousel_briefs")
voiceover = load_script("generate_voiceover_brief")
suntravel = load_script("generate_suntravel_brief")
blocks = load_script("prompt_blocks")
obcar = load_script("build_obcar_data")


class ProjectBriefsTest(unittest.TestCase):
    def test_obcar_tracker_covers_every_vehicle_and_delivery_step(self):
        data = obcar.build()
        tracker = data["tracker"]
        # 官網車隊表(sona.sssuni.com/okiblues)寫 25 車型,主檔必須跟它一致。
        self.assertEqual(len(tracker["vehicles"]), 25)
        # v2 拿掉七角度那一步,每個比例剩 6 步。
        self.assertEqual(len(tracker["defaultTasks"]), 15)
        self.assertNotIn("angles169", tracker["defaultTasks"])
        self.assertIn("orbitClips916", tracker["defaultTasks"])
        self.assertIn("coastStills916", tracker["defaultTasks"])
        self.assertEqual(tracker["vehicles"][12]["name"], "Honda Freed 三代")
        self.assertEqual(tracker["vehicles"][12]["tasks"]["references"], "done")
        # A01 曾經批准過,2026-08-05 因為改用玻璃反光＋環境寫實規則而退回重生。
        self.assertEqual(tracker["vehicles"][12]["tasks"]["anchor169"], "doing")

    def test_obcar_gives_every_ready_vehicle_its_own_batch(self):
        briefs = obcar.build()["briefs"]
        ready = [v for v in obcar.VEHICLES if v["ready"]]
        self.assertEqual(len(briefs), len(ready))
        self.assertTrue(all(b["items"] and len(b["items"]) == 20 for b in briefs))
        for brief, vehicle in zip(briefs, ready):
            self.assertIn(vehicle["name"], brief["title"])
            self.assertEqual(len([i for i in brief["items"] if i["aspect"] == "16:9"]), 10)
            self.assertEqual(len([i for i in brief["items"] if i["aspect"] == "9:16"]), 10)

    def test_obcar_every_prompt_is_self_contained_and_names_its_own_car(self):
        for brief in obcar.build()["briefs"]:
            vehicle = next(v for v in obcar.VEHICLES if v["id"] == brief["items"][0]["vehicle"])
            for item in brief["items"]:
                self.assertIn("【PROMPT】", item["text"], item["type"])
                self.assertIn("【NEGATIVE PROMPT｜禁止項】", item["text"], item["type"])
                self.assertIn("【RULES｜產出規則】", item["text"], item["type"])
                # 靜態圖必須帶車款身分;影片靠附上的批准圖,不重述車款。
                if "圖・" in item["type"]:
                    self.assertIn(vehicle["model"], item["text"], item["type"])

    def test_obcar_orbit_is_three_chained_legs_not_seven_angles(self):
        items = obcar.build()["briefs"][0]["items"]
        orbit = [i for i in items if "360°環繞" in i["type"]]
        self.assertEqual(len(orbit), 6)  # 兩個比例各三段
        self.assertTrue(all(i["engine"] == "Google Flow Lite" for i in orbit))
        first = [i for i in orbit if " P1 " in i["type"]]
        self.assertTrue(all("已批准的 A01" in i["text"] for i in first))
        later = [i for i in orbit if " P2 " in i["type"] or " P3 " in i["type"]]
        self.assertTrue(all("上一段的尾幀" in i["text"] for i in later))

    def test_obcar_prompts_stay_short_enough_to_scale_to_the_whole_fleet(self):
        # 舊版一條 5,200 字、一台車 130,000 字,23 台根本貼不完。
        # 最長的是 9:16 定錨圖(車款卡+場景+直式衍生規則)。
        # 2026-08-05 上修:玻璃反光、環境寫實、車頭車尾鎖定三段是實拍驗收出來的必要條件,
        # 不是裝飾;仍遠低於舊版 5,200,單條照樣一次貼得完。
        items = [i for b in obcar.build()["briefs"] for i in b["items"]]
        self.assertTrue(max(len(i["text"]) for i in items) < 3800)
        self.assertTrue(sum(len(i["text"]) for i in items) / len(items) < 2600)

    def test_obcar_stills_default_to_okinawa(self):
        images = [i for b in obcar.build()["briefs"] for i in b["items"] if "圖・" in i["type"]]
        self.assertTrue(all(i["engine"] == "ChatGPT Images" for i in images))
        self.assertTrue(all("northern Okinawa" in i["text"] for i in images))

    def test_obcar_final_films_are_three_flow_lite_clips(self):
        items = obcar.build()["briefs"][0]["items"]
        coast = [item for item in items if "海邊跟拍" in item["type"]]
        self.assertEqual(len(coast), 6)
        self.assertTrue(all("10 seconds" in item["text"] for item in coast))
        self.assertTrue(all(item["engine"] == "Google Flow Lite" for item in coast))

    def test_obcar_vertical_prompts_keep_action_inside_four_by_five(self):
        items = [i for b in obcar.build()["briefs"] for i in b["items"] if i["aspect"] == "9:16"]
        self.assertEqual(len(items), 10 * len([v for v in obcar.VEHICLES if v["ready"]]))
        for item in items:
            self.assertIn("centred 4:5", item["text"], item["type"])
            self.assertIn("1080×1350", item["text"], item["type"])
        # 直式定錨必須從已批准的 16:9 衍生,不是各自重新設計場景。
        anchors = [i for i in items if "A01" in i["type"]]
        self.assertTrue(all("approved 16:9 frame" in i["text"] for i in anchors))

    def test_obcar_rules_come_only_from_prompt_blocks(self):
        # 合流的重點:規則有第二份副本就一定會走鐘。生成器不准自己寫 negative/rules,
        # 每條都必須查得到 prompt_blocks 的表,而且落地的字串要一模一樣。
        expected = {
            "A01": blocks.OBCAR_STILL_NEGATIVE,
            "P1": blocks.OBCAR_ORBIT_NEGATIVE, "P2": blocks.OBCAR_ORBIT_NEGATIVE,
            "P3": blocks.OBCAR_ORBIT_NEGATIVE,
            "R01": blocks.OBCAR_STILL_NEGATIVE, "R02": blocks.OBCAR_COAST_NEGATIVE,
        }
        items = [i for b in obcar.build()["briefs"] for i in b["items"]]
        for item in items:
            self.assertTrue(blocks.is_bundled(item["text"]), item["type"])
            code = next(c for c in expected if c in item["type"])
            self.assertIn(expected[code], item["text"], item["type"])
            self.assertIsNotNone(blocks.blocks_for("obcar", item["type"]), item["type"])
        self.assertFalse(hasattr(obcar, "NEG_STILL"), "negative 不該再留在生成器裡")
        self.assertFalse(hasattr(obcar, "RULES"), "rules 不該再留在生成器裡")

    def test_obcar_vertical_anchor_gets_the_vertical_rules(self):
        # A01 是唯一一個規則隨比例改變的鏡頭,查表用的是 type 裡的「9:16」字樣。
        _, landscape = blocks.blocks_for("obcar", "OBcar 圖・16:9 A01 停車場定錨圖")
        _, vertical = blocks.blocks_for("obcar", "OBcar 圖・9:16 A01 停車場定錨圖")
        self.assertIn("批准後這張就是本車的場景主定錨", landscape)
        self.assertIn("已批准的 16:9 A01", vertical)

    def test_every_capychill_item_is_a_self_contained_package(self):
        # A single copy has to carry the prompt, the negative list and the rules,
        # otherwise the rules only exist in someone's memory.
        for item in capychill.make_brief(date(2026, 7, 25))["items"]:
            self.assertTrue(blocks.is_bundled(item["text"]), item["type"])

    def test_concept_prompt_demands_readable_paws(self):
        concept = next(
            item for item in capychill.make_brief(date(2026, 7, 25))["items"]
            if item["type"] == "專輯概念圖"
        )
        self.assertIn("PAW CONSTRUCTION", concept["text"])
        self.assertIn("separated toes", concept["text"])
        self.assertIn("mitten", concept["text"])

    def test_video_prompts_keep_paws_and_weather_alive(self):
        videos = [
            item for item in capychill.make_brief(date(2026, 7, 25))["items"]
            if item["type"].startswith("影片 Prompt")
        ]
        self.assertTrue(all("stiff or locked paws" in item["text"] for item in videos))
        self.assertTrue(all("shift and re-grip very slightly" in item["text"] for item in videos))

    def test_music_brief_bundles_and_flattens_object_prompts(self):
        daily = load_script("generate_daily_brief")
        brief = {
            "focus": "Study / Sleep seed pack",
            "prompts": [{"id": 1, "type": "Core Master Track", "duration": "2:45", "bpm": "72 BPM"}],
        }
        self.assertTrue(daily.bundle_brief(brief))
        text = brief["prompts"][0]
        self.assertTrue(blocks.is_bundled(text))
        self.assertIn("Track 1 — Core Master Track.", text)
        self.assertIn("BPM: 72 BPM", text)
        self.assertFalse(daily.bundle_brief(brief), "bundling twice must be a no-op")

    def test_drama_package_keeps_labelled_vocals_allowed(self):
        self.assertIn("No vocals, lyrics", blocks.music_negative())
        self.assertIn("except a character take", blocks.music_negative(allow_labelled_vocals=True))

    def test_capychill_daily_album_is_thirty_minute_ready(self):
        brief = capychill.make_brief(date(2026, 7, 23))
        music = [item for item in brief["items"] if item["type"] == "專輯音樂"]
        videos = [item for item in brief["items"] if item["type"].startswith("影片 Prompt")]
        self.assertEqual(len(music), 10)
        self.assertEqual(len(videos), 6)
        self.assertTrue(all("Veo 3.1 Lite" in item["engine"] for item in videos))
        self.assertTrue(all("Preserve the exact weather, time of day and light level" in item["text"] for item in videos))
        concept = next(item for item in brief["items"] if item["type"] == "專輯概念圖")
        self.assertIn("DUAL FORMAT", concept["text"])
        self.assertTrue(all("9:16 crop corridor" in item["text"] for item in videos))
        self.assertTrue(all("MANDATORY BASE ENVIRONMENT MOTION" in item["text"] for item in videos))
        self.assertTrue(all("ocean wave bands" in item["text"] for item in videos))
        self.assertEqual(videos[0]["type"], "影片 Prompt・基準驗收・場景動態")
        rainy = capychill.make_brief(date(2026, 7, 24))
        rainy_videos = [item for item in rainy["items"] if item["type"].startswith("影片 Prompt")]
        self.assertTrue(all("rain trails move continuously downward" in item["text"] for item in rainy_videos))

    def test_capychill_video_count_tracks_target_length(self):
        self.assertEqual(
            len([item for item in capychill.make_brief(date(2026, 7, 23), 45)["items"] if item["type"].startswith("影片 Prompt")]),
            8,
        )
        self.assertEqual(
            len([item for item in capychill.make_brief(date(2026, 7, 23), 60)["items"] if item["type"].startswith("影片 Prompt")]),
            10,
        )

    def test_consecutive_concepts_change_story_not_only_weather(self):
        first = capychill.make_brief(date(2026, 7, 23))
        second = capychill.make_brief(date(2026, 7, 24))
        first_prompt = next(item["text"] for item in first["items"] if item["type"] == "專輯概念圖")
        second_prompt = next(item["text"] for item in second["items"] if item["type"] == "專輯概念圖")
        self.assertIn("gratitude note", first_prompt)
        self.assertIn("index cards", second_prompt)
        self.assertIn("seaside writing alcove", first_prompt)
        self.assertIn("glass greenhouse", second_prompt)
        self.assertIn("64% of image width", first_prompt)
        self.assertIn("42% of image width", second_prompt)

    def test_industry_packs_run_first_then_universal_kit(self):
        # 買家先上：教練／房仲／攝影師… 是真的會掏錢的人，百搭 Kit 排在九天之後補齊。
        week = [carousel.make_brief(carousel.INDUSTRY_EPOCH + timedelta(days=n)) for n in range(9)]
        self.assertTrue(all(brief["title"].startswith("IG 行業包") for brief in week))
        self.assertIn("商業教練", week[0]["title"])
        kit = [carousel.make_brief(carousel.UNIVERSAL_EPOCH + timedelta(days=n)) for n in range(5)]
        self.assertTrue(all(brief["title"].startswith("IG 百搭 Kit") for brief in kit))
        self.assertEqual(len({brief["title"] for brief in kit}), 5)

    def test_one_day_is_one_industry_not_nine_days_per_brand(self):
        # The whole reason for the master-plate rewrite: a brand is a day's work.
        week = [carousel.make_brief(carousel.INDUSTRY_EPOCH + timedelta(days=n)) for n in range(9)]
        industries = [brief["title"].split("｜")[1] for brief in week]
        self.assertEqual(len(set(industries)), 9, industries)
        # Coming back to the same industry next round must not reuse the same look.
        again = carousel.make_brief(carousel.INDUSTRY_EPOCH + timedelta(days=carousel.CYCLE_DAYS))
        self.assertIn("商業教練", again["title"])
        self.assertNotEqual(again["title"], week[0]["title"])
        self.assertNotEqual(again["focus"], week[0]["focus"])

    def test_no_two_days_ever_look_the_same(self):
        # SS 的要求是「很多不同款」：視覺 × 配色 × 字型 × 質感 × 結構 五個維度用互質步長輪替，
        # 任何兩天都不該撞在同一個組合上。七種結構會被十四天的循環整除，那個共振特別容易回歸。
        looks = [
            (brief["title"], brief["meta"])
            for brief in (
                carousel.make_brief(carousel.EPOCH + timedelta(days=n)) for n in range(140)
            )
        ]
        self.assertEqual(len(set(looks)), len(looks))
        coach = [t.split("｜")[2] for t, _ in looks if "商業教練" in t]
        self.assertEqual(len(set(coach)), len(coach), coach)

    def test_segment_plate_covers_its_own_card_range_and_no_others(self):
        # 分段生成的核心承諾:每段只描述自己那 3 張,不重複、不跳號、不越界。
        family = carousel.VISUAL_FAMILIES[0]
        cards, segment_count = 9, 3
        seen = set()
        for i in range(segment_count):
            text = carousel.segment_plate_prompt(
                family, "warm-neutral", "warm cream, espresso brown", cards, i, segment_count)
            self.assertTrue(blocks.is_bundled(text))
            first, last = i * 3 + 1, min(cards, (i + 1) * 3)
            self.assertIn(f"cards {first}–{last}", text)
            seen.update(range(first, last + 1))
        self.assertEqual(seen, set(range(1, cards + 1)))

    def test_segment_plate_drops_the_pre_compress_hack_a_9card_plate_needs(self):
        # 9 張一條要求「先畫窄 3 倍」補償非等比拉伸;3 張一段的拉伸接近等比,這條補償應該消失。
        family = carousel.VISUAL_FAMILIES[0]
        whole = carousel.plate_prompt(family, "warm-neutral", "warm cream, espresso brown", 9)
        segment = carousel.segment_plate_prompt(
            family, "warm-neutral", "warm cream, espresso brown", 9, 0, 3)
        self.assertIn("PRE-COMPRESS", whole)
        self.assertNotIn("PRE-COMPRESS", segment)
        self.assertIn("interchangeable slice", segment.replace("\n", " "))

    def test_segment_split_command_maps_each_file_to_the_right_cards(self):
        cmd = carousel.segment_split_command(["a.png", "b.png", "c.png"], 9)
        self.assertIn("a.png --cards 3", cmd)
        self.assertIn("卡 1/2/3", cmd)
        self.assertIn("卡 7/8/9", cmd)

    def test_industry_pack_card_count_follows_its_story_structure(self):
        # 頁數跟著結構走（金句款 6 張、客戶疑慮款 7 張…），不是每天都硬湊九張。
        counts = set()
        for n in range(len(carousel.INDUSTRIES)):
            brief = carousel.make_brief(carousel.INDUSTRY_EPOCH + timedelta(days=n))
            cards = [i for i in brief["items"] if i["type"].startswith("圖卡文字")]
            self.assertIn(f"--cards {len(cards)}",
                          next(i["text"] for i in brief["items"] if i["type"] == "分割指令"))
            self.assertTrue(6 <= len(cards) <= 12, len(cards))
            counts.add(len(cards))
        self.assertGreater(len(counts), 1)

    def test_card_count_varies_by_structure_and_stays_in_range(self):
        counts = {}
        for family in carousel.UNIVERSAL_FAMILIES:
            brief = carousel.universal_brief(carousel.UNIVERSAL_EPOCH, family)
            cards = [i for i in brief["items"] if i["type"].startswith("圖卡文字")]
            self.assertEqual(len(cards), family["cards"], family["name"])
            self.assertEqual(len(family["roles"]), family["cards"], family["name"])
            self.assertTrue(6 <= family["cards"] <= 12, family["name"])
            counts[family["id"]] = family["cards"]
        # The whole point of variable length: they are not all nine.
        self.assertGreater(len(set(counts.values())), 1)

    def test_plate_is_text_free_and_split_command_matches_card_count(self):
        brief = carousel.universal_brief(carousel.UNIVERSAL_EPOCH, carousel.UNIVERSAL_FAMILIES[0])
        plates = [i for i in brief["items"] if i["type"].startswith("母圖")]
        self.assertEqual(len(plates), 3)  # one per colourway
        for plate in plates:
            self.assertTrue(blocks.is_bundled(plate["text"]))
            self.assertIn("NO TEXT OF ANY KIND", plate["text"])
            self.assertIn("9720×1440", plate["text"])
        command = next(i for i in brief["items"] if i["type"] == "分割指令")
        self.assertIn("--cards 9", command["text"])

    def test_only_cover_and_closing_card_carry_logo_and_cta(self):
        family = carousel.UNIVERSAL_FAMILIES[0]
        brief = carousel.universal_brief(carousel.UNIVERSAL_EPOCH, family)
        cards = [i["text"] for i in brief["items"] if i["type"].startswith("圖卡文字")]
        self.assertIn("logo may appear here", cards[0])
        self.assertIn("do not repeat them here", cards[4])
        self.assertIn("one clear CTA", cards[-1])

    def test_carousel_is_three_by_four_everywhere(self):
        brief = carousel.make_brief(carousel.INDUSTRY_EPOCH)
        for item in brief["items"]:
            self.assertNotIn("1080×1350", item["text"])
        spec = next(i for i in brief["items"] if i["type"] == "Canva 拆件規格")
        self.assertIn("1080×1440", spec["text"])
        # Buyers get cropped by the uploader default if nobody tells them.
        self.assertIn("4:5 改成 3:4", spec["text"])

    def test_capychill_does_not_repeat_before_july_31(self):
        titles = {
            capychill.make_brief(date(2026, 7, day))["title"]
            for day in range(23, 32)
        }
        self.assertEqual(len(titles), 9)

    def test_every_carousel_card_is_a_self_contained_package(self):
        for item in carousel.make_brief(carousel.INDUSTRY_EPOCH)["items"]:
            if item["type"].startswith("圖卡文字"):
                self.assertTrue(blocks.is_bundled(item["text"]), item["type"])
                self.assertIn("garbled", item["text"])
                self.assertIn("80 px safe margin", item["text"])

    def test_voiceover_scripts_and_ambience_get_different_rules(self):
        brief = {"items": [
            {"type": "旁白腳本", "text": "今天先深呼吸一次。"},
            {"type": "環境音", "text": "Soft rain on a wooden roof, 60 seconds."},
        ]}
        self.assertTrue(voiceover.bundle_items(brief))
        script, ambience = brief["items"]
        self.assertIn("…（停頓）…", script["text"])
        self.assertIn("-16 LUFS", script["text"])
        self.assertIn("No music, melody", ambience["text"])
        self.assertNotIn("-16 LUFS", ambience["text"])

    def test_bundling_an_already_bundled_brief_is_a_no_op(self):
        # The daily workflow re-runs over its own output; a second pass must not nest blocks.
        brief = {"items": [{"type": "Flow Lite", "text": "Wide shot of a harbour at dawn."}]}
        self.assertTrue(suntravel.bundle_items(brief))
        once = brief["items"][0]["text"]
        self.assertFalse(suntravel.bundle_items(brief))
        self.assertEqual(once, brief["items"][0]["text"])
        self.assertEqual(once.count(blocks.HEAD_RULES), 1)

    def test_locked_album_keeps_its_music_but_gets_new_video_rules(self):
        published = {"items": [
            {"type": "專輯音樂", "text": "ORIGINAL TRACK PROMPT"},
            {"type": "影片 Prompt・舊版", "text": "everything frozen, static rain"},
        ]}
        merged = capychill.keep_published_music(capychill.make_brief(date(2026, 7, 25)), published)
        music = [item for item in merged["items"] if item["type"] == "專輯音樂"]
        self.assertEqual(len(music), 1)
        self.assertEqual(music[0]["text"], "ORIGINAL TRACK PROMPT")
        videos = [item for item in merged["items"] if item["type"].startswith("影片 Prompt")]
        self.assertNotIn("舊版", " ".join(item["type"] for item in videos))
        for video in videos:
            self.assertIn("never frozen", video["text"])


if __name__ == "__main__":
    unittest.main()
