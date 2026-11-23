"""Build the public catalogue from yt-dlp's full uploads-playlist JSON on stdin."""
import json
from pathlib import Path
import sys

from update_latest_videos import CHANNEL_ID, VIDEO_ID

PLAYLIST_ID = "UU" + CHANNEL_ID[2:]
DEST = Path(__file__).resolve().parents[1] / "data" / "video-catalog.json"


def verified_catalog(playlist):
    if playlist.get("id") != PLAYLIST_ID or playlist.get("channel_id") != CHANNEL_ID:
        raise ValueError("Unexpected playlist or owner")
    entries = playlist["entries"]
    if not entries or len(entries) != playlist["playlist_count"]:
        raise ValueError("Incomplete playlist")
    videos = []
    seen = set()
    for entry in entries:
        vid = entry["id"]
        title = entry["title"].strip()
        if entry.get("channel_id") != CHANNEL_ID or not VIDEO_ID.fullmatch(vid) or not title:
            raise ValueError("Unverified video")
        if vid in seen:
            raise ValueError("Duplicate video")
        seen.add(vid)
        videos.append({"id": vid, "title": title})
    return {"channel_id": CHANNEL_ID, "videos": videos}


if __name__ == "__main__":
    result = verified_catalog(json.load(sys.stdin))
    DEST.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Verified {len(result['videos'])} public uploads.")
