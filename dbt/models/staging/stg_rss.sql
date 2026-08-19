select
    source,
    source_id,
    title,
    url,
    author,
    published_at,
    ingested_at
from {{ source('raw', 'raw_stories') }}
where source like 'rss:%'
