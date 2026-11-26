"""Download the book's texts that this repository can't share (see upstream/unshared.json).

The book's repository is MIT licensed, but a few of its input files are other people's
work. They stay out of this repository and the site. CI and local runs fetch them from a
fixed commit and refuse any file whose SHA-256 differs.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

UPSTREAM = Path(__file__).resolve().parents[1] / "upstream"


def manifest() -> dict:
    """The list in upstream/unshared.json."""
    return json.loads((UPSTREAM / "unshared.json").read_text())


def paths() -> set[str]:
    """Upstream-relative paths of the unshared files."""
    return {f["path"] for f in manifest()["files"]}


def fetch() -> None:
    """Download each file that's missing, and check every file's hash."""
    m = manifest()
    for f in m["files"]:
        dest = UPSTREAM / f["path"]
        if not dest.exists():
            url = f"{m['base']}/{m['commit']}/{f['path']}"
            with urllib.request.urlopen(url, timeout=30) as r:  # noqa: S310 (fixed https URL)
                data = r.read()
            if hashlib.sha256(data).hexdigest() != f["sha256"]:
                raise SystemExit(f"{f['path']}: downloaded file doesn't match its SHA-256")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        if hashlib.sha256(dest.read_bytes()).hexdigest() != f["sha256"]:
            raise SystemExit(f"{f['path']}: file on disk doesn't match its SHA-256")
        print(f"ok {f['path']}")


if __name__ == "__main__":
    fetch()
