import json

from tech_brief import archive
from tech_brief.agent.schemas import Digest, StorySummary, TopicSection


def test_archive_writes_valid_json(tmp_path, monkeypatch):
    monkeypatch.setattr(archive.settings, "briefs_dir", str(tmp_path / "briefs"))
    d = Digest(
        date="2026-08-19",
        overview="two sentences.",
        topics=[
            TopicSection(
                topic="AI / ML",
                stories=[
                    StorySummary(title="t", url="https://x.com", one_liner="why")
                ],
            )
        ],
    )
    path = archive.write(d)
    assert path.exists()
    payload = json.loads(path.read_text())
    assert payload["date"] == "2026-08-19"
    assert payload["topics"][0]["topic"] == "AI / ML"
    assert payload["topics"][0]["stories"][0]["url"] == "https://x.com"
