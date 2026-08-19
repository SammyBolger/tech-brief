from pathlib import Path

import duckdb

from tech_brief.config import settings


def connect() -> duckdb.DuckDBPyConnection:
    path = Path(settings.db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))
