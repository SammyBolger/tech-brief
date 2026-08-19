import hashlib
import logging
import time
from datetime import UTC, datetime, timedelta

import feedparser

from tech_brief.config import settings

log = logging.getLogger(__name__)

FEEDS: dict[str, str] = {
    "anthropic": "https://www.anthropic.com/news/rss.xml",
    "openai": "https://openai.com/blog/rss.xml",
    "the_verge": "https://www.theverge.com/rss/index.xml",
    "ars_technica": "https://feeds.arstechnica.com/arstechnica/index",
    "techmeme": "https://www.techmeme.com/feed.xml",
    "github_blog": "https://github.blog/feed/",
    "arxiv_ai": "http://export.arxiv.org/rss/cs.AI",
}


def fetch_all_feeds() -> list[dict]:
    cutoff = datetime.now(UTC) - timedelta(hours=settings.hours_lookback)
    out: list[dict] = []
    for name, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
        except Exception as exc:
            log.warning("rss %s failed: %s", name, exc)
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
            sid = hashlib.sha256(link.encode()).hexdigest()[:16]
            out.append(
                {
                    "source": f"rss:{name}",
                    "source_id": sid,
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
