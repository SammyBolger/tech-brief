select
    source_id,
    title,
    url,
    score as stars,
    author as owner,
    published_at,
    ingested_at
from {{ source('raw', 'raw_stories') }}
where source = 'github_trending'
