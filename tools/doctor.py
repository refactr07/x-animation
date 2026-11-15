#!/usr/bin/env python3
"""Is everything this repo needs in place?

    ./x doctor

Checks the toolchain, the fonts, the backdrops and Remotion's list of sections, and says what to do
about anything that is missing. It does not render; ./x parity is the test that the two engines agree.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version

from xcore.paths import FONTS, PUBLIC, ROOT, VIDEOS, studio
from xcore.tokens import BACKDROPS, TOKENS

rows: list[tuple[str, bool, str]] = []


def add(name: str, ok: bool, detail: str) -> None:
    rows.append((name, ok, detail))


def tool(name: str, args: list[str], hint: str) -> None:
    path = shutil.which(name)
    if not path:
        add(name, False, hint)
        return
    out = subprocess.run([name, *args], capture_output=True, text=True)
    first = (out.stdout or out.stderr).strip().splitlines()
    add(name, True, first[0][:70] if first else path)


def pkg(name: str, want: str | None = None, optional: str = "") -> None:
    try:
        v = version(name)
        add(name, want is None or v == want, v + ("" if want in (None, v) else f" (this repo pins {want}: uv sync)"))
    except PackageNotFoundError:
        if optional:
            rows.append((name, True, f"not installed (optional: {optional})"))
        else:
            add(name, False, "missing: uv sync")


def main() -> None:
    add("python", sys.version_info >= (3, 11), sys.version.split()[0])
    tool("uv", ["--version"], "brew install uv")
    pkg("manim", "0.22.1")
    pkg("typst")
    pkg("faster-whisper", optional="./x setup --voice, needed only for ./x align")
    tool("ffmpeg", ["-version"], "brew install ffmpeg")
    tool("ffprobe", ["-version"], "brew install ffmpeg")
    tool("node", ["--version"], "nvm install 24")

    modules = ROOT / "node_modules"
    package = json.loads((ROOT / "package.json").read_text())
    want = package["dependencies"]["remotion"]
    got = {}
    for dep in package["dependencies"]:
        f = modules / dep / "package.json"
        if f.exists() and (dep == "remotion" or dep.startswith("@remotion/")):
            got[dep] = json.loads(f.read_text())["version"]
    if not got:
        add("remotion", False, "node_modules is missing: npm ci")
    else:
        odd = {d: v for d, v in got.items() if v != want}
        add("remotion", not odd, f"{want}, {len(got)} packages" if not odd else f"mixed versions {odd}: npm run upgrade")
    shell = list((modules / ".remotion").rglob("chrome-headless-shell*")) if (modules / ".remotion").exists() else []
    add("headless browser", bool(shell), "installed" if shell else "missing: npx remotion browser ensure")

    files = [f for group in TOKENS["font"]["files"].values() for f in group.values()]
    missing = [f for f in files if not (FONTS / f).exists()]
    add("fonts", not missing, f"{len(files)} faces in public/fonts" if not missing else f"missing {missing}")

    made = len(list((PUBLIC / "backdrops").glob("*.png"))) if (PUBLIC / "backdrops").exists() else 0
    # never a fault: a render draws the backdrop it needs; ./x backdrops draws them all (for Studio)
    add("backdrops", True, f"{made} of {len(BACKDROPS['styles']) * 3} drawn (renders draw what they need; ./x backdrops draws all)")

    check = subprocess.run([sys.executable, str(ROOT / "tools" / "registry.py"), "--check"], capture_output=True, text=True)
    add("section registry", check.returncode == 0, "up to date" if check.returncode == 0 else "out of date: ./x sync")

    active = studio().get("active_video")
    sections = len(list(VIDEOS.glob("*/*/beats.json")))
    add("videos", True, f"{sections} sections; active video: {active or 'none (./x new starts one)'}")

    width = max(len(r[0]) for r in rows)
    for name, ok, detail in rows:
        print(f"  {'ok  ' if ok else 'FIX '} {name:<{width}}  {detail}")
    bad = [r for r in rows if not r[1]]
    print(f"\nDOCTOR: {'all good' if not bad else str(len(bad)) + ' thing(s) to fix'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
