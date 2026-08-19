from tech_brief.agent.schemas import Digest, StorySummary, TopicSection
from tech_brief.delivery.template import _esc, render


def _digest() -> Digest:
    return Digest(
        date="2026-08-19",
        overview="Two sentences about the day. Another sentence.",
        topics=[
            TopicSection(
                topic="AI / ML",
                stories=[
                    StorySummary(
                        title="Anthropic releases Claude 5",
                        url="https://example.com/claude5",
                        one_liner="A new model with better reasoning.",
                    )
                ],
            )
        ],
    )


def test_render_returns_subject_and_html():
    subject, html = render(_digest())
    assert "2026-08-19" in subject
    assert "Anthropic releases Claude 5" in html
    assert 'href="https://example.com/claude5"' in html
    assert "A new model with better reasoning." in html
    assert "tech-brief" in html.lower()


def test_escape_encodes_special_chars():
    assert _esc("<script>") == "&lt;script&gt;"
    assert _esc('a "b"') == "a &quot;b&quot;"
    assert _esc("a & b") == "a &amp; b"


def test_render_escapes_hostile_input():
    d = Digest(
        date="2026-08-19",
        overview="ok",
        topics=[
            TopicSection(
                topic="AI / ML",
                stories=[
                    StorySummary(
                        title="<script>alert(1)</script>",
                        url="https://example.com",
                        one_liner="ok",
                    )
                ],
            )
        ],
    )
    _, html = render(d)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
