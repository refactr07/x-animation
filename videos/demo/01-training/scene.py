from xkit import *

# SECTION demo/01-training, "How a model learns" (the reference section: read it before building one)
#
# Colour roles: blue = the question going in, teal = the model's settings (its dials),
#               red = the loss (how wrong it is), yellow = the thing to look at.
# Central picture: the model as a box of dials. It is noise, it guesses, it is measured, it is nudged,
#                  and (after a Remotion stretch that shows the same idea as code) it knows.
# Engines: Learn (Manim) -> TrainingLoop (Remotion, see TrainingLoop.tsx) -> Answer (Manim).
#
# No number of seconds below places a beat: beat() and on() follow the narration in beats.json,
# word by word. The run_times are the lengths of the moves themselves.

RANDOM = [0.12, 0.86, 0.34, 0.93, 0.2, 0.62]   # dial settings of an untrained model
TRAINED = [0.7, 0.72, 0.68, 0.71, 0.69, 0.73]  # after training: the needles agree
NOISE = [("banana", 0.14), ("seven", 0.13), ("Paris", 0.12), ("purple", 0.11)]
ANSWER = [("Paris", 0.97), ("Lyon", 0.02), ("Rome", 0.01)]
MODEL_AT = LEFT * 0.4   # where the model sits between a question and its answer
MODEL_SCALE = 1.7


def make_model(values, scale=MODEL_SCALE, at=MODEL_AT):
    return dial_panel(2, 3, values=values).scale(scale).move_to(at)


def name_tag(model):
    """The model's name, set under it. It travels with the model from then on."""
    return T("model", SMALL, GREY_B).next_to(model, DOWN, buff=0.22)


def make_prompt(model):
    """The question: two lines of blue text ending in the blank the model has to fill."""
    first = T("The capital of", BODY, BLUE_LIGHT)
    second = T("France is", BODY, BLUE_LIGHT)
    blank = Line(ORIGIN, RIGHT * 0.95, color=YELLOW, stroke_width=W_SHAPE)
    VGroup(first, second).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
    blank.next_to(second, RIGHT, buff=0.2).align_to(second, DOWN)
    block = VGroup(first, second, blank)
    block.next_to(model, LEFT, buff=1.25)
    return block, first, second, blank


def make_list(rows, model):
    # rows a little further apart than the default, so a highlight box fits round one of them
    return bar_list(rows, scale=1.6, size=BODY, row_gap=0.34, relative=False).next_to(model, RIGHT, buff=1.25)


