# Verification notes, 2026-11-17

Clean-clone test: the repo was cloned from the local p4-synthesis branch into a new folder, a new virtual environment was built from requirements.txt (Python 3.13.5), the Yahoo cache was restored with `python scripts/get_data.py --zip <local copy>` (2,076 of 2,076 files verified against the manifest), and the notebook was run with nbconvert. It finished with no errors in about 26 seconds. `results/findings.csv` and `data/processed/backtest_full.csv` were byte-identical to the original run.

Without a local copy of the cache zip, `python scripts/get_data.py` stops with instructions, because the class Drive file is not publicly shared.

Secret scan: all commits on every local and remote-tracking branch were searched for GitHub tokens (ghp_, github_pat_), sk- keys, AWS keys (AKIA), Google API keys (AIza), Slack tokens (xox), Bearer tokens, private key headers, and key=value assignments for api key, secret, token and password, including notebook outputs. No matches. No files named like .env, .pem, id_rsa, secret, token or credential appear in history. The largest blob in history is about 2 MB. The notebook and scripts do contain the student's contact email in the User-Agent string, as in P2.
