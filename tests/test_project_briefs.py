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
        self.assertEqual(len(videos), 4)
        self.assertTrue(all("Veo 3.1 Lite" in item["text"] for item in videos))

    def test_carousel_has_eight_ready_copy_slides(self):
        brief = carousel.make_brief(date(2026, 7, 23), 0, 0)
        copy = brief["items"][0]["text"].splitlines()
        self.assertEqual(len(copy), 8)
        self.assertIn("1080×1350", brief["items"][2]["text"])


if __name__ == "__main__":
    unittest.main()
