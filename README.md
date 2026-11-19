# DSA 405 P4: does a Nasdaq momentum rule beat the S&P 500?

Course: DSA 405-002 Data Wrangling and Web Scraping, NC State, Fall 2026 (Prof. Jonathan Holt). Author: Riley Hoover (rdhoover), solo project, Tier 1, no stretch component.

## What the project is and what it found

The question has remained unchanged since P1: does a monthly top-10 momentum strategy, selected from Nasdaq's 100 highest-volume stocks, outperform buy-and-hold on the S&P 500 (SPY) over roughly 30 years? Because the Nasdaq Symbol Directory lacks a volume column, the project obtained Yahoo Finance price history for 1,036 Nasdaq Global Select common stocks plus SPY, ranks the stocks each month by average daily dollar volume, retains the top 100, and buys the 10 with the highest 12-month return. P4 repeats that analysis using the saved raw data and adds evaluations of how reliable the results are.

On the headline run (February 1997 to September 2026, 356 months, no trading costs) $1 became $736.22 for the rule (24.9% a year) and $16.18 for SPY (9.8% a year). The rule outperformed SPY in 60.1% of the months and had far greater volatility (36.7% a year versus 15.3%). A paired bootstrap of the yearly growth differential produced a 5th to 95th percentile interval of +4.2 to +26.4 percentage points, and the rule came out ahead in 99.0% of the resamples. That interval assumes the months are independent, so it is rough. The outcome is also skewed upward by survivorship: the stock list is today's Nasdaq directory, so firms that were delisted along the way are missing. Think of the differential as an upper bound on what a real investor would have earned. All figures are in `results/findings.csv`.

Other checks: 21 monthly returns were flagged as anomalous (above +300%), including CHRD in November 2020 at about +30,991%, whose cause is not established. None of the 21 sat inside a held portfolio when it was earned, so the headline is unaffected by eliminating CHRD alone. Removing all 21 jumps raised the rule's final wealth to $822.40, and capping them at +300% gave $764.30. We suspect, but did not test, that the jumps boosted 12-month momentum and pulled the rule into names that then gave the gains back. Six tickers (INDV, MGPI, NATH, QRVO, SLP, WBD) could not be parsed from the cache and are absent from the price table.

## Data sources, links and licenses

| Source | Producer and link | Terms |
| --- | --- | --- |
| Nasdaq Symbol Directory, `nasdaqtraded.txt` | Nasdaq, Inc. (Nasdaq Trader). File: https://www.nasdaqtrader.com/dynamic/symdir/nasdaqtraded.txt. Field definitions: https://www.nasdaqtrader.com/Trader.aspx?id=symboldirdefs | Nasdaq states the data is for internal, non-commercial use unless separately licensed. This repo is an educational class project and holds one unmodified snapshot (file creation stamp 2026-09-17 14:03, sha256 `61eaccdf817442beaceada8ce5fc0a84f8c4db865564d8a474e7dea9189318d0`). |
| Yahoo Finance daily chart data | Yahoo. Endpoint: https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}. Terms: https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html | There is no open data license. Yahoo's terms restrict automated collection without permission. The pull (P3, finished 2026-11-05) was approved by the student for this class project only. That is not express permission from Yahoo. Do not reuse the cache commercially or redistribute it publicly. |

The Yahoo responses are stored as a cache zip outside git (see below). P4 never contacts Yahoo.

## How to run

