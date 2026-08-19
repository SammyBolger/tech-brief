from pydantic import BaseModel, Field


class StorySummary(BaseModel):
    title: str
    url: str
    one_liner: str = Field(description="One sentence on why the reader should care.")


class TopicSection(BaseModel):
    topic: str
    stories: list[StorySummary]


class Digest(BaseModel):
    date: str
    overview: str = Field(description="Two sentences summarizing the day.")
    topics: list[TopicSection]
