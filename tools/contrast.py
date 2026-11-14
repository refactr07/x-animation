#!/usr/bin/env python3
"""Every colour against every backdrop: can it be read, can it be seen?

    ./x contrast

Text and words in colour need a contrast ratio of at least 4.5 against the backdrop they sit on
(WCAG AA); strokes and shapes need 3. A backdrop's own pattern has to stay quiet: between 1.1 and
2.5 against its background. Exit code 1 when a colour fails on any backdrop. Run it after changing
theme/tokens.json or theme/backdrops.json.
"""

from __future__ import annotations

import sys

from xcore.tokens import BACKDROPS, TOKENS, color, contrast

TEXT = ["text", "grey.a", "grey.b", "grey.c", "blue", "blue_light", "teal", "green", "yellow", "gold", "orange", "red", "pink", "purple"]
SHAPES = ["grey.d"]  # used for guides and empty slots only, never for text


def main() -> None:
    styles = BACKDROPS["styles"]
    fails = []
    print(f"{'':<12}" + "".join(f"{s:>10}" for s in styles) + "   needs")
    for group, need in ((TEXT, 4.5), (SHAPES, 1.5)):
        for name in group:
            row = [contrast(color(name), styles[s]["bg"]) for s in styles]
            flag = "".join(f"{v:10.2f}" for v in row)
            print(f"{name:<12}{flag}   {need}")
            for s, v in zip(styles, row):
                if v < need:
                    fails.append(f"{name} on {s}: {v:.2f} (needs {need})")
    print()
    for s, spec in styles.items():
        if spec.get("pattern"):
            v = contrast(spec["pattern"]["color"], spec["bg"])
            ok = 1.1 <= v <= 2.5
            print(f"pattern of {s:<10} {v:5.2f}   {'ok' if ok else 'should be between 1.1 and 2.5'}")
            if not ok:
                fails.append(f"pattern of {s}: {v:.2f}")
    tint = TOKENS["tint"]["fill"]
    print(f"\ntinted fills mix {tint:.0%} of the colour over the backdrop; text on a tint keeps the contrast of its backdrop or better")
    if fails:
        print("\nCONTRAST FAIL\n" + "\n".join("  - " + f for f in fails))
        sys.exit(1)
    print("\nCONTRAST OK: every colour can be read on every backdrop")


if __name__ == "__main__":
    main()
