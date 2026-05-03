import unittest

from app.utils.json_safe import parse_json_safe


class TestParseJsonSafe(unittest.TestCase):
    def test_parses_plain_object(self):
        self.assertEqual(parse_json_safe('{"a": 1}'), {"a": 1})

    def test_parses_markdown_code_fence(self):
        text = "```json\n{ \"ok\": true }\n```"
        self.assertEqual(parse_json_safe(text), {"ok": True})

    def test_extracts_object_from_surrounding_text(self):
        text = "some preamble\n{ \"x\": 2, \"y\": 3 }\ntrailing"
        self.assertEqual(parse_json_safe(text), {"x": 2, "y": 3})

    def test_extracts_array_from_surrounding_text(self):
        text = "prefix [1, 2, 3] suffix"
        self.assertEqual(parse_json_safe(text), [1, 2, 3])

    def test_returns_none_on_empty(self):
        self.assertIsNone(parse_json_safe("   "))

