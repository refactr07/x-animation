"""xkit: the Manim half of x-animation. Every scene file starts with

    from xkit import *

which gives the whole Manim namespace with the house style laid over it: the palette replaces
Manim's colour names, text is set in Computer Modern through Typst, every move eases with
smootherstep, and Segment locks each beat to its cue.
"""

from manim import *  # noqa: F401,F403

from .theme import *  # noqa: F401,F403  (after manim: BLUE, YELLOW, WHITE ... are now the house colours)
from .text import *  # noqa: F401,F403
from .motion import *  # noqa: F401,F403
from .layout import *  # noqa: F401,F403
from .shapes import *  # noqa: F401,F403
from .pictograms import *  # noqa: F401,F403
from .counter import *  # noqa: F401,F403
from .scene import *  # noqa: F401,F403