class Learn(Segment):
    def construct(self):
        # ---------------------------------------------------------------- Noise
        # "Every AI model starts out as noise."
        self.beat("Noise")
        model = make_model([0.5] * 6, scale=2.0, at=ORIGIN)
        self.play(build(model.frame, run_time=0.7), stagger([pop(d) for d in model.dials], 0.12, run_time=0.8))
        self.regroup(model)
        name = name_tag(model)
        self.on("starts", lead=0.1)  # show the thing, then name it
        self.play(rise(name, distance=0.12, run_time=0.4))
        self.on("noise", lead=0.35)
        self.play(turn_dials(model.dials, RANDOM, run_time=0.8, lag_ratio=0.05))

        # ---------------------------------------------------------------- Guess
        # "Ask it a question, and it guesses."
        self.beat("Guess")
        seat = make_model(RANDOM)  # the model's place for this beat: lay the row out around it
        prompt, first, second, blank = make_prompt(seat)
        guesses = make_list(NOISE, seat)
        ask = arrow(prompt.get_right(), seat.get_left())
        out = arrow(seat.get_right(), guesses.get_left())
        check_layout(prompt, seat, guesses)
        # make room first: the model settles into its seat while the question is written
        self.play(
            model.animate(run_time=0.5).scale(MODEL_SCALE / 2.0).move_to(MODEL_AT),
            name.animate(run_time=0.5).move_to(name_tag(seat)),
            later(0.1, write(first, run_time=0.35)),
            later(0.3, write(second, run_time=0.3)),
            later(0.5, draw(blank, run_time=0.2)),
        )
        self.on("question", lead=0.1)
        self.play(grow(ask, run_time=0.45))
        # room(): this move takes 0.45 s, or less if the voice reaches "guesses" sooner
        self.play(travel(ask, BLUE, run_time=self.room("guesses", most=0.45, lead=0.35)))
        self.on("guesses", lead=0.35)
        self.play(grow(out, run_time=0.4), later(0.25, pop_list(guesses.rows)))

        # ---------------------------------------------------------------- Wrong
        # "Training measures how wrong that guess is,"
        self.beat("Wrong")
        measured = highlight_box(guesses, RED, buff=0.2)

        # The plot the loss will live on, laid out now so the loss readout knows where its home is.
        plot = axes((0, 6.5, 1), (0, 4.6, 1), width=7.0, height=4.2).move_to([2.45, -0.45, 0])

        def loss_at(x):
            return 0.32 * (x - 4.2) ** 2 + 0.35

        curve = plot.plot(loss_at, x_range=[0.65, 6.3], color=GREY_A, stroke_width=W_SHAPE * 1.2)
        home = plot.y_axis.get_top() + UP * 0.55 + RIGHT * 0.95  # left edge of the number, above the y axis
        number = still_number(2.31, "{:.2f}", HEADING, RED, anchor=LEFT, at=home)
        tag = T("loss", BODY, RED)
        align_baseline(tag, number)
        tag.shift(RIGHT * (number.get_left()[0] - 0.25 - tag.get_right()[0]))
        loss = VGroup(tag, number)
        loss_home = loss.get_center()
        loss.next_to(measured, DOWN, buff=0.4)
        check_layout(prompt, model, VGroup(measured, loss))

        self.play(draw(measured, run_time=0.45))
        self.on("wrong", lead=0.3)
        self.play(rise(loss, run_time=0.45))

        # The stage turns from "question in, guess out" into "settings in, loss out".
        model_home = [-4.75, -0.45, 0]
        settings = T("settings", BODY, TEAL)
        settings.next_to(plot.x_axis.get_right(), DOWN, buff=0.3).shift(LEFT * settings.width / 2)
        feeds = thin_arrow([-3.1, -0.45, 0], [-1.35, -0.45, 0], buff=0)
        x = ValueTracker(0.9)
        point = Dot(plot.c2p(0.9, loss_at(0.9)), radius=0.13, color=RED).set_z_index(3)
        allow_overlap(point)
        parts_of(VGroup(plot, curve, point, settings))
        self.on("that", lead=0.1)
        seat = make_model(RANDOM, scale=1.4, at=model_home)
        self.play(
            *leave(prompt, ask, out, measured, *guesses.rows, run_time=0.35),
            model.animate(run_time=1.0).scale(1.4 / MODEL_SCALE).move_to(model_home),
            name.animate(run_time=1.0).move_to(name_tag(seat)),
            glide(loss, loss_home, via=[0.6, 3.0, 0], run_time=1.0),
            # the plot waits until the model has cleared its left edge: nothing overlaps, even mid-move
            later(0.6, draw(plot, run_time=0.55)),
            later(0.75, draw(curve, run_time=0.4)),
            later(0.85, grow(feeds, run_time=0.3)),
            later(0.85, rise(settings, distance=0.1, run_time=0.3)),
            later(0.85, pop(point, run_time=0.3)),
        )

        # ---------------------------------------------------------------- Downhill
        # "and nudges every number inside the model a little, downhill."
        self.beat("Downhill")
        point.add_updater(lambda m: m.move_to(plot.c2p(x.get_value(), loss_at(x.get_value()))))

        class Loss:  # what the readout shows: the loss where the point is, on the scale it was measured in
            @staticmethod
            def get_value():
                return loss_at(x.get_value()) * 2.31 / loss_at(0.9)

        readout = counter(self, Loss, "{:.2f}", HEADING, RED, anchor=LEFT, at=home)
        self.remove(number)
        self.add(readout)

        steps = [("nudges", 2.2, 0.65), ("number", 3.1, 0.55), ("model", 3.7, 0.55), ("downhill", 4.1, 0.8)]
        for k, (word, to, seconds) in enumerate(steps, start=1):
            self.on(word, lead=0.15)
            ghost = Dot(point.get_center(), radius=0.06, color=GREY_C).set_z_index(2)
            allow_overlap(ghost)
            share = k / len(steps)
            dials = [r + (t - r) * share for r, t in zip(RANDOM, TRAINED)]
            self.play(
                FadeIn(ghost, run_time=0.2),
                x.animate(run_time=seconds).set_value(to),
                turn_dials(model.dials, dials, run_time=seconds),
            )
        self.finish()


class Answer(Segment):
    def construct(self):
        # ---------------------------------------------------------------- Works
        # "and the noise turns into something that knows the answer."
        self.beat("Works")
        model = make_model(RANDOM)
        prompt, first, second, blank = make_prompt(model)
        answer = make_list(ANSWER, model)
        ask = arrow(prompt.get_right(), model.get_left())
        out = arrow(model.get_right(), answer.get_left())
        check_layout(prompt, model, answer)

        # The cut from the editor lands on the model already settling: the noise turns into order.
        self.add(model, name_tag(model), prompt)
        self.play(turn_dials(model.dials, TRAINED, run_time=1.0, lag_ratio=0.06), grow(ask, run_time=0.5))
        self.on("something", lead=0.1)
        self.play(travel(ask, BLUE, run_time=self.room("knows", most=0.45, lead=0.3)))
        self.on("knows", lead=0.3)
        self.play(grow(out, run_time=0.4), later(0.25, pop_list(answer.rows)))
        self.on("answer", lead=0.25)
        chosen = highlight_box(answer.rows[0], YELLOW, buff=0.12)
        filled = T("Paris", BODY, YELLOW)
        filled.next_to(second, RIGHT, buff=0.2)
        align_baseline(filled, second)
        parts_of(VGroup(prompt, filled))  # the answer takes the blank's place: it belongs to the question now
        self.play(draw(chosen, run_time=0.5), FadeOut(blank, run_time=0.25), later(0.2, write(filled, run_time=0.5)))
        self.finish()
