# Google Trends API for Python (pytrends alternative)

Get Google Trends data in Python without getting blocked: interest over time, interest by region and daily trending searches, saved to CSV. Works as a drop-in replacement for pytrends, which is no longer maintained and often fails with HTTP 429 errors.

Google has no official public Google Trends API. This script gets the data through the [Google Trends Scraper](https://apify.com/data_xplorer/google-trends-fast-scraper) Actor on Apify. The Actor handles Google's rate limits and proxies, so your code only sends a keyword and receives JSON.

> Click **Watch > Custom > Releases** at the top of this page to be notified when the Actor gets new features. See the [changelog](CHANGELOG.md).

## Video

[![Google Trends Scraper: Trending Searches and Keyword Trends as Clean Data](https://img.youtube.com/vi/jOgshmxVvWk/maxresdefault.jpg)](https://www.youtube.com/watch?v=jOgshmxVvWk)

*Video: how the Google Trends Scraper works.*

## What you can do

| Task | Command | Output |
| --- | --- | --- |
| Interest over time for keywords | `python trends.py interest chatgpt gemini --geo US` | `interest_over_time.csv` |
| Interest by region (states, regions) | `python trends.py interest bitcoin --geo US --regions` | `interest_by_region.csv` |
| Today's trending searches in a country | `python trends.py trending --country GB` | `trending_history.csv` |
| Alert when a word starts trending | `python trends.py trending --country US --watch "bitcoin,nvidia"` | Telegram message |

## Quick start

You need Python 3.9+ and an [Apify](https://apify.com) account (the free plan includes monthly credits).

```bash
git clone https://github.com/dataxplore19/google-trends-api-python.git
cd google-trends-api-python
pip install -r requirements.txt
export APIFY_TOKEN="your_apify_token"
python trends.py interest chatgpt gemini --geo US --timeframe "today 3-m"
```

Telegram alerts are optional. Without these two variables, alerts are printed to the console.

```bash
export TELEGRAM_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

## Interest over time

```bash
python trends.py interest chatgpt gemini --geo US --timeframe "today 3-m" --regions
```

Console:

```
chatgpt: peak 100 on 2026-09-03, latest 50 on 2026-11-15 (day data)
gemini: peak 100 on 2026-10-08, latest 61 on 2026-11-15 (day data)
186 rows written to interest_over_time.csv
102 rows written to interest_by_region.csv
```

`interest_over_time.csv`:

```csv
date,keyword,value
2026-08-15,chatgpt,48
2026-08-16,chatgpt,47
```

`interest_by_region.csv`:

```csv
keyword,rank,region,value
chatgpt,1,California,100
chatgpt,2,Georgia,90
```

Options:

- `--geo`: country code (`US`, `GB`, `FR`, `DE`...). Leave it out for worldwide.
- `--timeframe`: `now 1-h`, `now 4-h`, `now 1-d`, `now 7-d`, `today 1-m`, `today 3-m`, `today 12-m` (default) or `today 5-y`. Short periods return hourly points, long periods daily or weekly points.
- `--regions`: also save interest by region.

Each keyword is fetched in its own request, so each series is scaled from 0 to 100 on its own peak. To compare the shape of two keywords this is fine; to compare their absolute volume, use the Google Trends website with both keywords in one chart.

## Trending searches

```bash
python trends.py trending --country FR --max 8 --watch "portugal"
```

```
  1. portugal – danemark (50K+)
Google Trends FR: 'portugal – danemark' is trending (50K+), matches portugal
  2. raoul chichin (20K+)
  3. algérie – togo (50K+)
```

- `--country`: 125 countries are supported (`US`, `GB`, `IN`, `BR`, `JP`...).
- `--hours`: trends of the last `4`, `24` (default), `48` or `168` hours.
- `--watch`: comma-separated words. You get an alert when a trending search or one of its related queries contains one of them.
- `--alert-new`: alert on every trending search that was not in earlier runs.

Every run is appended to `trending_history.csv` with the rank, the search volume and the related queries, so you build your own history of what trended and when.

## Run it on a schedule

With cron, trending searches every hour:

```bash
0 * * * * cd /path/to/google-trends-api-python && APIFY_TOKEN=your_apify_token /usr/bin/python3 trends.py trending --country US --watch "your brand"
```

## Use the data in pandas

```python
import pandas as pd

df = pd.read_csv("interest_over_time.csv", parse_dates=["date"])
df.pivot(index="date", columns="keyword", values="value").plot()
```


## Other languages

Prefer JavaScript? The same tool for Node.js: [google-trends-api-node](https://github.com/dataxplore19/google-trends-api-node).

For AI assistants (Claude, Cursor, VS Code): the [google-trends-mcp-server](https://github.com/dataxplore19/google-trends-mcp-server) MCP server. Without code, in n8n: [n8n templates](https://github.com/dataxplore19/n8n-google-trends-news-templates).

## FAQ

### Is there an official Google Trends API?

Google announced an official Trends API in 2025, in alpha with access on request only. For most people the options are the Google Trends website, unofficial libraries like pytrends, or a hosted scraper like the one this script uses.

### Why does pytrends return a 429 error?

Google limits how many requests one IP address can send to Google Trends. pytrends sends them from your own IP, so you hit the limit quickly, especially from a server. The Actor used here sends requests through rotating proxies and retries for you.

### How do I get Google Trends data for many keywords?

Pass them all to `interest`: `python trends.py interest kw1 kw2 kw3 ...`. Each keyword runs in turn and all series end up in the same CSV.

### Can I get Google Trends data by city or state?

Yes. `--regions` returns interest by region of the country set with `--geo` (US states for `--geo US`).

### Can I use it from n8n, Make or another language?

Yes. The Actor is a plain HTTP API. See the [API tab of the Actor](https://apify.com/data_xplorer/google-trends-fast-scraper/api) for JavaScript, cURL and other examples.

### Can an AI agent use it?

Yes. See [AGENTS.md](AGENTS.md). The Actor is also available to AI assistants through the [Apify MCP server](https://mcp.apify.com).

## Disclosure

I am the author of the Google Trends Scraper Actor used by this script.

## License

MIT
