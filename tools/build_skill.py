#!/usr/bin/env python3
"""Build the refactr-animation-1 skill from this repository, so the skill and the studio never drift.

    ./x skill                 build dist/refactr-animation-1/ and dist/refactr-animation-1.skill
    ./x skill --install       also install it to ~/.claude/skills/refactr-animation-1

The skill is this repo's .claude/skills/refactr-animation-1 (SKILL.md and scripts/) plus a snapshot
of the studio in assets/project: every file git tracks or would track, without the repo's own
.claude folder, the build output, or any media. scripts/new_project.sh copies that snapshot into a
folder to make it a workspace. Run this again after changing the kit, the tools or the docs.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from xcore.paths import ROOT

NAME = "refactr-animation-1"
SOURCE = ROOT / ".claude" / "skills" / NAME
DIST = ROOT / "dist"
SKIP_PREFIX = (".claude/", "dist/")
MEDIA = (".mp4", ".mov", ".mkv", ".webm", ".wav", ".mp3", ".m4a", ".aiff", ".flac")


def studio_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout.splitlines()
    return sorted(f for f in out if f and not f.startswith(SKIP_PREFIX) and not f.lower().endswith(MEDIA)
                  and (ROOT / f).is_file())


def build() -> Path:
    out = DIST / NAME
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(SOURCE, out)
    files = studio_files()
    for rel in files:
        target = out / "assets" / "project" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)
    # a new workspace starts on the studio's own demo, with nobody's video active
    (out / "assets" / "project" / "studio.json").write_text('{\n  "active_video": "demo"\n}\n')
    for script in (out / "scripts").glob("*.sh"):
        script.chmod(0o755)
    (out / "assets" / "project" / "x").chmod(0o755)
    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file()) / 1e6
    print(f"SKILL: {out.relative_to(ROOT)}  ({len(files)} studio files, {size:.1f} MB)")
    return out


def package(out: Path) -> Path:
    archive = DIST / f"{NAME}.skill"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob("*")):
            if p.is_file():
                z.write(p, Path(NAME) / p.relative_to(out))
    print(f"PACKAGE: {archive.relative_to(ROOT)}  ({archive.stat().st_size / 1e6:.1f} MB)")
    return archive


def install(out: Path) -> None:
    dest = Path.home() / ".claude" / "skills" / NAME
    dest.parent.mkdir(parents=True, exist_ok=True)
    # replace file by file, then drop what the new build no longer has: the folder itself stays put
    shutil.copytree(out, dest, dirs_exist_ok=True)
    keep = {p.relative_to(out) for p in out.rglob("*")}
    for p in sorted(dest.rglob("*"), reverse=True):
        if p.relative_to(dest) not in keep:
            p.unlink() if p.is_file() or p.is_symlink() else p.rmdir()
    print(f"INSTALLED: {dest}")


def main() -> None:
    if not (SOURCE / "SKILL.md").exists():
        sys.exit(f"{SOURCE} has no SKILL.md")
    out = build()
    package(out)
    if "--install" in sys.argv:
        install(out)


if __name__ == "__main__":
    main()
