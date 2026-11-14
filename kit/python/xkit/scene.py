"""Segment: a Manim scene whose beats land on their cues, frame for frame.

A segment is one run of beats that Manim draws (beats.json "segments"). Scene code names beats and
words, never seconds, so retiming to a voiceover changes beats.json and nothing else:

    class Descent(Segment):                 # same name as the segment's "scene" in beats.json
        def construct(self):
            self.beat("Noise")              # waits until this beat's cue, then starts it
            ...
            self.on("wrong")                # waits until the word "wrong" is spoken in this beat
            self.play(...)
            self.beat("Downhill")           # pads the rest of "Noise" with a still hold
            ...
            self.finish()                   # pads to the segment's end, to the frame

Time is counted in frames. Manim advances its clock by whole frames, and every wait below is a
whole number of frames, so frame i of the clip is exactly t = i / fps and a cue lands on the same
frame here as in a Remotion segment.
"""

from __future__ import annotations

import inspect
import os
from pathlib import Path

from manim import Animation, FadeOut, Group, Mobject, MovingCameraScene, Restore, ThreeDScene, VGroup, config

from xcore.backdrop import backdrop_png
from xcore.beats import END, Beat, Beats, Segment as _Seg, frame_of
from xcore.tokens import BACKDROPS, TOKENS

from .layout import describe, find_overlaps
from .motion import use_house_motion
from .theme import CAMERA, LEAD, set_stage

# Render every play: until() relies on the clock being exact, and cached plays advance it by
# their nominal length instead of their frame count.
config.disable_caching = True


