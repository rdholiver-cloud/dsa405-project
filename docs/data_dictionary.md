# Data dictionary (final P4 state)

Carried forward from the P2 notebook dictionary and updated for the P3 join and the P4 backtest outputs. Confirmed 2026-11-17. No changes were made to the meaning of the P2 Nasdaq columns after P3. P4 added analysis outputs (sensitivity scenarios, findings, figures) and did not change the headline joined table.

Source docs for the directory: Nasdaq [Symbol Directory Definitions](https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs) for `nasdaqlisted.txt` and `otherlisted.txt`. That page does not define `nasdaqtraded.txt`. The combined file mixes Nasdaq-listed columns (Market Category, Financial Status) with other-listed columns (Listing Exchange, ETF, CQS Symbol, NASDAQ Symbol). Gaps and contradictions are noted below.

Raw snapshot: `data/raw/nasdaqtraded.txt`, sha256 `61eaccdf817442beaceada8ce5fc0a84f8c4db865564d8a474e7dea9189318d0`, File Creation Time 2026-09-17 14:03 as printed in the trailer.

## 1. Nasdaq Symbol Directory (Source 1)

P2 writes the full clean table to `data/processed/nasdaq_symbol_directory_clean.csv` (13,253 securities, 16 columns) and an analysis extract to `data/processed/nasdaq_symbol_directory_analysis.csv` (13,215 Nasdaq-traded, non-test rows). P3/P4 also write a slimmer join table, `data/processed/directory.csv`, with one row per symbol after dropping the trailer and test issues (13,216 rows: 13,253 minus 37 test issues). Load processed CSVs with `dtype="string"` and `keep_default_na=False` so ticker NA (Nano Labs) is not turned into a missing value.

