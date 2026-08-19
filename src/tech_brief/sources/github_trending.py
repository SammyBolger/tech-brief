import logging
from datetime import UTC, datetime, timedelta

import httpx

log = logging.getLogger(__name__)


def fetch_trending_repos(limit: int = 25) -> list[dict]:
    """Repos created in the last 7 days ranked by stars.

    GitHub does not expose an official trending API. This uses the search
    endpoint as a proxy: repos created recently and sorted by stars.
    """
    since = (datetime.now(UTC) - timedelta(days=7)).strftime("%Y-%m-%d")
    q = f"created:>{since}"
    try:
        r = httpx.get(
            "https://api.github.com/search/repositories",
            params={"q": q, "sort": "stars", "order": "desc", "per_page": limit},
            headers={"Accept": "application/vnd.github+json"},
            timeout=10,
        )
        r.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("github trending failed: %s", exc)
        return []

    out: list[dict] = []
    for item in r.json().get("items", []):
        description = item.get("description") or ""
        out.append(
            {
                "source": "github_trending",
                "source_id": str(item["id"]),
                "title": f"{item['full_name']}: {description}".strip().rstrip(":"),
                "url": item["html_url"],
                "score": int(item.get("stargazers_count", 0)),
                "num_comments": int(item.get("open_issues_count", 0)),
                "author": item["owner"]["login"],
                "published_at": item.get("created_at", ""),
            }
        )
    return out
