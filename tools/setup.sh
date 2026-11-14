#!/usr/bin/env bash
# One-time setup on a new machine or a fresh clone. Safe to run again: it only adds what is missing.
#
#   ./x setup            Python + Manim, Node + Remotion, the headless browser, backdrops
#   ./x setup --voice    also the speech aligner used by ./x align (downloads a model on first use)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing '$1'. $2" >&2; exit 1; }; }
need uv "Install it:  brew install uv   (or: curl -LsSf https://astral.sh/uv/install.sh | sh)"
need node "Install Node 22 or newer (this repo pins 24 in .nvmrc):  nvm install 24"
need ffmpeg "Install it:  brew install ffmpeg"

echo "== Python: Manim Community + the kit =="
# macOS has wheels for everything. Linux needs: sudo apt install build-essential python3-dev libcairo2-dev libpango1.0-dev
if [ "${1:-}" = "--voice" ]; then uv sync --extra voice; else uv sync; fi

echo "== Node: Remotion =="
if [ -f package-lock.json ]; then npm ci --no-fund --no-audit; else npm install --no-fund --no-audit; fi
npx --no-install remotion browser ensure

echo "== Backdrops and Remotion's list of sections =="
uv run -q python -W ignore tools/backdrops.py
uv run -q python -W ignore tools/registry.py

echo
uv run -q python -W ignore tools/doctor.py
echo
echo "Ready. Try:  ./x draft demo/01-training"
