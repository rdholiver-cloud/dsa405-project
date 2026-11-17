#!/usr/bin/env python3
"""Restore the raw Nasdaq file and the Yahoo cache for the P4 notebook.

The Nasdaq Symbol Directory snapshot is committed at data/raw/nasdaqtraded.txt.
The Yahoo cache zip is not in git (about 87 MB compressed, 502 MB uncompressed).
If the zip is already present, or the extracted files already match the
committed manifest, this script stays offline and only verifies hashes.

If the zip is missing, the script tries the class Google Drive link. As of
2026-11-17 that file was not publicly shared, so the download is expected to
fail unless the owner later shares it. Place the zip yourself or pass --zip
PATH. This script never changes Drive sharing and never contacts Yahoo.

Usage (from the repo root):

    python scripts/get_data.py
    python scripts/get_data.py --zip /path/to/DSA405_P3_yahoo_cache_2026-11-05.zip
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW = REPO_ROOT / "data" / "raw"
YAHOO_RAW = RAW / "yahoo"

NASDAQ_PATH = RAW / "nasdaqtraded.txt"
NASDAQ_SHA256 = "61eaccdf817442beaceada8ce5fc0a84f8c4db865564d8a474e7dea9189318d0"

CACHE_ZIP_NAME = "DSA405_P3_yahoo_cache_2026-11-05.zip"
CACHE_ZIP = RAW / CACHE_ZIP_NAME
CACHE_ZIP_SHA256 = "656dff59e9feb7d108bfe5fca87a95648e91ca9d6fa27b73df6555c0c9ec5c7f"
CACHE_DRIVE_ID = "1V8y-qF7jM2aOFJIyZxxBLP0QUMa5VuDN"
CACHE_DRIVE_URL = f"https://drive.google.com/uc?export=download&id={CACHE_DRIVE_ID}&confirm=t"

MANIFEST_PATH = RAW / "DSA405_P3_yahoo-cache-manifest.json.gz"
MANIFEST_SHA256 = "848703115237a4b08bc31fe8e1b71377f04f7149d03192ca3c4adac34af678ef"

USER_AGENT = (
    "DSA405-002-FA26-NCSU-student/1.0 "
    "(educational non-commercial class project; "
    "Riley Hoover; rdh.oliver@gmail.com)"
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_hash(path: Path, expected: str, label: str) -> None:
    actual = file_sha256(path)
    if actual != expected:
        raise SystemExit(
            f"{label} sha256 mismatch for {path}.\n"
            f"  expected {expected}\n"
            f"  actual   {actual}"
        )


def load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        raise SystemExit(
            f"Missing cache manifest: {MANIFEST_PATH}. "
            "It should be committed in the repo."
        )
    require_hash(MANIFEST_PATH, MANIFEST_SHA256, "Cache manifest")
    return json.loads(gzip.decompress(MANIFEST_PATH.read_bytes()))


def missing_cache_files(manifest: dict) -> list[str]:
    missing = []
    for name, (size, sha) in manifest.items():
        target = YAHOO_RAW / name
        if (
            not target.is_file()
            or target.stat().st_size != size
            or file_sha256(target) != sha
        ):
            missing.append(name)
    return missing


def ensure_nasdaq() -> None:
    if not NASDAQ_PATH.is_file():
        raise SystemExit(
            f"Missing {NASDAQ_PATH}. This snapshot is committed in the repo "
            "and should not be replaced with a fresh Nasdaq download "
            "(a new download would be a different day's file)."
        )
    require_hash(NASDAQ_PATH, NASDAQ_SHA256, "Nasdaq Symbol Directory")
    print(f"Nasdaq file ok: {NASDAQ_PATH}")
    print(f"  sha256 {NASDAQ_SHA256}")


def looks_like_html_login(path: Path) -> bool:
    with path.open("rb") as stream:
        head = stream.read(1024).lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html") or b"service-login" in head or b"accounts.google.com" in head


def download_drive_zip(destination: Path) -> bool:
    """Try the public Drive URL. Return True on a successful hash-checked write."""
    print("Trying the class Drive link for the Yahoo cache zip.")
    print(f"  {CACHE_DRIVE_URL}")
    tmp = destination.with_suffix(destination.suffix + ".download.tmp")
    request = Request(CACHE_DRIVE_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=120) as response:
            content_type = (response.headers.get("Content-Type") or "").lower()
            final_url = response.geturl()
            if "accounts.google.com" in final_url or "service-login" in final_url:
                print(
                    "Drive redirected to a sign-in page. The file is not "
                    "publicly shared."
                )
                return False
            if "text/html" in content_type:
                print(
                    "Drive returned an HTML page instead of the zip. The file "
                    "is probably not publicly shared."
                )
                return False
            with tmp.open("wb") as target:
                shutil.copyfileobj(response, target)
    except HTTPError as exc:
        print(f"Drive download failed with HTTP {exc.code}.")
        return False
    except URLError as exc:
        print(f"Drive download failed: {exc.reason}")
        return False
    if looks_like_html_login(tmp) or tmp.stat().st_size < 1024 * 1024:
        print(
            "Download does not look like the cache zip (HTML or too small). "
            "The Drive file is not publicly shared, or the link is wrong."
        )
        tmp.unlink(missing_ok=True)
        return False
    actual = file_sha256(tmp)
    if actual != CACHE_ZIP_SHA256:
        print(
            "Downloaded file failed the sha256 check. Leaving it uninstalled.\n"
            f"  expected {CACHE_ZIP_SHA256}\n"
            f"  actual   {actual}"
        )
        tmp.unlink(missing_ok=True)
        return False
    tmp.replace(destination)
    print(f"Downloaded and verified {destination}")
    return True


def explain_private_drive() -> str:
    return (
        "The Yahoo cache zip was not found locally, and the class Drive file\n"
        f"  https://drive.google.com/file/d/{CACHE_DRIVE_ID}/view\n"
        "is not publicly shared, so this script cannot fetch it for you.\n"
        f"Place a copy of {CACHE_ZIP_NAME} at:\n"
        f"  {CACHE_ZIP}\n"
        "or re-run with --zip PATH. The expected sha256 is:\n"
        f"  {CACHE_ZIP_SHA256}\n"
        "The owner of the class Drive folder would need to share that file\n"
        "with anyone who has the link before a stranger can download it\n"
        "automatically. This script does not change Drive sharing and does\n"
        "not contact Yahoo."
    )


def install_zip_from(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"--zip path does not exist: {path}")
    require_hash(path, CACHE_ZIP_SHA256, "Yahoo cache zip")
    CACHE_ZIP.parent.mkdir(parents=True, exist_ok=True)
    if path.resolve() != CACHE_ZIP.resolve():
        shutil.copy2(path, CACHE_ZIP)
        require_hash(CACHE_ZIP, CACHE_ZIP_SHA256, "Copied Yahoo cache zip")
        print(f"Copied zip to {CACHE_ZIP}")
    else:
        print(f"Cache zip already in place: {CACHE_ZIP}")


def extract_missing(manifest: dict, missing: list[str]) -> None:
    require_hash(CACHE_ZIP, CACHE_ZIP_SHA256, "Yahoo cache zip")
    YAHOO_RAW.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(CACHE_ZIP) as archive:
        names = set(archive.namelist())
        if names != set(manifest):
            raise SystemExit(
                "Unexpected cache zip contents; stopped before extraction. "
                f"zip has {len(names)} entries, manifest has {len(manifest)}."
            )
        for member in archive.infolist():
            name = member.filename
            if (
                member.is_dir()
                or Path(name).name != name
                or "/" in name
                or "\\" in name
                or not name.endswith(".json")
            ):
                raise SystemExit(f"Unsafe cache zip member: {name}")
        print(f"Extracting {len(missing)} of {len(manifest)} cache files.")
        for name in missing:
            target = YAHOO_RAW / name
            staged = target.with_suffix(target.suffix + ".bootstrap.tmp")
            with archive.open(name) as source, staged.open("wb") as sink:
                shutil.copyfileobj(source, sink)
            size, sha = manifest[name]
            if staged.stat().st_size != size or file_sha256(staged) != sha:
                staged.unlink(missing_ok=True)
                raise SystemExit(f"Restored cache file failed verification: {name}")
            staged.replace(target)


def ensure_raw_data(zip_path: Path | None = None) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    ensure_nasdaq()
    manifest = load_manifest()
    print(f"Cache manifest ok ({len(manifest)} files).")

    if zip_path is not None:
        install_zip_from(zip_path)

    missing = missing_cache_files(manifest)
    if not missing:
        print(
            f"All {len(manifest)} cached Yahoo files already match the "
            "manifest. Zip download and extraction skipped (offline)."
        )
        return

    print(f"{len(missing)} of {len(manifest)} cache files are missing or changed.")
    if not CACHE_ZIP.is_file():
        if not download_drive_zip(CACHE_ZIP):
            raise SystemExit(explain_private_drive())
    else:
        require_hash(CACHE_ZIP, CACHE_ZIP_SHA256, "Yahoo cache zip")
        print(f"Cache zip ok: {CACHE_ZIP}")

    extract_missing(manifest, missing)
    still_missing = missing_cache_files(manifest)
    if still_missing:
        raise SystemExit(
            f"Cache still incomplete after extraction ({len(still_missing)} files)."
        )
    print(f"Restored and verified {len(manifest)} cached Yahoo files. No Yahoo requests.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--zip",
        dest="zip_path",
        type=Path,
        default=None,
        help="Path to DSA405_P3_yahoo_cache_2026-11-05.zip if it is not already in data/raw/.",
    )
    args = parser.parse_args()
    ensure_raw_data(zip_path=args.zip_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
