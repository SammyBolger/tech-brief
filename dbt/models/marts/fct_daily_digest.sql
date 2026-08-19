{{ config(materialized='table') }}

with topics as (
    select
        *,
        case
            when lower(title) like '%claude%'
                or lower(title) like '%anthropic%'
                or lower(title) like '%openai%'
                or lower(title) like '%llm%'
                or lower(title) like '%gpt%'
                or lower(title) like '%agent%'
                or lower(title) like '%rag%'
                or lower(title) like '%langchain%'
                or lower(title) like '%langgraph%'
                or source = 'rss:arxiv_ai'
                or source = 'rss:anthropic'
                or source = 'rss:openai'
                or source = 'reddit:MachineLearning'
                or source = 'reddit:LocalLLaMA'
                or source = 'reddit:artificial'
                then 'AI / ML'
            when lower(title) like '%security%'
                or lower(title) like '%cve%'
                or lower(title) like '%vulnerab%'
                or lower(title) like '%breach%'
                or lower(title) like '%exploit%'
                then 'Security'
            when lower(title) like '%aws%'
                or lower(title) like '%gcp%'
                or lower(title) like '%azure%'
                or lower(title) like '%kubernetes%'
                or lower(title) like '%docker%'
                or lower(title) like '%cloudflare%'
                or lower(title) like '%postgres%'
                then 'Cloud / Infra'
            when source = 'github_trending' then 'Dev Tools'
            when lower(title) like '%startup%'
                or lower(title) like '%funding%'
                or lower(title) like '%raised%'
                or lower(title) like '%acquisition%'
                or lower(title) like '%ipo%'
                then 'Startups'
            else 'General Tech'
        end as topic
    from {{ ref('fct_stories_scored') }}
),
ranked as (
    select
        *,
        row_number() over (partition by topic order by final_score desc) as topic_rank
    from topics
)
select
    topic,
    source,
    title,
    url,
    author,
    published_at,
    score,
    num_comments,
    final_score
from ranked
where topic_rank <= 5
order by topic, final_score desc
