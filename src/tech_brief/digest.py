"""End-to-end orchestrator: ingest, transform, summarize, archive, deliver."""

import logging

from tech_brief.agent.graph import run as run_agent
from tech_brief.archive import write as write_archive
from tech_brief.delivery.email import send as send_email
from tech_brief.delivery.template import render
from tech_brief.pipeline import ingest_all, run_dbt

log = logging.getLogger(__name__)


def main() -> None:
    n = ingest_all()
    log.info("ingest: %d stories", n)

    run_dbt()
    log.info("transform: dbt build ok")

    digest = run_agent()
    log.info("agent: digest built with %d topics", len(digest.topics))

    path = write_archive(digest)
    log.info("archive: wrote %s", path)

    subject, html = render(digest)
    send_email(subject, html)
    log.info("delivered")
