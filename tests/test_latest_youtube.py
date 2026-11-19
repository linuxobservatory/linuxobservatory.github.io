import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "update_latest_videos",
    Path(__file__).resolve().parents[1] / "scripts" / "update_latest_videos.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture(root_id=None, bad_entry_id=None):
    good = mod.CHANNEL_ID
    root_id = root_id or good
    entry_id = bad_entry_id or good
    entries = "".join(
        f"<entry><yt:videoId>V{i:010d}</yt:videoId><yt:channelId>{entry_id}</yt:channelId>"
        f"<title>Linux game {i}</title><published>2026-11-{i+10:02d}T12:00:00+00:00</published>"
        f"</entry>"
        for i in range(6)
    )
    return (
        '<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
        f"<yt:channelId>{root_id}</yt:channelId>"
        f"<author><uri>https://www.youtube.com/channel/{good}</uri></author>"
        f"{entries}</feed>"
    ).encode()


class FeedValidationTests(unittest.TestCase):
    def test_pinned_channel_returns_six_in_latest_first_order(self):
        videos = mod.parse_feed(fixture())
        self.assertEqual(len(videos), 6)
        self.assertEqual(videos[0]["id"], "V0000000005")
        self.assertTrue(all("youtube.com/watch?v=" in v["url"] for v in videos))

    def test_wrong_feed_owner_rejected(self):
        with self.assertRaises(ValueError):
            mod.parse_feed(fixture(root_id="UC0000000000000000000000"))

    def test_foreign_video_rejected(self):
        with self.assertRaises(ValueError):
            mod.parse_feed(fixture(bad_entry_id="UC0000000000000000000000"))


if __name__ == "__main__":
    unittest.main()
