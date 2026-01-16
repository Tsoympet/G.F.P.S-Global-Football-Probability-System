import unittest

from backend.xg import compute_xg_summary


class XGTests(unittest.TestCase):
    def test_compute_xg_summary_aggregates(self):
        snapshot = {
            "fixtures": [
                {"id": "10", "homeTeam": "Alpha", "awayTeam": "Beta"},
            ],
            "events": {
                "10": [
                    {"minute": 3, "description": "Alpha shot", "team": "Alpha"},
                    {"minute": 15, "description": "Beta penalty", "team": "Beta", "xg": 0.8},
                ]
            },
        }
        summary = compute_xg_summary(snapshot)
        self.assertEqual(len(summary), 1)
        item = summary[0]
        self.assertGreater(item["xg"]["home"], 0)
        self.assertGreaterEqual(item["xg"]["away"], 0.8)
        self.assertTrue(item["timeline"])


if __name__ == "__main__":
    unittest.main()
