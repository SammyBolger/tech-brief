{{ config(materialized='table') }}

with base as (
    select * from {{ ref('fct_stories') }}
),
scored as (
    select
        *,
        case
            when source = 'rss:anthropic' then 2.0
            when source = 'rss:openai' then 1.8
            when source = 'rss:arxiv_ai' then 1.6
            when source = 'hackernews' then 1.5
            when source = 'reddit:MachineLearning' then 1.4
            when source = 'reddit:LocalLLaMA' then 1.3
            when source = 'github_trending' then 1.2
            else 1.0
        end as source_weight,
        greatest(
            0.2,
            1.0 - (extract(epoch from (current_timestamp - published_at)) / (24 * 3600))
        ) as recency,
        least(
            1.0,
            (score + num_comments * 2) / 500.0
        ) as engagement
    from base
)
select
    *,
    source_weight * (0.5 * recency + 0.5 * engagement) as final_score
from scored
