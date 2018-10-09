from big_ol_pile_of_manim_imports import *

import math

class BangBang(Animation):
    CONFIG = {
        "acceleration": 0.0001,
        "friction": 0.00005,
        "setpoint": 5,
        "direction": RIGHT,
        "run_time": 15,
        "rate_func": (lambda x: 1),
    }

    def __init__(self, system, a_vec, **kwargs):
        self.system = system
        self.velocity = 0
        self.pv = 0
        self.b_flag = False

        self.a_vec = a_vec

        Animation.__init__(self, VGroup(system, a_vec), **kwargs)


    def update_mobject(self, dt):
        system = self.system
        a_vec = self.a_vec 

        self.pv += self.velocity * dt
        system.shift(self.velocity * self.direction * dt)

        accel = self.acceleration - self.friction * math.copysign(1, self.velocity)

        if self.pv < self.setpoint:
            self.velocity += self.acceleration * dt
            if self.b_flag:
                a_vec.scale(-1)
                self.b_flag = False
        else:
            self.velocity -= self.acceleration * dt
            if not self.b_flag:
                a_vec.scale(-1)
                self.b_flag = True

        # I'm sorry...
        # Really, (int(not self.b_flag) - 0.5) is just a (messy) way of returning a direction multiplier
        # Since if it's going backwards ---> -1/2, if it's going forwards ---> +1/2
        a_vec.next_to(self.system, UP).shift(RIGHT * self.a_vec.get_width() * (int(not self.b_flag) - 0.5))

class PIDController(Animation):
    CONFIG = {
        "max_acceleration": 0.01,
        "friction": 0.001,
        "setpoint": 5,
        "direction": RIGHT,
        "run_time": 15,
        "kp": 0.01,
        "kd": 0.1,
        "ki": 0.0001,
        "rate_func": (lambda x: 1),
    }

    def __init__(self, system, a_label, a_vec, **kwargs):
        self.system = system
        self.velocity = 0
        self.pv = 0
        self.a_vec = a_vec
        self.a_label = a_label

        # Have to digest the config outside of the Animation init for acceleration scaling.
        digest_config(self, kwargs)

        self.acceleration = self.kp * (self.setpoint - self.pv)
        self.a_prev = self.acceleration
        self.e_prev = (self.setpoint - self.pv)
        self.integral = 0

        Animation.__init__(self, VGroup(system, a_label, a_vec), **kwargs)

    def update_mobject(self, dt):
        system = self.system
        a_vec = self.a_vec
        a_label = self.a_label

        # Calculate applied acceleration
        self.acceleration = self.pid_output()
        if abs(self.acceleration) > self.max_acceleration:
            self.acceleration = self.max_acceleration * math.copysign(1, self.acceleration)

        # Record keeping for PID calculation
        self.e_prev = self.error()
        self.integral += self.ki * self.error()

        # Record applied acceleration for proper vector scaling
        a_app = self.acceleration

        # Apply friction
        if abs(self.velocity > 0):
            self.acceleration += -self.friction * math.copysign(1, self.velocity)
        else:
            self.acceleration += -math.copysign(1, self.velocity) * min(self.friction, abs(self.acceleration))

        self.velocity += self.acceleration * dt

        self.pv += self.velocity * dt
        dx = self.velocity * dt
        system.shift(dx * self.direction)
        a_label.shift(dx * self.direction)
        system.rotate_in_place(-2 * dx)

        a_vec.scale(a_app / self.a_prev)
        a_vec.next_to(self.a_label, UP).shift(RIGHT * self.a_vec.get_width() / 2.0 * math.copysign(1, a_app))
        self.a_prev = a_app

    def error(self):
        return self.setpoint - self.pv

    def pid_output(self):
        return self.kp * self.error() + self.kd * (self.error()- self.e_prev) + self.integral

class PController(PIDController):
    CONFIG = {
        "kp": 0.01,
        "ki": 0,
        "kd": 0,
    }

class PDController(PIDController):
    CONFIG = {
        "kp": 0.01,
        "ki": 0,
        "kd": 0.2,
    }


