import httpx
import pytest

from tech_brief.delivery import email


def test_send_raises_when_no_recipient(monkeypatch):
    monkeypatch.setattr(email.settings, "digest_to_email", "")
    with pytest.raises(RuntimeError, match="DIGEST_TO_EMAIL"):
        email.send("s", "<p>b</p>")


def test_send_raises_when_no_api_key(monkeypatch):
    monkeypatch.setattr(email.settings, "digest_to_email", "you@x.com")
    monkeypatch.setattr(email.settings, "resend_api_key", "")
    with pytest.raises(RuntimeError, match="RESEND_API_KEY"):
        email.send("s", "<p>b</p>")


def test_send_posts_to_resend(monkeypatch):
    calls: dict = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        calls["url"] = url
        calls["headers"] = headers
        calls["json"] = json
        req = httpx.Request("POST", url)
        return httpx.Response(200, request=req, json={"id": "r1"})

    monkeypatch.setattr(email.settings, "digest_to_email", "you@x.com")
    monkeypatch.setattr(email.settings, "resend_api_key", "re_test")
    monkeypatch.setattr(email.settings, "digest_from_email", "brief@x.com")
    monkeypatch.setattr(httpx, "post", fake_post)

    email.send("subject", "<p>hi</p>")
    assert calls["url"] == "https://api.resend.com/emails"
    assert calls["headers"]["Authorization"] == "Bearer re_test"
    assert calls["json"]["to"] == ["you@x.com"]
    assert calls["json"]["subject"] == "subject"
