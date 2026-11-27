import importlib.util
import io
import json
import tempfile
import unittest
from unittest.mock import patch
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

    def test_youtube_uc_prefix_omitted_in_atom_channel_ids(self):
        # Regression: the real Atom feed returned the 22-character ID without UC.
        short_id = mod.CHANNEL_ID[2:]
        videos = mod.parse_feed(fixture(root_id=short_id, bad_entry_id=short_id))
        self.assertEqual(len(videos), 6)


    def test_wrong_feed_owner_rejected(self):
        with self.assertRaises(ValueError):
            mod.parse_feed(fixture(root_id="UC0000000000000000000000"))

    def test_foreign_video_rejected(self):
        with self.assertRaises(ValueError):
            mod.parse_feed(fixture(bad_entry_id="UC0000000000000000000000"))


class FeedOutageTests(unittest.TestCase):
    def unavailable(self):
        return mod.urllib.error.HTTPError(mod.FEED_URL, 503, "Unavailable", {}, None)

    @patch.object(mod.time, "sleep")
    @patch.object(mod.urllib.request, "urlopen")
    def test_503_then_verified_feed(self, fetch, sleep):
        fetch.side_effect = [self.unavailable(), io.BytesIO(fixture())]
        self.assertEqual(mod.fetch_videos(), mod.parse_feed(fixture()))
        sleep.assert_called_once_with(5)

    @patch.object(mod.time, "sleep")
    @patch.object(mod.urllib.request, "urlopen")
    def test_persistent_503_preserves_cache_and_requires_valid_data(self, fetch, sleep):
        fetch.side_effect = self.unavailable()
        with tempfile.TemporaryDirectory() as tmp, patch.object(mod, "DEST", Path(tmp) / "latest.json"):
            with self.assertRaises(ConnectionError):
                mod.main()
            cache = json.dumps({"channel_id": mod.CHANNEL_ID, "channel": mod.CHANNEL_URL,
                                "videos": mod.parse_feed(fixture())})
            mod.DEST.write_text(cache)
            mod.main()
            self.assertEqual(mod.DEST.read_text(), cache)
            self.assertEqual(fetch.call_count, 8)


if __name__ == "__main__":
    unittest.main()
