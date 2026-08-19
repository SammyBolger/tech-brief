# briefs

One JSON file per day, named `YYYY-MM-DD.json`, written by the daily workflow after the agent finishes.

Shape:

```json
{
  "date": "2026-08-19",
  "overview": "Two sentences summarizing the day.",
  "topics": [
    {
      "topic": "AI / ML",
      "stories": [
        {
          "title": "...",
          "url": "...",
          "one_liner": "..."
        }
      ]
    }
  ]
}
```

These files are the source for the archive UI on my portfolio.
