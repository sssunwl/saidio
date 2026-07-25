import importlib.util
import unittest
from datetime import date
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

    def test_carousel_has_nine_separate_story_role_prompts(self):
        brief = carousel.make_brief(date(2026, 7, 23), 0, 0)
        cards = [item for item in brief["items"] if item["type"].startswith("IG 圖組")]
        self.assertEqual(len(cards), 9)
        self.assertTrue(all("exactly ONE" in item["text"] for item in cards))
        self.assertTrue(all(f"頁碼：{index}/9" in item["text"] for index, item in enumerate(cards, 1)))
        self.assertIn("大主題／HEADLINE", cards[0]["text"])
        self.assertIn("停頓句／PAUSE LINE", cards[4]["text"])
        self.assertIn("CTA：", cards[8]["text"])
        self.assertIn("1080×1350", brief["items"][-1]["text"])

    def test_carousel_cycle_uses_nine_distinct_template_families(self):
        self.assertEqual(len({style["id"] for style in carousel.DAY_STYLES}), 9)
        briefs = [carousel.make_brief(date(2026, 7, 23), 0, index) for index in range(9)]
        covers = [
            next(item["text"] for item in brief["items"] if item["type"] == "IG 圖組・第 1 張")
            for brief in briefs
        ]
        self.assertEqual(len(set(covers)), 9)
        self.assertIn("quiet-arch-editorial", covers[0])
        self.assertIn("menu-modular-grid", covers[1])
        self.assertNotEqual(carousel.DAY_STYLES[0]["cover"], carousel.DAY_STYLES[1]["cover"])

    def test_new_carousels_use_story_roles_not_every_field_on_every_card(self):
        brief = carousel.make_brief(date(2026, 7, 25), 0, 2)
        cards = [item["text"] for item in brief["items"] if item["type"].startswith("IG 圖組")]
        layouts = [
            text.split("Layout: ", 1)[1].split(". Render only", 1)[0]
            for text in cards
        ]
        self.assertEqual(len(set(layouts)), 9)
        self.assertIn("LOGO：Mori Café", cards[0])
        self.assertNotIn("HASHTAG：", cards[4])
        self.assertNotIn("CTA：", cards[4])
        self.assertIn("停頓句／PAUSE LINE", cards[4])
        self.assertIn("HASHTAG：", cards[8])

    def test_capychill_does_not_repeat_before_july_31(self):
        titles = {
            capychill.make_brief(date(2026, 7, day))["title"]
            for day in range(23, 32)
        }
        self.assertEqual(len(titles), 9)

    def test_every_carousel_card_is_a_self_contained_package(self):
        for item in carousel.make_brief(date(2026, 7, 25), 0, 2)["items"]:
            if item["type"].startswith("IG 圖組"):
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
