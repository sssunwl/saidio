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


class ProjectBriefsTest(unittest.TestCase):
    def test_capychill_daily_album_is_thirty_minute_ready(self):
        brief = capychill.make_brief(date(2026, 7, 23))
        music = [item for item in brief["items"] if item["type"] == "專輯音樂"]
        videos = [item for item in brief["items"] if item["type"].startswith("影片 Prompt")]
        self.assertEqual(len(music), 10)
        self.assertEqual(len(videos), 6)
        self.assertTrue(all("Veo 3.1 Lite" in item["engine"] for item in videos))
        self.assertTrue(all("Preserve the exact weather shown in the reference" in item["text"] for item in videos))
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


if __name__ == "__main__":
    unittest.main()
