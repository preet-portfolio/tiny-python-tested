"""Lay out each chapter the way the author's tests expect, and bundle it for the web.

build/<chapter>/ holds test.py (upstream, untouched), its input files, the solution and
the scenario tests side by side, so ``pytest test.py`` works with a real subprocess.
"""

from __future__ import annotations

import json
import shutil
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "chapters"
UPSTREAM = ROOT / "upstream"
BUILD = ROOT / "build"


def chapters() -> list[dict]:
    """Every chapter manifest, in book order."""
    out = []
    for manifest in sorted(CHAPTERS.glob("*/chapter.json")):
        data = json.loads(manifest.read_text())
        data["_dir"] = manifest.parent
        out.append(data)
    return out


def stage(ch: dict, program_source: Path | None = None) -> Path:
    """Copy one chapter into build/<id>/ and return that directory."""
    dest = BUILD / ch["id"]
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    up = UPSTREAM / ch["id"]
    for name in ch["upstream_tests"] + ch.get("inputs", []):
        src = up / name
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)
    for name in ch["scenario_tests"] + ch.get("extra_tests", []) + ch.get("chapter_files", []):
        shutil.copy2(ch["_dir"] / name, dest / name)
    shared = BUILD / "inputs"
    shared.mkdir(parents=True, exist_ok=True)
    for name in ch.get("shared_inputs", []):
        shutil.copy2(UPSTREAM / "inputs" / name, shared / name)
    prog = dest / ch["program"]
    shutil.copy2(program_source or ch["_dir"] / ch["program"], prog)
    prog.chmod(prog.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return dest


def bundle(ch: dict) -> dict:
    """Everything the browser needs for one chapter, as text."""
    d: Path = ch["_dir"]
    up = UPSTREAM / ch["id"]
    files: dict[str, str] = {}
    for name in ch["upstream_tests"]:
        files[name] = (up / name).read_text()
    for name in ch.get("inputs", []):
        p = up / name
        paths = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
        for x in paths:
            files[str(x.relative_to(up))] = x.read_text()
    for name in ch["scenario_tests"] + ch.get("chapter_files", []):
        files[name] = (d / name).read_text()
    # Paths are relative to the chapter folder, as the tests use them.
    for name in ch.get("shared_inputs", []):
        files[f"../inputs/{name}"] = (UPSTREAM / "inputs" / name).read_text()
    meta = {k: v for k, v in ch.items() if not k.startswith("_")}
    return {
        **meta,
        "files": files,
        "starter": (d / "starter.py").read_text(),
        "reference": (d / ch["program"]).read_text(),
        "book": (d / ch["book_program"]).read_text() if ch.get("book_program") else None,
    }


def main() -> None:
    """Stage every chapter; with --web DIR also write the browser bundles."""
    web = sys.argv[sys.argv.index("--web") + 1] if "--web" in sys.argv else None
    index = []
    for ch in chapters():
        stage(ch)
        if web:
            out = Path(web) / "chapters"
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{ch['id']}.json").write_text(json.dumps(bundle(ch)))
            index.append({k: ch[k] for k in ("id", "number", "title", "program", "mechanic")})
    if web:
        runtime = Path(web) / "runtime"
        runtime.mkdir(parents=True, exist_ok=True)
        pkg = {p.name: p.read_text() for p in sorted((ROOT / "tptl").glob("*.py"))}
        (runtime / "tptl.json").write_text(json.dumps(pkg))
        (Path(web) / "chapters" / "index.json").write_text(json.dumps(index, indent=1))
    print(f"staged {len(chapters())} chapter(s) in {BUILD}")


if __name__ == "__main__":
    main()
