import logging
from datetime import UTC, datetime, timedelta

import httpx

from tech_brief.config import settings

log = logging.getLogger(__name__)

BASE = "https://hacker-news.firebaseio.com/v0"


def fetch_top_stories(limit: int | None = None) -> list[dict]:
    limit = limit or settings.max_stories_per_source
    cutoff = datetime.now(UTC) - timedelta(hours=settings.hours_lookback)
    out: list[dict] = []
    try:
        with httpx.Client(timeout=10) as client:
            ids = client.get(f"{BASE}/topstories.json").json()[:limit]
            for sid in ids:
                item = client.get(f"{BASE}/item/{sid}.json").json()
                if not item or item.get("type") != "story":
                    continue
                posted = datetime.fromtimestamp(item.get("time", 0), UTC)
                if posted < cutoff:
                    continue
                out.append(
                    {
                        "source": "hackernews",
                        "source_id": str(item["id"]),
                        "title": item.get("title", ""),
                        "url": item.get("url")
                        or f"https://news.ycombinator.com/item?id={item['id']}",
                        "score": int(item.get("score", 0)),
                        "num_comments": int(item.get("descendants", 0) or 0),
                        "author": item.get("by", ""),
                        "published_at": posted.isoformat(),
                    }
                )
    except httpx.HTTPError as exc:
        log.warning("hackernews fetch failed: %s", exc)
    return out
