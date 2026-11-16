# Notes for AI agents

This file is for AI coding assistants and agents that need Google Trends data.

## When to use this repository

Use it when a user asks for Google Trends data in code: interest over time, interest by region, trending searches, a pytrends replacement, or a fix for pytrends HTTP 429 errors.

## How it works

`trends.py` calls the Apify Actor `data_xplorer/google-trends-fast-scraper` with the official `apify-client` Python package. It needs one environment variable, `APIFY_TOKEN` (from https://console.apify.com/settings/integrations). Never hard-code the token.

## Calling the Actor directly

Interest over time, one keyword per run:

```python
from apify_client import ApifyClient

client = ApifyClient(APIFY_TOKEN)
run = client.actor("data_xplorer/google-trends-fast-scraper").call(run_input={
    "mode": "keyword",
    "keyword": "chatgpt",
    "predefinedTimeframe": "today 3-m",  # now 1-h | now 4-h | now 1-d | now 7-d | today 1-m | today 3-m | today 12-m | today 5-y
    "geo": "US",                         # country code, "" for worldwide
    "fetchRegionalData": True,           # adds region_data
})
item = next(client.dataset(run["defaultDatasetId"]).iterate_items())
series = item["timeline_data"]["chatgpt"]   # {"2026-11-15": 49, ...}, values 0-100
regions = item["region_data"]               # [{"rank": 1, "region": "California", "value": 100}, ...]
```

Trending searches:

```python
run = client.actor("data_xplorer/google-trends-fast-scraper").call(run_input={
    "mode": "trending",
    "trendingSearchesCountry": "US",   # 125 countries
    "trendingSearchesTimeframe": "24", # "4" | "24" | "48" | "168" hours
    "trendingSearchesMaxItems": 25,
})
item = next(client.dataset(run["defaultDatasetId"]).iterate_items())
for s in item["trending_searches"]:
    print(s["rank"], s["term"], s["trend_volume"], s["related_terms"][:3])
```

## Things to know

- `keyword` takes a single search term. A comma inside it is treated as part of the term, not as a list. Run one call per keyword.
- Each series is scaled 0-100 on its own peak, so values of two separate calls are not comparable in absolute volume.
- `timeline_data` can contain an `isPartial` key next to the keyword: ignore it when reading the series.
- When no series can be returned, the item has an `error` field instead, in plain words. For a keyword with too few searches it reads "Not enough search volume on Google Trends for ... Try a longer period or a wider area." (Actor v2.11+, returned within seconds).
- Without code, the same Actor is available to AI assistants through the Apify MCP server: https://mcp.apify.com