class _Cued:
    """Cue timing, the stage, live objects and the overlap audit. Mixed into Segment and Segment3D."""

    #: Check that no two objects overlap, on every `audit_every` seconds of every animation.
    audit: bool = True
    audit_every: float = 0.1

    # ------------------------------------------------------------------ setup
    def setup(self) -> None:
        super().setup()
        use_house_motion()
        here = Path(inspect.getfile(type(self))).resolve().parent
        self.section: Beats | None = Beats.load(here) if (here / "beats.json").exists() else None
        self.seg: _Seg | None = None
        if self.section is not None:
            try:
                self.seg = self.section.segment(type(self).__name__)
            except KeyError:
                self.seg = None  # a scene that is not a segment plays against the whole section
        self._origin = self.seg.start if self.seg else 0.0
        self._beat: Beat | None = None
        self._live: list[VGroup] = []
        self._tick = 0
        self._seen: set[tuple[int, int]] = set()
        self.late: list[tuple[str, float]] = []
        self.overlaps: list[str] = []
        self._paint_stage(self.section.backdrop if self.section else os.environ.get("X_BACKDROP", "dots"))

    def _paint_stage(self, style: str) -> None:
        """Use the section's backdrop PNG as the camera background (the same file Remotion shows)."""
        spec = BACKDROPS["styles"][style]
        set_stage(spec["bg"])
        cam = self.camera
        cam.background_color = spec["bg"]
        cam.background_image = str(backdrop_png(style, cam.pixel_width, cam.pixel_height))
        cam.init_background()
        cam.reset()

    # ------------------------------------------------------------------ the clock
    @property
    def fps(self) -> float:
        return float(config.frame_rate)

    @property
    def frame_now(self) -> int:
        return round(self.time * self.fps)

    @property
    def now(self) -> float:
        """Seconds since the start of the section (not of this segment)."""
        return self._origin + self.frame_now / self.fps

    def _local_frame(self, section_seconds: float) -> int:
        """Frame of this clip on which a section time falls. Both ends are rounded on the section's
        frame grid, so consecutive segments never gain or lose a frame between them."""
        return frame_of(section_seconds, self.fps) - frame_of(self._origin, self.fps)

    def _hold_frames(self, n: int) -> None:
        """A still hold of exactly n frames."""
        if n <= 0:
            return
        fps, before = self.fps, self.frame_now
        moving = bool(
            getattr(self, "always_update_mobjects", False)
            or getattr(self, "updaters", None)
            or any(m.has_time_based_updater() for m in self.get_mobject_family_members())
        )
        if moving:
            # rendered frame by frame: np.arange(0, run_time, 1/fps) must yield exactly n steps
            duration = 1 / fps if n == 1 else (n - 0.5) / fps
            super().wait(duration, frozen_frame=False)
        else:
            # one frame repeated: Manim writes int(duration * fps) copies of it
            super().wait((n + 0.5) / fps, frozen_frame=True)
        got = self.frame_now - before
        if got != n and not self.renderer.skip_animations:
            raise RuntimeError(f"hold of {n} frames wrote {got}: Manim's frame stepping changed, fix _hold_frames")

    def goto(self, section_seconds: float, what: str = "") -> None:
        """Hold still until the given section time. Reports when that time has already passed."""
        n = self._local_frame(section_seconds) - self.frame_now
        if n < 0:
            late = -n / self.fps
            if late > 1.5 / self.fps:
                self.late.append((what, late))
                print(f"TIMING {what or 'cue'} is {late:.2f}s late: shorten what comes before it")
            return
        self._hold_frames(n)

    def wait(self, duration: float = 1.0, stop_condition=None, frozen_frame=None) -> None:
        """A hold of a whole number of frames. Prefer on(), at() and beat(), which follow the voice."""
        if stop_condition is not None:
            super().wait(duration, stop_condition=stop_condition, frozen_frame=frozen_frame)
            return
        self._hold_frames(max(1, round(duration * self.fps)))

    # ------------------------------------------------------------------ beats and words
    def beat(self, name: str) -> Beat:
        """Start a beat on its cue. Whatever time the previous beat left over becomes a still hold."""
        if self.section is None:
            raise RuntimeError("beat() needs a beats.json beside the scene file")
        b = self.section.beat(name)
        self.goto(b.start, f"beat {name}")
        self._beat = b
        print(f"CUE {name} {self.now:.3f}")
        return b

    def on(self, phrase: str, nth: int = 1, lead: float = LEAD, beat: str | None = None) -> None:
        """Hold until `phrase` is spoken in the current beat (or in `beat`).

        The hold ends `lead` seconds before the word, so a move started next lands on it. Pass
        lead=0 when the change itself is instant, or a longer lead for a slow move that should
        finish on the word.
        """
        b = self.section.beat(beat) if beat else self._beat
        if b is None:
            raise RuntimeError("on() comes after beat()")
        word = b.find(phrase, nth)
        self.goto(max(word.start - lead, b.start), f'word "{phrase}" in {b.name}')

    def at(self, seconds: float) -> None:
        """Hold until `seconds` into the current beat. on() is better when a word marks the moment."""
        if self._beat is None:
            raise RuntimeError("at() comes after beat()")
        self.goto(self._beat.start + seconds, f"{seconds:.2f}s into {self._beat.name}")

    def left(self) -> float:
        """Seconds until the next beat starts: what is still free in this beat."""
        if self._beat is None:
            return 0.0
        return max(0.0, self.section.next_cue(self._beat.name) - self.now)

    def room(self, phrase: str | None = None, most: float = 1.0, least: float = 0.2, nth: int = 1,
             lead: float = LEAD) -> float:
        """How long a move may take if it has to be done before `phrase` is spoken (or, with no
        phrase, before the next beat): never more than `most`, never less than `least`.

            self.play(grow(arrow, run_time=self.room("guesses", most=0.5)))

        Use it for the move just before a word that matters. With an estimate the move takes `most`;
        with a brisk voiceover it tightens by itself instead of making the next cue late.
        """
        if self._beat is None:
            return most
        if phrase is None:
            target = self.section.next_cue(self._beat.name)
        else:
            target = max(self._beat.find(phrase, nth).start - lead, self._beat.start)
        return min(most, max(least, target - self.now))

    def finish(self, clear: bool = False) -> None:
        """End the segment exactly on its last frame. With clear=True everything fades to the stage
        over the final half second (for the last segment of a section)."""
        end = self.seg.end if self.seg else (self.section.duration if self.section else self.now)
        if clear:
            self.goto(end - 0.5, "the closing fade")
            mobs = [m for m in self.mobjects if m is not getattr(self.camera, "frame", None)]
            for m in mobs:
                m.clear_updaters()
            if mobs:
                frames = self._local_frame(end) - self.frame_now
                if frames >= 2:
                    self.play(*[FadeOut(m) for m in mobs], run_time=(frames - 0.5) / self.fps)
        self.goto(end, "the end of the segment")
        want = self._local_frame(end)
        print(f"SEGMENT {type(self).__name__} frames={self.frame_now} expected={want} "
              f"late={len(self.late)} overlaps={len(self.overlaps)}")

    # ------------------------------------------------------------------ live objects
    def live(self, update) -> VGroup:
        """An object rebuilt every frame: update(holder, dt) sets holder.submobjects.

        For a counter, a meter, text that types itself. The holder is emptied before every play,
        because a play remembers each object's parts when it starts: a holder still carrying last
        frame's child would draw that child, frozen, for the whole play. Call clear_updaters() on
        it to freeze it with its last child.
        """
        holder = VGroup()
        holder.add_updater(update)
        self._live.append(holder)
        return holder

    def regroup(self, group: Mobject) -> Mobject:
        """After a build that brought a group's parts in one by one, the scene lists every part
        separately. This replaces them with the group itself, so the scene holds one object."""
        self.remove(*group.get_family())
        self.add(group)
        return group

    def play(self, *args, **kwargs) -> None:
        for holder in self._live:
            if holder.updaters:
                holder.submobjects = []
        super().play(*args, **kwargs)

    # ------------------------------------------------------------------ the overlap audit
    def update_to_time(self, t: float) -> None:
        super().update_to_time(t)
        mode = os.environ.get("X_OVERLAP", "report")
        if not self.audit or mode == "off":
            return
        self._tick += 1
        if self._tick % max(1, round(self.audit_every * self.fps)):
            return
        for a, b in find_overlaps(self.mobjects):
            pair = (id(a), id(b))
            if pair in self._seen:
                continue
            self._seen.add(pair)
            where = f"in {self._beat.name}" if self._beat else ""
            msg = f"OVERLAP at {self.now:.2f}s {where}: {describe(a)} / {describe(b)}"
            self.overlaps.append(msg)
            if mode == "error":
                raise ValueError(msg + "  -> make room first, reroute the move, or allow_overlap() a deliberate crossing")
            print(msg)