| Name (raw to clean) | Type | Units / levels | Missingness | Used in analysis? | Notes and documentation flags |
| --- | --- | --- | --- | --- | --- |
| Nasdaq Traded to nasdaq_traded | Y/N text as loaded; boolean after the P2 clean | Y = trades on Nasdaq systems; N = listed but not Nasdaq-traded | Should not be missing on a security row. The trailer has a timestamp instead. | Yes. Exclude N from the tradable universe. | This snapshot has exactly one N: BRK.A. Field is not defined on the Symbol Directory Definitions page (it exists only on nasdaqtraded.txt). |
| Symbol to symbol | text ticker | Typically a 1-5 character root plus optional suffix. Other-listed ACT symbols may be up to 14 characters. | A missing value after a default pandas load can mean ticker NA, not a hole in the file. | Yes. Identity / join key. | CQS-style punctuation appears on NYSE names (BRK.A, ABR$D). Not always equal to NASDAQ Symbol. Docs describe Symbol only for nasdaqlisted.txt. |
| Security Name to security_name | text | Up to 255 characters on other-listed names. | Should not be missing on a security row. | Yes. Human-readable label, and the P3 universe filter requires the text "Common Stock". | P2 stripped 74 trailing spaces and collapsed 185 repeated internal spaces. |
| Listing Exchange to listing_exchange | categorical code | A, N, P, Q, Z, V, F, M in this file. Published other-listed list is A, N, P, Z, V. Observed extras: Q = Nasdaq, F = TXSE, M = NYSE Texas (test). | Missing only on the trailer. | Yes. Nasdaq-listed vs other-listed. The P3/P4 pool keeps Q. | Q, F, and M are not on the published other-listed allowed list. F is TXSE's SIP participant ID. The docs page still uses stale names (NYSE MKT, BATS). P2 also stores listing_exchange_name. |
| Market Category to market_category | categorical code | Q = Global Select; G = Global Market; S = Capital Market; space/missing = not Nasdaq-listed. | A stored space means "not a Nasdaq listing," not an unknown tier. | Yes. The P3/P4 pool keeps Q (Global Select). | Defined for nasdaqlisted.txt. The combined file uses a space instead of leaving the field empty. P2 also stores market_category_name. |
| ETF to is_etf (P2) / etf (P3/P4 directory.csv) | Y/N text as loaded; boolean after the P2 clean; left as Y/N in the P3/P4 slim directory | Y or N | Should not be missing on a security row. | Yes. The P3/P4 pool keeps N. | Defined for otherlisted.txt, but present for Nasdaq-listed rows too. The flag is Nasdaq's, not a name parse. |
| Round Lot Size to round_lot_size | integer after the P2 clean | Shares per round lot (1, 10, 40, 100 in this snapshot) | Missing only on the trailer in a default load. | No, for the momentum study. Kept in the P2 clean table because it is in the file. | Lot 1 is BRK.A. |
| Test Issue to is_test_issue | Y/N text; boolean after the P2 clean | Y = test symbol; N = live symbol | Should not be missing on a security row. | Yes. Exclude Y. P3/P4 drop test issues before building directory.csv. | 37 test symbols in this snapshot. |
| Financial Status to financial_status | categorical code | N, D, E, Q, G, H, J, K as documented. This snapshot uses N, D, E, H only. | Empty means "not a Nasdaq-listed issuer," not Normal. | Yes. The P3/P4 pool keeps N (Normal). | Defined for nasdaqlisted.txt. Do not recode a blank to Normal. P2 also stores financial_status_name. |
| CQS Symbol to cqs_symbol | text | CTA ticker, up to 14 characters. | Blank on all Nasdaq-listed (Q) rows. Structural missing, not a failed lookup. | No, for this project. | Defined for otherlisted.txt. |
| NASDAQ Symbol to nasdaq_symbol | text | Nasdaq-protocol ticker, up to 14 characters. | Should match a real ticker; a default pandas load can blank ticker NA. | Identity toward Yahoo. P3/P4 join on `symbol` after mapping Yahoo hyphens to periods. | 518 securities have Symbol != NASDAQ Symbol, all on NYSE/NYSE American suffix names. |
| NextShares to is_nextshares | Y/N text; boolean after the P2 clean | Y or N; this snapshot is all N | Should not be missing on a security row. | No. Degenerate in this pull. | Not defined on the Symbol Directory Definitions page. |
| snapshot_at (derived, P2) | timestamp string from the trailer | This copy: 2026-09-17 14:03. Timezone is not labeled; Nasdaq Trader operates on Eastern Time. | If missing, the file was truncated. | Yes. Provenance of the universe. | Attaching it as a column on every P2 row is our choice, not Nasdaq's layout. |
| listing_exchange_name, market_category_name, financial_status_name (derived, P2) | text labels | See the matching code columns | Missing when the code is missing. | Yes, as readable filters in the P2 table. | Labels for F and M come from SIP / venue identity, not from the stale other-listed table. |

## 2. Yahoo Finance chart cache (Source 2)

Raw files live in `data/raw/yahoo/{TICKER}.json` (response body) and `{TICKER}.meta.json` (HTTP status, URL, UTC fetch time, response headers). They are restored from `DSA405_P3_yahoo_cache_2026-11-05.zip` (sha256 `656dff59e9feb7d108bfe5fca87a95648e91ca9d6fa27b73df6555c0c9ec5c7f`) using `scripts/get_data.py`. The cache was collected in P3 with `requests` against `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}`, daily interval, 1996-01-01 to 2026-10-01 exclusive (last full month is September 2026). P4 does not contact Yahoo again.

| Name | Type | Units | Notes |
| --- | --- | --- | --- |
| ticker | text | Yahoo symbol | For class shares Yahoo uses a hyphen (BRK-B) where the directory uses a period. |
| date | timestamp, tz-naive, normalized to the exchange date | calendar day | Built from the chart timestamps and the exchange time zone in the response metadata. |
| close | float | split-adjusted close, in US dollars | Yahoo's `close` in this endpoint is already split-adjusted. It is not necessarily the unadjusted print. |
| adj_close | float | split- and dividend-adjusted close, in US dollars | Used for returns and momentum. |
| volume | float or int | split-adjusted share count | Because volume is split-adjusted, ranking uses dollar volume (close times volume), not share count. |

