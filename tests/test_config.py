from tech_brief.config import Settings


def test_defaults_when_env_absent(monkeypatch):
    for k in (
        "ANTHROPIC_API_KEY",
        "RESEND_API_KEY",
        "DIGEST_TO_EMAIL",
        "DIGEST_FROM_EMAIL",
    ):
        monkeypatch.delenv(k, raising=False)
    s = Settings(_env_file=None)
    assert s.review_model.startswith("claude-")
    assert s.hours_lookback == 24
    assert s.max_stories_per_source == 50


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "abc")
    monkeypatch.setenv("DIGEST_TO_EMAIL", "you@x.com")
    s = Settings(_env_file=None)
    assert s.anthropic_api_key == "abc"
    assert s.digest_to_email == "you@x.com"
