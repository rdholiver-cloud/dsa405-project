# Provenance brief (final P4 state)

Carried forward from the P2 notebook (`DSA405_002_FA26_P2_rdhoover.ipynb`, Provenance Brief cell, under 200 words) and extended for the Yahoo source added in P3. Nothing about either source changed after P3. Confirmed 2026-11-19.

## Source 1: Nasdaq Symbol Directory (from P2, punctuation lightly edited)

The Nasdaq Trader website publishes a public text file of securities that trade on Nasdaq systems. I downloaded that file once, on 17 September 2026, from a link that does not require a login. Nasdaq itself stamps a creation time on the last line; this copy says 17 September 2026 at 14:03. I left the downloaded file untouched in a raw folder. Every change lives in code and in a separate processed folder, so another person can start from the original file and undo or redo any step using the cleaning log.

This file is a snapshot of what exists now, not a history. For each security it gives the ticker, the name, the listing exchange, whether the product is an ETF, whether the symbol is only a test symbol, how many shares make a round lot, and (for companies listed on Nasdaq) whether the issuer is in good standing. It does not include prices or trading volume. Those will come from a second source in a later assignment. Nasdaq allows non-commercial internal use; this is a class project. No personal information is in the file.

File: `data/raw/nasdaqtraded.txt`, sha256 `61eaccdf817442beaceada8ce5fc0a84f8c4db865564d8a474e7dea9189318d0`. Link: https://www.nasdaqtrader.com/dynamic/symdir/nasdaqtraded.txt

## Source 2: Yahoo Finance daily chart data (P3, unchanged in P4)

Yahoo publishes daily price and volume history through the chart endpoint https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}. In P3 the project requested daily history from 1996-01-01 to 2026-10-01 (exclusive) for the 1,036 Nasdaq Global Select common stocks in the snapshot plus SPY, 1,037 requests in all, fetched between 2026-10-27 and 2026-11-05 (UTC), with a 2 second gap between requests and an identifying class-project User-Agent. Each response body and a sidecar with status, URL, fetch time and headers was saved and is kept as `DSA405_P3_yahoo_cache_2026-11-05.zip` (sha256 `656dff59e9feb7d108bfe5fca87a95648e91ca9d6fa27b73df6555c0c9ec5c7f`), restored and hash-checked by `scripts/get_data.py`. Yahoo grants no open license, and its terms restrict automated collection without permission; the cache is used for this class project only and is not for commercial reuse. No login, API key or personal data is involved. P4 reads the cache and never contacts Yahoo.

Full detail: report Section 2, `docs/data_dictionary.md`, and the README sources table.
