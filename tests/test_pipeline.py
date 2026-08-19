from tech_brief import pipeline
from tech_brief.db import connect


def _fake_stories(source: str, n: int) -> list[dict]:
    return [
        {
            "source": source,
            "source_id": f"{source}-{i}",
            "title": f"title {i}",
            "url": f"https://example.com/{source}/{i}",
            "score": i * 10,
            "num_comments": i,
            "author": "someone",
            "published_at": "2026-08-19T12:00:00+00:00",
        }
        for i in range(n)
    ]


def test_ingest_all_writes_raw_stories(tmp_path, monkeypatch):
    db_path = tmp_path / "t.duckdb"
    monkeypatch.setattr(pipeline, "hackernews", type("m", (), {"fetch_top_stories": lambda: _fake_stories("hackernews", 3)}))
    monkeypatch.setattr(pipeline, "rss", type("m", (), {"fetch_all_feeds": lambda: _fake_stories("rss:x", 2)}))
    monkeypatch.setattr(pipeline, "reddit", type("m", (), {"fetch_reddit_top": lambda: _fake_stories("reddit:y", 1)}))
    monkeypatch.setattr(pipeline, "github_trending", type("m", (), {"fetch_trending_repos": lambda: _fake_stories("github_trending", 1)}))

    from tech_brief.config import settings
    monkeypatch.setattr(settings, "db_path", str(db_path))

    n = pipeline.ingest_all()
    assert n == 7

    con = connect()
    try:
        rows = con.execute("select source, count(*) from raw_stories group by source order by source").fetchall()
    finally:
        con.close()
    assert dict(rows) == {"github_trending": 1, "hackernews": 3, "reddit:y": 1, "rss:x": 2}
