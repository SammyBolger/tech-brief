import hashlib
import logging
import time
from datetime import UTC, datetime, timedelta

import feedparser

from tech_brief.config import settings

log = logging.getLogger(__name__)

# Reddit blocks anonymous JSON requests. The RSS endpoint still works.
SUBREDDITS = ["MachineLearning", "programming", "artificial", "LocalLLaMA"]


def fetch_reddit_top() -> list[dict]:
    cutoff = datetime.now(UTC) - timedelta(hours=settings.hours_lookback)
    out: list[dict] = []
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top/.rss?t=day"
        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            log.warning("reddit %s failed: %s", sub, exc)
            continue

        if feed.bozo and not feed.entries:
            log.warning("reddit %s returned no entries", sub)
            continue

        for entry in feed.entries[: settings.max_stories_per_source]:
            published = _to_datetime(
                entry.get("published_parsed") or entry.get("updated_parsed")
            )
            if published and published < cutoff:
                continue
            link = entry.get("link", "")
            if not link:
                continue
            out.append(
                {
                    "source": f"reddit:{sub}",
                    "source_id": hashlib.sha256(link.encode()).hexdigest()[:16],
                    "title": entry.get("title", ""),
                    "url": link,
                    "score": 0,
                    "num_comments": 0,
                    "author": entry.get("author", ""),
                    "published_at": (published or datetime.now(UTC)).isoformat(),
                }
            )
    return out


def _to_datetime(parsed) -> datetime | None:
    if not parsed:
        return None
    try:
        return datetime.fromtimestamp(time.mktime(parsed), UTC)
    except (TypeError, ValueError, OverflowError):
        return None
