{{ config(materialized='table') }}

with unioned as (
    select
        source_id,
        source,
        title,
        url,
        coalesce(score, 0) as score,
        coalesce(num_comments, 0) as num_comments,
        author,
        published_at,
        ingested_at
    from {{ source('raw', 'raw_stories') }}
    where url is not null and url != ''
),
deduped as (
    select
        *,
        row_number() over (partition by url order by ingested_at desc) as rn
    from unioned
)
select
    source_id,
    source,
    title,
    url,
    score,
    num_comments,
    author,
    published_at,
    ingested_at
from deduped
where rn = 1
