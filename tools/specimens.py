"""Specimen sheets for the Manim kit: every colour, size, shape and pictogram on one stage.

    ./x specimens                 # writes docs/assets/kit_*.png

Look at these after changing theme/tokens.json or adding to the kit: a pictogram that reads badly
here will read badly in a video.
"""

from xkit import *

config.disable_caching = True


def caption(text, mob, color=GREY_C):
    return T(text, TINY, color).next_to(mob, DOWN, buff=0.16)


class Palette(Scene):
    def construct(self):
        set_stage(BG.to_hex())
        title = T("Blackboard", TITLE).to_edge(UP, buff=MARGIN_Y)
        names = ["BLUE", "TEAL", "GREEN", "YELLOW", "GOLD", "ORANGE", "RED", "PINK", "PURPLE"]
        swatches = VGroup()
        for n in names:
            col = globals()[n]
            sw = VGroup(box(1.1, 0.8, col), T(n.title(), TINY, col))
            sw.arrange(DOWN, buff=0.14)
            swatches.add(sw)
        swatches.arrange(RIGHT, buff=0.3).next_to(title, DOWN, buff=0.5)

        greys = VGroup(*[
            VGroup(box(1.1, 0.5, c, fill=0.5), T(n, TINY, GREY_C)).arrange(DOWN, buff=0.12)
            for n, c in [("White", WHITE), ("Grey A", GREY_A), ("Grey B", GREY_B), ("Grey C", GREY_C), ("Grey D", GREY_D)]
        ]).arrange(RIGHT, buff=0.3).next_to(swatches, DOWN, buff=0.45)

        sizes = VGroup(
            T("Hero 140", HERO), T("Title 84", TITLE), T("Heading 68", HEADING), T("Label 54", LABEL),
            T("Body 46", BODY), T("Small 36", SMALL), T("Tiny 28", TINY),
        )
        row1 = VGroup(sizes[0], sizes[1]).arrange(RIGHT, buff=0.6, aligned_edge=DOWN)
        row2 = VGroup(*sizes[2:]).arrange(RIGHT, buff=0.45, aligned_edge=DOWN)
        VGroup(row1, row2).arrange(DOWN, buff=0.3).next_to(greys, DOWN, buff=0.45)

        strokes = VGroup(*[
            VGroup(Line(LEFT * 0.7, RIGHT * 0.7, stroke_width=w, color=WHITE), T(n, TINY, GREY_C)).arrange(DOWN, buff=0.14)
            for n, w in [("hair", W_HAIR), ("thin", W_THIN), ("shape", W_SHAPE), ("hero", W_HERO)]
        ]).arrange(RIGHT, buff=0.5).to_edge(DOWN, buff=MARGIN_Y)
        self.add(title, swatches, greys, row1, row2, strokes)


class Shapes(Scene):
    def construct(self):
        set_stage(BG.to_hex())
        row1 = VGroup(
            VGroup(box(1.6, 1.0, BLUE)).add(), disc(0.5, TEAL), token("token", BLUE), token("next", YELLOW),
            chip("Name Tag", YELLOW), chip("Step One", PINK), badge("1"), badge("A", YELLOW),
        ).arrange(RIGHT, buff=0.45)
        a = arrow(LEFT * 1.1, RIGHT * 1.1)
        b = thin_arrow(LEFT * 0.9, RIGHT * 0.9)
        c = arc_arrow(LEFT * 0.9 + DOWN * 0.2, RIGHT * 0.9 + DOWN * 0.2, angle=-PI / 2)
        word = T("look here", BODY)
        hl = VGroup(word, highlight_box(word))
        word2 = T("underlined", BODY)
        ul = VGroup(word2, underline(word2))
        word3 = T("not this", BODY, GREY_B)
        st = VGroup(word3, cross_out(word3))
        boxed = box(0.9, 0.7, GREY_B)
        sx = VGroup(boxed, strike(boxed, inset=0.14))
        row2 = VGroup(a, b, c, hl, ul, st, sx, check(), cross()).arrange(RIGHT, buff=0.45)
        probs = bar_list([("Paris", 0.86), ("London", 0.06), ("Rome", 0.04), ("Berlin", 0.02)], more=True)
        vec = bracket_vector([1.9, -2.3, 0.4, -0.1, 3.2], more=True)
        ax = axes((0, 6, 1), (0, 4, 1), 3.6, 2.2)
        curve = ax.plot(lambda x: 0.35 * (x - 3) ** 2 + 0.5, x_range=[0.3, 5.7], color=TEAL, stroke_width=W_SHAPE)
        plot = VGroup(ax, curve, Dot(ax.c2p(1.2, 0.35 * 1.8**2 + 0.5), radius=0.09, color=YELLOW))
        math = eq("{{ w : w }} arrow.l {{ w : w0 }} - {{ eta : lr }} nabla {{ L : loss }}", BODY,
                  colors={"w": BLUE, "w0": BLUE, "lr": YELLOW, "loss": RED})
        bar = progress_bar(2.6, 0.62, BLUE)
        row3 = VGroup(probs, vec, plot, VGroup(math, bar).arrange(DOWN, buff=0.5)).arrange(RIGHT, buff=0.7)
        VGroup(row1, row2, row3).arrange(DOWN, buff=0.7).move_to(ORIGIN)
        self.add(row1, row2, row3)


class Pictograms(Scene):
    def construct(self):
        set_stage(BG.to_hex())
        items = [
            ("person", person()), ("team", team()), ("robot", robot()), ("page", page()), ("pages", pages()),
            ("code_bars", code_bars(scale=0.7)), ("folder", folder()), ("clipboard", clipboard(done=2)),
            ("app_window", app_window(1.9, 1.3)), ("browser", browser(1.9, 1.3)), ("terminal", terminal(1.7, 1.1)),
            ("phone", phone()), ("laptop", laptop()), ("chat_bubble", chat_bubble(1.6, 0.7)),
            ("server", server()), ("database", database()), ("cloud", cloud()), ("chip_cpu", chip_cpu()),
            ("gear", gear()), ("dial", dial(0.7)), ("dial_panel", dial_panel()), ("neural_net", neural_net(width=1.9, height=1.2, node_radius=0.07)),
            ("clock", clock()), ("magnifier", magnifier()), ("padlock", padlock()), ("key", key()), ("bolt", bolt()),
            ("star", star()), ("lightbulb", lightbulb()), ("envelope", envelope()), ("globe", globe()),
            ("warning", warning()), ("coin", coin()), ("eye", eye()), ("line_chart", line_chart()), ("crowd", crowd(radius=0.5, n=10)),
        ]
        cells = VGroup()
        for name, mob in items:
            cell = VGroup(mob, T(name, TINY, GREY_C).scale(0.8))
            cell.arrange(DOWN, buff=0.16)
            cells.add(cell)
        cells.arrange_in_grid(rows=4, cols=9, buff=(0.3, 0.4))
        cells.scale_to_fit_width(FRAME_W - 2 * MARGIN_X)
        if cells.height > FRAME_H - 2 * MARGIN_Y:
            cells.scale_to_fit_height(FRAME_H - 2 * MARGIN_Y)
        self.add(cells.move_to(ORIGIN))
