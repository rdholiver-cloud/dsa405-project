# P2 ungraded self-score

Course rubric weights from the P2 handout. This is an ungraded copy for submission alongside the notebook. Scores are a student’s honest estimate, not a claim of a recorded grade.

| Criterion | Weight | Self-score (0–4) | Weighted | Notes |
| --- | --- | --- | --- | --- |
| Diagnosis & dictionary | ×2 | 4 | 8 | Dtype-as-loaded vs should-be, missingness with `dropna=False`, distinct counts, numeric min/max/range, full levels for categoricals with &lt;~30 values. Dictionary covers all 12 source fields plus derived analysis fields. Contradictions with Nasdaq docs are flagged (combined `nasdaqtraded.txt` is not defined on the Symbol Directory Definitions page; exchange codes `Q`, `F`, `M` are absent from the published other-listed allowed list). |
| Cleaning execution | ×2 | 4 | 8 | Repair over drop: ticker `NA` recovered, whitespace fixed, types cast, codes decoded. Only the non-security trailer row is removed from the full table. Test issues and the one non-traded name are kept in the full clean file and omitted only from the analysis extract. Raw file is never overwritten. |
| Cleaning log | ×3 | 4 | 12 | 18 decision rows with column, change, rows/cells affected, why (not a restatement), and what is lost. Reversible from this log plus `data/raw/nasdaqtraded.txt`. |
| Provenance | ×1 | 4 | 4 | ≤200 words, plain language, source / timestamp / what was not collected. |
| Tidy / reproducible | ×2 | 4 | 8 | Kernel restart, top-to-bottom run, pinned `requirements.txt`, raw vs processed split, notebook named `DSA405_002_FA26_P2_rdhoover.ipynb`. |
| **Total** | | | **40 / 40** | Cap at the handout’s 4-point feel per criterion. Riley should re-score after reading the notebook cold. |

## Defect classes

**Found:** trailer row treated as a record; pandas default NA eating ticker `NA`; space-as-value in Market Category; empty vs missing in CQS / Financial Status; trailing and repeated spaces in names; Y/N stored as text; round lot stored as float; undocumented listing-exchange codes.

**Checked and not found:** duplicate symbols, non-ASCII names, mixed-case tickers, negative or fractional lots (other than the float artifact), Market Category or Financial Status filled on non-Nasdaq listings, ETF=`N` with “ETF” in the name, blank security names, personal data.
