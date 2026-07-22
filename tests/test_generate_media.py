import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.generate_media import find_block, find_video_uri, normalized_music_items, choose_item


class MediaHelpersTest(unittest.TestCase):
    def test_finds_nested_audio(self):
        value = {"steps": [{"content": [{"type": "audio", "data": "YWJj"}]}]}
        self.assertEqual(find_block(value, "audio")["data"], "YWJj")

    def test_finds_nested_video_uri(self):
        value = {"response": {"generatedVideos": [{"video": {"uri": "https://example.test/video"}}]}}
        self.assertEqual(find_video_uri(value), "https://example.test/video")

    def test_normalizes_old_music_schema(self):
        brief = {"focus": "test", "prompts": ["one", "two"]}
        self.assertEqual(len(normalized_music_items(brief)), 2)
        self.assertEqual(brief["items"][0]["engine"], "Lyria")

    def test_ready_item_is_skipped(self):
        items = [{"type": "B-roll", "generation": {"status": "ready"}}]
        self.assertIsNone(choose_item(items, {"B-roll"}))


if __name__ == "__main__":
    unittest.main()
