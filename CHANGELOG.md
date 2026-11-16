# Changelog

Updates to the [Google Trends Scraper](https://apify.com/data_xplorer/google-trends-fast-scraper?fpr=6vi1cs) Actor used by this repository. Click **Watch > Custom > Releases** at the top of the page to be notified of new ones.

## Actor v2.11 (2026-11-16)

- Keywords with too few searches now come back within seconds with a plain-words `error` field ("Not enough search volume on Google Trends for ..."), instead of retrying for over a minute and sometimes hitting the run timeout.
- When Google limits requests, the run stops cleanly before its timeout with an explanation in `error`.

## Actor v2.10 (2026-11-06)

- Trending searches work again after Google changed its Trending page on 2026-11-03.

## Actor v2.9 (2026-11-02)

- Interest by region also works worldwide: with no country set, `fetchRegionalData` returns interest by country.
- Countries with very low search volume are left out of the worldwide breakdown, as on the Google Trends website.