class Segment(_Cued, MovingCameraScene):
    """The base for every 2D segment. The camera is static unless the narration dives into a detail."""

    def zoom_to(self, target, scale: float = 0.6, run_time: float = CAMERA) -> Animation:
        """Reframe onto a detail: self.play(self.zoom_to(mob)). Follow it with zoom_out()."""
        frame = self.camera.frame
        if not hasattr(frame, "saved_state") or frame.saved_state is None:
            frame.save_state()
        point = target.get_center() if isinstance(target, Mobject) else target
        return frame.animate(run_time=run_time).scale(scale).move_to(point)

    def zoom_out(self, run_time: float = CAMERA) -> Animation:
        return Restore(self.camera.frame, run_time=run_time)


class Segment3D(_Cued, ThreeDScene):
    """For ideas that are really spatial: vector spaces, surfaces, stacked layers. The overlap audit
    is off (projection makes distant things overlap on screen); check 3D shots on the QA sheets."""

    audit = False


def everything(scene) -> Group:
    """All objects on screen, as one group (the camera frame excluded)."""
    return Group(*[m for m in scene.mobjects if m is not getattr(scene.camera, "frame", None)])


__all__ = ["Segment", "Segment3D", "everything", "END"]

_ = TOKENS  # tokens are part of this module's contract: the stage and motion defaults come from them
