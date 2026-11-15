#!/usr/bin/env bash
# x-animation: one command for everything.   ./x help
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
py() { uv run -q python -W ignore "$@"; }

cmd="${1:-help}"
[ $# -gt 0 ] && shift
case "$cmd" in
  setup)      exec bash tools/setup.sh "$@" ;;
  new)        py tools/section.py new "$@" ;;
  time|check|cues|show) py tools/section.py "$cmd" "$@" ;;
  scaffold)   py tools/scaffold.py "$@" ;;
  sync)       py tools/registry.py "$@" ;;
  draft|preview|final) py tools/render.py "$cmd" "$@" ;;
  sheet|frames) py tools/sheet.py "$cmd" "$@" ;;
  still)      py tools/stills.py "$@" ;;
  align)      py tools/align.py "$@" ;;
  stillness)  py tools/stillness.py "$@" ;;
  contrast)   py tools/contrast.py "$@" ;;
  parity)     py tools/parity.py "$@" ;;
  doctor)     py tools/doctor.py "$@" ;;
  backdrops)  py tools/backdrops.py "$@" ;;
  specimens)  py tools/specimens_render.py "$@" ;;
  skill)      py tools/build_skill.py "$@" ;;
  studio)     py tools/registry.py && exec npx remotion studio "$@" ;;
  typecheck)  py tools/registry.py && exec npx tsc --noEmit ;;
  help|-h|--help)
    cat <<'TXT'
x-animation: script in, verified video out.

  A section, start to finish
    ./x new "Title" --script script.txt   create the next section of the active video from a pasted script
    ./x time <section>                    recompute beat and word times after editing beats.json
    ./x check <section>                   the rules a render needs
    ./x scaffold <section>                write a starting scene.py / Component.tsx for each segment
    ./x draft <section>                   960x540 check render, with QA sheets          (--only Name for one segment)
    ./x preview <section>                 1920x1080 at full frame rate
    ./x final <section>                   3840x2160 master, verified
    ./x align <section> voiceover.wav     retime every beat and word to a recorded voiceover

  Looking at things
    ./x show <section>     beats, engines, pictures        ./x cues <section>      the cue sheet
    ./x sheet <video>      storyboard of a render          ./x frames <video> t1 t2 ...   chosen frames
    ./x still <section> <Component> t1 t2 ...              Remotion frames without a render
    ./x studio             Remotion Studio, to scrub the Remotion segments

  Keeping the system honest
    ./x doctor             toolchain versions and what is missing
    ./x parity             render the same colours and type in both engines and compare them
    ./x contrast           every colour against every backdrop
    ./x specimens          the kit's colours, shapes and pictograms as sheets
    ./x typecheck          TypeScript           ./x sync    refresh Remotion's list of sections
    ./x skill [--install]  build the refactr-animation-1 Claude skill from this repo (and install it)

<section> is a folder, video/section, or a section's name or number in the active video (studio.json).
TXT
    ;;
  *) echo "unknown command: $cmd (try ./x help)" >&2; exit 1 ;;
esac
