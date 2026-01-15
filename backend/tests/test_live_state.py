import unittest

from backend.live_state import LiveState


class LiveStateEventFeedTests(unittest.TestCase):
    def test_event_feed_categorization(self):
        state = LiveState()
        state._insert_event_into_feed("fx1", {"type": "Red Card", "player": "A"})
        state._insert_event_into_feed("fx1", {"type": "corner", "team": "Home"})
        state._insert_event_into_feed("fx1", {"type": "substitution", "player": "B"})
        snap = state.snapshot()
        feed = snap.get("eventFeed", {}).get("fx1", {})
        self.assertEqual(len(feed.get("cards", [])), 1)
        self.assertEqual(len(feed.get("corners", [])), 1)
        self.assertEqual(len(feed.get("substitutions", [])), 1)
        self.assertEqual(len(feed.get("other", [])), 0)


if __name__ == "__main__":
    unittest.main()
