"""LangGraph pipeline that turns the dbt gold table into a Digest object."""

import logging
from datetime import date
from typing import TypedDict

import anthropic
from langgraph.graph import END, StateGraph

from tech_brief.agent.prompts import SUMMARIZE_SYSTEM, SUMMARIZE_USER_TMPL
from tech_brief.agent.schemas import Digest
from tech_brief.config import settings
from tech_brief.db import connect

log = logging.getLogger(__name__)


class DigestState(TypedDict, total=False):
    date: str
    rows: list[dict]
    grouped: dict[str, list[dict]]
    digest: Digest


def fetch_gold(state: DigestState) -> DigestState:
    con = connect()
    try:
        rows = con.execute(
            """
            select topic, title, url, source, final_score
            from fct_daily_digest
            order by topic, final_score desc
            """
        ).fetchall()
    finally:
        con.close()

    state["rows"] = [
        {"topic": r[0], "title": r[1], "url": r[2], "source": r[3], "final_score": r[4]}
        for r in rows
    ]
    log.info("loaded %d rows from fct_daily_digest", len(state["rows"]))
    return state


def group_by_topic(state: DigestState) -> DigestState:
    grouped: dict[str, list[dict]] = {}
    for row in state["rows"]:
        grouped.setdefault(row["topic"], []).append(row)
    state["grouped"] = grouped
    return state


def summarize(state: DigestState) -> DigestState:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    stories_text_parts: list[str] = []
    for topic, rows in state["grouped"].items():
        stories_text_parts.append(f"\n## {topic}")
        for r in rows:
            stories_text_parts.append(f"- {r['title']} ({r['url']}) [source: {r['source']}]")
    stories_text = "\n".join(stories_text_parts)

    user_msg = SUMMARIZE_USER_TMPL.format(
        date=state["date"], stories_by_topic=stories_text
    )

    resp = client.messages.create(
        model=settings.review_model,
        max_tokens=4096,
        system=SUMMARIZE_SYSTEM,
        tools=[
            {
                "name": "emit_digest",
                "description": "Emit the final digest as structured JSON.",
                "input_schema": Digest.model_json_schema(),
            }
        ],
        tool_choice={"type": "tool", "name": "emit_digest"},
        messages=[{"role": "user", "content": user_msg}],
    )
    tool_use = next(b for b in resp.content if b.type == "tool_use")
    state["digest"] = Digest.model_validate(tool_use.input)
    return state


def build_graph():
    g = StateGraph(DigestState)
    g.add_node("fetch_gold", fetch_gold)
    g.add_node("group_by_topic", group_by_topic)
    g.add_node("summarize", summarize)
    g.set_entry_point("fetch_gold")
    g.add_edge("fetch_gold", "group_by_topic")
    g.add_edge("group_by_topic", "summarize")
    g.add_edge("summarize", END)
    return g.compile()


def run(target_date: str | None = None) -> Digest:
    graph = build_graph()
    init: DigestState = {"date": target_date or date.today().isoformat()}
    final = graph.invoke(init)
    return final["digest"]
