"""xcore: the engine-agnostic half of the x-animation kit.

Tokens, the beat/cue timing model and backdrops. Nothing here imports Manim, so the tools in
tools/ start fast and the same numbers reach both engines.
"""

from .paths import ROOT
from .tokens import TOKENS, BACKDROPS, color, contrast, mix

__all__ = ["ROOT", "TOKENS", "BACKDROPS", "color", "contrast", "mix"]
