import logging
import os
import subprocess
from pathlib import Path

from tech_brief.config import settings
from tech_brief.db import connect
from tech_brief.sources import github_trending, hackernews, reddit, rss

log = logging.getLogger(__name__)


def ingest_all() -> int:
    """Pull from every source and overwrite the raw_stories table."""
    stories: list[dict] = []
    stories.extend(hackernews.fetch_top_stories())
    stories.extend(rss.fetch_all_feeds())
    stories.extend(reddit.fetch_reddit_top())
    stories.extend(github_trending.fetch_trending_repos())

    log.info("pulled %d stories across all sources", len(stories))

    con = connect()
    try:
        con.execute(
            """
            create table if not exists raw_stories (
                source text,
                source_id text,
                title text,
                url text,
                score integer,
                num_comments integer,
                author text,
                published_at timestamp,
                ingested_at timestamp default current_timestamp
            )
            """
        )
        con.execute("delete from raw_stories")
        if stories:
            con.executemany(
                """
                insert into raw_stories
                (source, source_id, title, url, score, num_comments, author, published_at)
                values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        s["source"],
                        s["source_id"],
                        s["title"],
                        s["url"],
                        s["score"],
                        s["num_comments"],
                        s["author"],
                        s["published_at"],
                    )
                    for s in stories
                ],
            )
    finally:
        con.close()

    return len(stories)


def run_dbt() -> None:
    project_root = Path(__file__).resolve().parents[2]
    dbt_dir = project_root / "dbt"
    db_path = (project_root / Path(settings.db_path)).resolve()
    env = {**os.environ, "TECH_BRIEF_DB_PATH": str(db_path)}
    result = subprocess.run(
        ["dbt", "build", "--project-dir", str(dbt_dir), "--profiles-dir", str(dbt_dir)],
        cwd=project_root,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("dbt build failed\nstdout:\n%s\nstderr:\n%s", result.stdout, result.stderr)
        raise RuntimeError("dbt build failed")
    log.info("dbt build succeeded")