1. Use Python 3.13 (the recorded run used 3.13.5). Python 3.11 or later should work but is untested.
2. Clone the repo. The submission branch is `main` (the P4 work was built on `p4-synthesis` and merged into `main` through PR #1):

```bash
git clone https://github.com/rdholiver-cloud/dsa405-project.git
cd dsa405-project
```
3. Create an environment and install the pinned packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

4. Get the Yahoo cache. It is approximately 87 MB zipped and 502 MB unzipped, so it is not in git. The zip is `DSA405_P3_yahoo_cache_2026-11-05.zip` (sha256 `656dff59e9feb7d108bfe5fca87a95648e91ca9d6fa27b73df6555c0c9ec5c7f`). Place it in `data/raw/` or pass its path:

```bash
python scripts/get_data.py                       # tries the class Google Drive link, then a GitHub Release copy if one is published
python scripts/get_data.py --zip /path/to/DSA405_P3_yahoo_cache_2026-11-05.zip
```

The script checks the Nasdaq file hash, checks the committed manifest (`data/raw/DSA405_P3_yahoo-cache-manifest.json.gz`, 2,076 files with sizes and sha256), checks the zip hash, unzips into `data/raw/yahoo/`, and checks every unzipped file. The script downloads the zip from the class Google Drive file, which is shared so anyone with the link can download it. If a GitHub Release copy (tag `p4-yahoo-cache`) has been published on this repo, the script tries that next, with the same sha256 check. If neither works, the script says so, and you can pass a local copy of the zip with `--zip <path>`. The script never changes Drive sharing and never contacts Yahoo.

**Check the findings with no download.** If the cache cannot be restored, this one command still reproduces the results from tables committed in `data/processed/`:

```bash
python scripts/reproduce_offline.py
```

It reads `data/processed/backtest_full.csv` (the 356-month headline backtest) and `data/processed/flagged_monthly_returns.csv`, recomputes the headline growth, CAGR, beat share and volatility, both bootstraps with the same seed, the three subperiods and the held-jump check, and compares all 47 values to `results/findings.csv` at the 12 significant digits the file stores. It writes `figures/offline/growth_baseline.png` and `figures/offline/subperiod_cagr.png` and exits with an error if any value differs. The three sensitivity paths and the input counts need the full monthly price panel, so the script reads those 30 rows from `results/findings.csv` and checks only that they agree with each other. Rebuilding those from raw data needs the cache and step 5.

5. Run the notebook from a clean kernel:

```bash
jupyter nbconvert --to notebook --execute --output DSA405_002_FA26_P4_rdhoover.executed.ipynb DSA405_002_FA26_P4_rdhoover.ipynb
```

The run takes about 30 seconds and writes `figures/`, `results/findings.csv`, and `data/processed/`. The notebook invokes `scripts/get_data.py` itself, so step 4 can be skipped if the zip is already in `data/raw/`. The recorded run is saved in `logs/p4_nbconvert_run.log`, and the executed notebook with all its outputs is committed.

## Repo structure

| Path | What it is |
| --- | --- |
| `DSA405_P4_Report_rdhoover.md` | The P4 written report, all nine sections |
| `DSA405_002_FA26_P4_rdhoover.ipynb` | Main P4 notebook: raw files to joined table, backtest, sensitivity checks, bootstrap, findings and figures |
| `DSA405_002_FA26_P4_rdhoover.executed.ipynb` | The same notebook after a clean nbconvert run, with outputs |
| `DSA405_002_FA26_P2_rdhoover.ipynb` | P2 audit and cleaning of the Nasdaq file, kept as the cleaning provenance |
| `scripts/get_data.py` | Hash-checked data restore (Nasdaq file, Yahoo cache zip, manifest) |
| `scripts/reproduce_offline.py` | Rebuilds and checks the headline findings and two figures from committed tables, no download |
| `scripts/fetch_nasdaqtraded.py` | P2 script that downloaded the Nasdaq snapshot. Not needed to reproduce |
| `data/raw/nasdaqtraded.txt` | Unmodified Nasdaq snapshot |
| `data/raw/DSA405_P3_yahoo-cache-manifest.json.gz` | Expected size and sha256 of every cached Yahoo file |
| `data/raw/yahoo/` | Restored Yahoo cache. Not in git |
| `data/processed/` | P2 clean tables and the P2 notebook's own 18-row `cleaning_log.csv` output (the final log is `docs/cleaning_log.csv`), plus P4 outputs: `directory.csv`, `backtest_full.csv`, `flagged_monthly_returns.csv`, `fetch_failures.csv`. The large `prices_daily.csv`, `prices_monthly.csv` and `joined_monthly.csv` are rebuilt by the notebook and not in git |
| `docs/data_dictionary.md`, `docs/cleaning_log.csv` | Data dictionary and cleaning log, updated to the final data |
| `docs/provenance.md` | Provenance brief for both sources, carried forward from P2 and updated for the Yahoo cache |
| `results/findings.csv` | Every headline number the report cites, with uncertainty figures |
| `figures/` | `growth_baseline.png`, `growth_sensitivity.png`, `subperiod_cagr.png` |
| `logs/p4_nbconvert_run.log` | Log of the recorded clean run |
| `RUBRIC_SELF_SCORE.md` | The P4 self-scored rubric. The earlier P2 version is in git history |
| `requirements.txt` | Pinned packages |

## Known limits

- Survivorship: only stocks in the 2026-09-17 directory are included.
- Six tickers did not parse and 21 returns look implausible. Both are shown, not suppressed.
- No trading costs, taxes or slippage. The rule trades 10 names a month.
- The bootstrap assumes months are independent, which they are not.
- The dollar-volume ranking uses Yahoo's split-adjusted close and volume.
