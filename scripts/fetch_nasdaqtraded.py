#!/usr/bin/env python3
"""One-time download of the Nasdaq Symbol Directory into data/raw/.

The cleaning notebook never writes to data/raw/. Run this script only to
obtain or refresh the unmodified snapshot. The committed copy is enough
for the P2 notebook to run.

Usage (from the repo root):
    python3 scripts/fetch_nasdaqtraded.py
    python3 scripts/fetch_nasdaqtraded.py --force  # overwrite the raw file
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

SOURCE_URL = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqtraded.txt"
USER_AGENT = (
    "DSA405-002-FA26-NCSU-student/1.0 "
    "(educational non-commercial class project; "
    "Riley Hoover; rdh.oliver@gmail.com)"
)
REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = REPO_ROOT / "data" / "raw" / "nasdaqtraded.txt"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite data/raw/nasdaqtraded.txt if it already exists.",
    )
    args = parser.parse_args()

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    if RAW_PATH.exists() and not args.force:
        digest = sha256_bytes(RAW_PATH.read_bytes())
        print(f"Already present: {RAW_PATH}")
        print(f"sha256: {digest}")
        print("Re-run with --force to download a newer snapshot.")
        return 0

    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()

    if b"Nasdaq Traded|" not in payload.splitlines()[0]:
        print("Download did not look like nasdaqtraded.txt; not writing.", file=sys.stderr)
        return 1

    RAW_PATH.write_bytes(payload)
    print(f"Wrote {RAW_PATH} ({len(payload)} bytes)")
    print(f"sha256: {sha256_bytes(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
