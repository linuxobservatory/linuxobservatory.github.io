#!/usr/bin/env python3
"""Update the latest-six-video grid from the pinned Linux Observatory channel.

Channel identity is fixed. Never resolve the ID from an arbitrary page or search
result: that previously displayed videos from another creator.
"""
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

CHANNEL_ID = "UCNq7pDavJRTEjg3AOdcuMAg"
CHANNEL_URL = "https://www.youtube.com/@LinuxObservatory"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
DEST = Path(__file__).resolve().parents[1] / "data" / "latest-videos.json"
NAMESPACES = {
    "a": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}
VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}\Z")


def parse_feed(xml_content):
    feed = ET.fromstring(xml_content)
    actual_id = feed.findtext("yt:channelId", namespaces=NAMESPACES)
    if actual_id != CHANNEL_ID:
        raise ValueError(f"Wrong YouTube channel ID in feed: {actual_id!r}")

    author_uri = feed.findtext("a:author/a:uri", namespaces=NAMESPACES)
    if author_uri != f"https://www.youtube.com/channel/{CHANNEL_ID}":
        raise ValueError(f"Unexpected channel author URL: {author_uri!r}")

    videos = []
    seen_ids = set()
    for entry in feed.findall("a:entry", NAMESPACES):
        entry_channel = entry.findtext("yt:channelId", namespaces=NAMESPACES)
        if entry_channel != CHANNEL_ID:
            raise ValueError("A video in the feed belongs to another channel")
        vid = entry.findtext("yt:videoId", namespaces=NAMESPACES) or ""
        title = (entry.findtext("a:title", namespaces=NAMESPACES) or "").strip()
        published = entry.findtext("a:published", namespaces=NAMESPACES) or ""
        if not VIDEO_ID.fullmatch(vid) or not title or not published:
            raise ValueError("The YouTube feed contained an incomplete video entry")
        if vid in seen_ids:
            continue
        seen_ids.add(vid)
        videos.append({
            "id": vid,
            "title": title,
            "published": published,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
        })

    videos.sort(key=lambda v: v["published"], reverse=True)
    if len(videos) < 6:
        raise ValueError("Fewer than six verified videos. Existing data retained.")
    return videos[:6]


def main():
    req = urllib.request.Request(
        FEED_URL,
        headers={"User-Agent": "Mozilla/5.0 (Linux Observatory site feed updater)"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        videos = parse_feed(response.read())

    # Do not touch the last known-good data if the feed fails validation.
    existing = json.loads(DEST.read_text(encoding="utf-8")) if DEST.exists() else {}
    if existing.get("channel_id") == CHANNEL_ID and existing.get("videos") == videos:
        print("No new videos to publish.")
        return

    result = {
        "channel_id": CHANNEL_ID,
        "channel": CHANNEL_URL,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "videos": videos,
    }
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Published six verified videos from " + CHANNEL_ID)


if __name__ == "__main__":
    main()
