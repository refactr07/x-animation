#!/usr/bin/env bash
# Make a folder a refactr-animation workspace: the two-engine studio (Manim + Remotion), ready to render.
#
#   bash new_project.sh "<folder>"                             copy the studio in, install both engines, check
#   bash new_project.sh "<folder>" --modules-from "<workspace>"   link that workspace's Node packages (instant)
#   bash new_project.sh "<folder>" --voice                     also install the speech aligner for ./x align
#   bash new_project.sh "<folder>" --no-setup                  copy only
#   bash new_project.sh "<folder>" --update-kit                refresh kit, tools and docs of an existing workspace
#
# Safe to run again. A plain run never overwrites a file that exists. --update-kit overwrites the kit,
# the tools, the docs and the build files, and never touches videos/, theme/, FEEDBACK.md, STYLE.md,
# CLAUDE.md or studio.json: those are the workspace's own.
set -euo pipefail

SKILL="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$SKILL/assets/project"
DIR=""
MODULES=""
VOICE=0
SETUP=1
UPDATE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --modules-from) MODULES="${2:?--modules-from needs a workspace folder}"; shift 2 ;;
    --voice) VOICE=1; shift ;;
    --no-setup) SETUP=0; shift ;;
    --update-kit) UPDATE=1; shift ;;
    -h|--help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) if [ -z "$DIR" ]; then DIR="$1"; shift; else echo "unexpected argument: $1" >&2; exit 1; fi ;;
  esac
done
[ -n "$DIR" ] || { echo 'usage: bash new_project.sh "<folder>" [--modules-from "<workspace>"] [--voice] [--no-setup] [--update-kit]' >&2; exit 1; }

if [ ! -f "$SRC/x" ]; then
  echo "This copy of the skill has no bundled studio ($SRC is missing)." >&2
  echo "Get the studio instead with:  git clone https://github.com/refactr07/x-animation \"$DIR\"" >&2
  exit 1
fi

missing=0
for tool in uv node ffmpeg python3; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    missing=1
    case "$tool" in
      uv) echo "Missing uv. Install it:  brew install uv   (or: curl -LsSf https://astral.sh/uv/install.sh | sh)" >&2 ;;
      node) echo "Missing Node (22 or newer). Install it:  nvm install 24" >&2 ;;
      ffmpeg) echo "Missing ffmpeg. Install it:  brew install ffmpeg" >&2 ;;
      python3) echo "Missing python3." >&2 ;;
    esac
  fi
done
[ "$missing" = 0 ] || [ "$SETUP" = 0 ] || exit 1

mkdir -p "$DIR"
DIR="$(cd "$DIR" && pwd)"

# Copy with Python: the same behaviour on every platform, and exact control over what may be replaced.
python3 - "$SRC" "$DIR" "$UPDATE" <<'PY'
import shutil
import sys
from pathlib import Path

src, dest, update = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3] == "1"
# What --update-kit may replace: the machinery. Everything else belongs to the workspace.
MACHINERY = ("kit/", "tools/", "src/", "docs/", "public/fonts/", "x", "remotion.config.ts", "tsconfig.json",
             "package.json", "package-lock.json", "pyproject.toml", "uv.lock", ".nvmrc", ".python-version",
             "videos/kit/", "videos/demo/")
added = replaced = kept = 0
for f in sorted(p for p in src.rglob("*") if p.is_file()):
    rel = f.relative_to(src).as_posix()
    target = dest / rel
    if target.exists():
        machinery = any(rel == m or rel.startswith(m) for m in MACHINERY) and rel != "src/sections.generated.tsx"
        if update and machinery and target.read_bytes() != f.read_bytes():
            shutil.copy2(f, target)
            replaced += 1
        else:
            kept += 1
        continue
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, target)
    added += 1
print(f"WORKSPACE {dest}: {added} files added, {replaced} replaced, {kept} already there and kept")
PY
chmod +x "$DIR/x" "$DIR/tools/setup.sh" 2>/dev/null || true
cd "$DIR"

if [ -n "$MODULES" ] && [ ! -e node_modules ]; then
  if [ -d "$MODULES/node_modules" ]; then
    ln -s "$(cd "$MODULES" && pwd)/node_modules" node_modules
    echo "linked node_modules from $MODULES"
  else
    echo "$MODULES has no node_modules: installing them here instead" >&2
  fi
fi

if [ "$SETUP" = 1 ]; then
  if [ "$VOICE" = 1 ]; then bash tools/setup.sh --voice; else bash tools/setup.sh; fi
else
  echo "Copied only. Finish with:  cd \"$DIR\" && ./x setup"
fi

echo
echo "Next, in $DIR:"
echo "  read FEEDBACK.md, then videos/demo/01-training (the reference section)"
echo "  ./x new \"Title\" --video <video-slug> --script <pasted script file>"