class TargetScene(Scene):
    def construct(self):
        self.ball = Circle(color=RED, fill_color=BLACK, fill_opacity=1, height=1)
        self.ball.move_to(DOWN * 1 + LEFT * 5)

        self.floor = Rectangle(color=BLACK, fill_color=BLACK, fill_opacity=1, height=2, width=14.2)
        self.floor.move_to(DOWN * 3)

        self.flag = ImageMobject("flag", height=3)
        self.flag.move_to(DOWN * 0.5 + LEFT * self.flag.get_width() / 2.0)

        self.add(self.floor)
        self.add(self.flag)
        self.play(FadeIn(self.ball))


class BangBangScene(TargetScene):
    def construct(self):
        TargetScene.construct(self)

        self.a_label = TextMobject("$a$")
        self.a_label.next_to(self.ball, UP)

        self.system = VGroup(self.ball, self.a_label)

        self.a_vec = Vector(RIGHT, color=BLACK)
        self.a_vec.next_to(self.system, UP).shift(RIGHT * self.a_vec.get_width() / 2.0)

        self.play(FadeIn(self.a_vec), FadeIn(self.a_label))

        self.play(BangBang(self.system, self.a_vec))


class ProportionalScene(TargetScene):
    def construct(self):
        TargetScene.construct(self)

        self.scene_setup()

        self.play(PController(self.system, self.a_label, self.a_vec, friction=0.0))
        self.wait()

        friction_question = TextMobject("But what about with friction?")
        friction_question.to_edge(UP)
        
        # The acceleration vector will be messed up here.
        # The easiest way to fix it is to just restore it to its initial state.
        self.remove(self.a_vec)
        self.a_vec.target = self.a_vec_init

        distance_travelled_mod = np.linalg.norm((LEFT * 5 + DOWN * 1) - self.system.get_center()) % PI
        self.play(FadeIn(friction_question), MoveToTarget(self.a_vec), VGroup(self.system, self.a_label).move_to, LEFT * 5 + DOWN * 0.75, submobject_mode="smoothed_lagged_start", rate_func=smooth)
        self.play(Rotate(self.system, angle=2 * distance_travelled_mod, in_place=True))
        self.wait()

        self.play(PController(self.system, self.a_label, self.a_vec), FadeOut(friction_question))
  
    def scene_setup(self):
        self.p_label = TextMobject("$P$")
        self.p_label.move_to(self.ball.get_center())

        self.a_label = TextMobject("$a$")
        self.a_label.next_to(self.ball, UP)

        self.system = VGroup(self.ball, self.p_label)

        self.a_vec = Arrow(ORIGIN, RIGHT, color=BLACK, preserve_tip_size_when_scaling=True)
        self.a_vec.next_to(self.a_label, UP).shift(RIGHT * self.a_vec.get_width() / 2.0)

        self.a_vec_init = deepcopy(self.a_vec)

        self.play(FadeIn(self.a_vec), FadeIn(self.a_label), FadeIn(self.p_label))     


class PDScene(TargetScene):
    def construct(self):
        TargetScene.construct(self)

        self.scene_setup()

        self.play(PDController(self.system, self.a_label, self.a_vec, run_time=8))
        self.wait(4)

        system_pos_line = Line(self.system.get_center(), self.system.get_center() + UP * 3, color=GREEN)
        goal_pos_line = Line(DOWN * 4, UP * 4, color=RED)

        self.play(ShowCreation(system_pos_line), ShowCreation(goal_pos_line))
        self.wait(3)
  
    def scene_setup(self):
        self.p_label = TextMobject("$PD$")
        self.p_label.move_to(self.ball.get_center())

        self.a_label = TextMobject("$a$")
        self.a_label.next_to(self.ball, UP)

        self.system = VGroup(self.ball, self.p_label)

        self.a_vec = Arrow(ORIGIN, RIGHT, color=BLACK, preserve_tip_size_when_scaling=True)
        self.a_vec.next_to(self.a_label, UP).shift(RIGHT * self.a_vec.get_width() / 2.0)

        self.a_vec_init = deepcopy(self.a_vec)

        self.play(FadeIn(self.a_vec), FadeIn(self.a_label), FadeIn(self.p_label))