Days with a null close, adjusted close, or volume are dropped at parse time (FISV: 1 day; PSKY: 40 days). Tickers whose cached body is missing the `timestamp` path are logged in `data/processed/fetch_failures.csv` and are not parsed: INDV, MGPI, NATH, QRVO, SLP, WBD.

## 3. Monthly prices and joined table

`data/processed/prices_monthly.csv` is one row per ticker per month. `data/processed/joined_monthly.csv` is that table left-joined to `directory.csv` on `symbol`. The headline joined table retains every flagged monthly return. The daily table is rebuilt in memory and is not kept in git (`prices_daily.csv` is about 289 MB).

| Name | Type | Units | Notes |
| --- | --- | --- | --- |
| ticker | text | Yahoo symbol | |
| month | monthly period, YYYY-MM | calendar month | Window is 1996-01 through 2026-09. |
| adj_close | float | US dollars | Month-end adjusted close (last trading day in the month). |
| volume | float | split-adjusted shares | Sum of daily volume in the month. |
| avg_dollar_volume | float | US dollars | Mean of daily close times daily volume in the month. Used for the liquidity rank. |
| trading_days | integer | days | Count of usable trading days in the month. Verification expects 1-23. |
| ret | float | decimal return | Month-to-month change in month-end adj_close. A value of 3.0 is +300%. |
| symbol | text | directory symbol | `ticker` with hyphens mapped to periods. |
| security_name, listing_exchange, market_category, etf, financial_status | text | as in directory.csv | Attached by the left join. SPY is present as the benchmark ETF. |

Verification flags monthly `ret` values outside (-100%, +300%]. There are 21 such rows. They stay in this headline table and are listed in `data/processed/flagged_monthly_returns.csv` (`ret` is decimal; `note` is a short audit comment).

## 4. Backtest and findings

`data/processed/backtest_full.csv` is the headline backtest (flagged returns kept). Each row is one holding month.

| Name | Type | Units | Notes |
| --- | --- | --- | --- |
| month | YYYY-MM | the month when the portfolio is chosen | The return earned is the next month's return. The first holding month in the headline run is February 1997, and the last is September 2026 (356 months). |
| picks | text | comma-separated tickers | The 10 names held that month. SPY is never a pick. |
| strategy_ret | float | decimal monthly return | Equal-weight mean of the 10 names' next-month returns. No costs, taxes, or slippage. |
| spy_ret | float | decimal monthly return | SPY's next-month return over the same month. |
| strategy_growth | float | growth of $1 | Cumulative product of 1 + strategy_ret, starting at the first holding month. |
| spy_growth | float | growth of $1 | Cumulative product of 1 + spy_ret. |

`results/findings.csv` holds the headline numbers and the P4 sensitivity and uncertainty summaries. Columns:

| Name | Type | Notes |
| --- | --- | --- |
| metric | text | For example `final_wealth_strategy`, `cagr_strategy`, `n_months`. |
| scenario | text | `baseline` (flags kept), `exclude_flagged` (21 jumps removed from the price path), `cap_300` (those jumps capped at +300%), `exclude_chrd_2020_11` (only the CHRD November 2020 jump removed), or a named subperiod / bootstrap label. |
| value | number | The recorded value. Rates are stored as decimals (0.249 is 24.9%). |
| unit | text | `dollars_per_1`, `decimal_per_year`, `decimal_per_month`, `months`, `share_of_months`, `count`, and similar. |
| note | text | Short definition of the metric or scenario. |

Sensitivity method (P4, 2026-11-17): for each treated ticker-month, later adjusted closes of that ticker are rescaled so the treated month's return equals 0 (exclude) or +300% (cap). Later month-to-month returns are unchanged. The jump is also removed from later 12-month momentum. The headline `joined_monthly.csv` is not rewritten by this step.
