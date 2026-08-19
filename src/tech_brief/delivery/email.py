import logging

import httpx

from tech_brief.config import settings

log = logging.getLogger(__name__)


def send(subject: str, html: str, to: str | None = None) -> None:
    to_email = to or settings.digest_to_email
    if not to_email:
        raise RuntimeError("DIGEST_TO_EMAIL is not set")
    if not settings.resend_api_key:
        raise RuntimeError("RESEND_API_KEY is not set")

    r = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {settings.resend_api_key}"},
        json={
            "from": settings.digest_from_email,
            "to": [to_email],
            "subject": subject,
            "html": html,
        },
        timeout=15,
    )
    r.raise_for_status()
    log.info("delivered digest to %s", to_email)
