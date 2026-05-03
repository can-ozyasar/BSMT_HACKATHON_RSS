import unittest

from app.services.scorer import calculate_bios_score


class TestScorer(unittest.TestCase):
    def test_bmw_relocation_scores_99(self):
        article = {
            "event_type": "relocation",
            "company": "BMW",
            "from_location": "München",
            "to_location": "Debrecen",
            "sector": "automotive",
            "timeline": "2026 Q1",
            "source_url": "https://www.reuters.com/world/europe/example",
        }
        res = calculate_bios_score(article, graph_delta=0.0)
        self.assertEqual(res["color"], "green")
        self.assertEqual(res["score_final"], 99)

    def test_confidence_penalty_applies_half(self):
        base = {
            "event_type": "other",
            "company": None,
            "from_location": None,
            "to_location": None,
            "sector": None,
            "timeline": None,
            "source_url": "https://blog.example.com/post",
        }
        res = calculate_bios_score(base, graph_delta=0.0)
        self.assertTrue(res["adjustments"]["confidence_penalty"])
        # Should be very low with ×0.50 penalty.
        self.assertLess(res["score_final"], 10)

    def test_industryweek_trust_used(self):
        article = {
            "event_type": "expansion",
            "company": "Siemens",
            "from_location": None,
            "to_location": "Warsaw",
            "sector": "electronics",
            "timeline": "next year",
            "source_url": "https://www.industryweek.com/operations/article/123",
        }
        res = calculate_bios_score(article, graph_delta=0.0)
        self.assertIn(res["color"], {"blue", "yellow", "green"})
