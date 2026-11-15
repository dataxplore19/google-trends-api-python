# Changelog

Updates to the [Google Trends Scraper](https://apify.com/data_xplorer/google-trends-fast-scraper) Actor used by this repository. Click **Watch > Custom > Releases** at the top of the page to be notified of new ones.

## Actor v2.10 (2026-11-06)

- Trending searches work again after Google changed its Trending page on 2026-11-03.

## Actor v2.9 (2026-11-02)

- Interest by region also works worldwide: with no country set, `fetchRegionalData` returns interest by country.
- Countries with very low search volume are left out of the worldwide breakdown, as on the Google Trends website.
