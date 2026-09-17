# DSA 405 P2 — Nasdaq Symbol Directory audit and clean

Course: **DSA 405-002 Data Wrangling and Web Scraping**, NC State, Fall 2026 (Prof. Jonathan Holt).

This repository is the P2 milestone of a larger question from P1: *does a monthly top-10 momentum strategy built from Nasdaq’s 100 highest-volume names beat buy-and-hold on the S&P 500 over ~30 years?*

**P2 uses only one source:** the Nasdaq Symbol Directory. Price history, yfinance, joins, and backtests are deferred to **P3**.

## Data origin

- Publisher: Nasdaq, Inc. (Nasdaq Trader)
- File: Nasdaq Symbol Directory (`nasdaqtraded.txt`)
- URL: https://www.nasdaqtrader.com/dynamic/symdir/nasdaqtraded.txt
- Format: pipe-separated text (`sep="|"`)
- License / use: Nasdaq states the data is for internal non-commercial use unless separately licensed. This repo is an educational class project.
- Snapshot in `data/raw/nasdaqtraded.txt` is unmodified. The last line of the file is a Nasdaq “File Creation Time” stamp (this copy: `0917202614:03` → 2026-09-17 14:03 as printed).

Field definitions were cross-checked against Nasdaq’s [Symbol Directory Definitions](https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs). That page documents `nasdaqlisted.txt` and `otherlisted.txt`, not `nasdaqtraded.txt` itself. The combined file’s extra columns and extra exchange codes are treated as documentation gaps in the notebook.

## How to run

1. Use Python 3.10+ (developed on 3.12).
2. From the repo root:

```bash
python3 -m pip install -r requirements.txt
jupyter notebook DSA405_002_FA26_P2_UNITY_ID.ipynb
```

3. Restart the kernel and run all cells top to bottom.

The notebook **reads** `data/raw/nasdaqtraded.txt` and **writes only** under `data/processed/`. It will refuse to start if the raw file is missing. It never writes into `data/raw/`.

If you need a fresh Nasdaq snapshot (not required for grading this copy):

```bash
python3 scripts/fetch_nasdaqtraded.py --force
```

That script is the only HTTP fetch. It sends an identifying educational user-agent. Do not point any cleaning code at `data/raw/`.

## Outputs

| Path | What it is |
| --- | --- |
| `data/raw/nasdaqtraded.txt` | Unmodified Nasdaq pull |
| `data/processed/nasdaq_symbol_directory_clean.csv` | All real securities, types repaired, names trimmed, codes decoded |
| `data/processed/nasdaq_symbol_directory_analysis.csv` | Analysis universe: Nasdaq-traded and not a test issue |
| `data/processed/cleaning_log.csv` | The 10–20 cleaning decisions with counts |
| `data/processed/row_column_accounting.csv` | Before/after row and column counts |
| `data/processed/file_metadata.json` | Source URL, raw sha256, file-creation timestamp |

## TODO before Moodle submit (Riley)

The notebook filename uses a **placeholder** Unity ID:

`DSA405_002_FA26_P2_UNITY_ID.ipynb`

**Riley: replace `UNITY_ID` with your real NC State Unity ID in the filename before submitting to Moodle.** Do not invent one in git. Also paste the repo link on Moodle as required by the P2 handout. This agent will not submit to Moodle.

## What this milestone is not

- Not a yfinance pull
- Not a price join
- Not a backtest
- Not a Moodle submission
