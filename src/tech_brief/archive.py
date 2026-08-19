import json
from pathlib import Path

from tech_brief.agent.schemas import Digest
from tech_brief.config import settings


def write(digest: Digest) -> Path:
    briefs_dir = Path(settings.briefs_dir)
    briefs_dir.mkdir(parents=True, exist_ok=True)
    path = briefs_dir / f"{digest.date}.json"
    path.write_text(json.dumps(digest.model_dump(), indent=2))
    return path
