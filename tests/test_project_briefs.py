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


class ProjectBriefsTest(unittest.TestCase):
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
