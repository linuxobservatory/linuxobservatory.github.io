#!/usr/bin/env python3
"""Refresh the six newest public uploads from Linux Observatory's YouTube Atom feed."""
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "latest-videos.json"
CHANNEL = "https://www.youtube.com/@LinuxObservatory"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LinuxObservatorySite/1.0)"}

def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read().decode("utf-8")

def main():
    page = get(CHANNEL)
    ids = re.findall(r'(?:\"externalId\"|\"channelId\"|\"channel_id\")\s*:\s*\"(UC[A-Za-z0-9_-]{22})\"', page)
    if not ids:
        raise RuntimeError("Unable to resolve the channel ID; existing data was preserved")
    channel_id = ids[0]
    feed = ET.fromstring(get("https://www.youtube.com/feeds/videos.xml?channel_id=" + channel_id))
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
    entries = []
    for entry in feed.findall("a:entry", ns):
        video_id = entry.findtext("yt:videoId", namespaces=ns)
        title = entry.findtext("a:title", default="", namespaces=ns).strip()
        published = entry.findtext("a:published", default="", namespaces=ns)
        if video_id and re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            entries.append({"id": video_id, "title": title, "published": published, "url": "https://www.youtube.com/watch?v=" + video_id, "thumbnail": "https://i.ytimg.com/vi/" + video_id + "/hqdefault.jpg"})
    entries.sort(key=lambda x: x["published"], reverse=True)
    if not entries:
        raise RuntimeError("Feed returned no videos; existing data was preserved")
    payload = {"channel": CHANNEL, "updated_at": datetime.now(timezone.utc).isoformat(), "videos": entries[:6]}
    DEST.parent.mkdir(parents=True, exist_ok=True)
    output = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if not DEST.exists() or json.loads(DEST.read_text(encoding="utf-8")).get("videos") != payload["videos"]:
        DEST.write_text(output, encoding="utf-8")
        print("Updated latest videos")
    else:
        print("No new uploads")

if __name__ == "__main__":
    main()
