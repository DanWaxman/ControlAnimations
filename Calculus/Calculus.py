from big_ol_pile_of_manim_imports import *

class StraightLineScene(GraphScene):
    CONFIG = {
            "x_min": -10,
            "x_max": 10,
            "y_min": -10,
            "y_max": 10,
            "graph_origin": ORIGIN,
    }
    
    def construct(self):
        self.setup_axes(animate=True)
        graph = self.get_graph(lambda x : 2*x, RED)
        left_line = self.get_vertical_line_to_graph(1, graph, color=GREEN)
        right_line = self.get_vertical_line_to_graph(3, graph, color=GREEN)
        
        slope_text = TexMobject("\\textrm{slope} = 2")
        label_coord = self.input_to_graph_point(2, graph)
        slope_text.next_to(label_coord, UP * 1 + LEFT * 1)

        self.play(ShowCreation(graph))
        
        self.wait(5)
        self.play(ShowCreation(left_line), ShowCreation(right_line), ShowCreation(slope_text))
        self.wait()


class WavyFunctionScene(GraphScene):
    CONFIG = {
            "x_min": -10,
            "x_max": 10,
            "y_min": -10,
            "y_max": 10,
            "graph_origin": ORIGIN,
    }

    def construct(self):
        l_vals = [1, 1.2, 1.4, 1.6, 1.8, 1.9, 1.95, 1.99]
        r_vals = [3, 2.8, 2.6, 2.4, 2.2, 2.1, 2.05, 2.01]
        self.setup_axes(animate=True)
        graph = self.get_graph(self.gfunc, RED)
        left_lines = [self.get_vertical_line_to_graph(y, graph, color=GREEN) for y in l_vals]
        right_lines = [self.get_vertical_line_to_graph(y, graph, color=GREEN) for y in r_vals]

        slopes = [(self.gfunc(r_vals[i]) - self.gfunc(l_vals[i])) / (r_vals[i] - l_vals[i]) for i in range(len(l_vals))]
        slope_texts = [TexMobject("\\textrm{slope} = " + str(z)[:7]) for z in slopes]
        
        label_coord = self.input_to_graph_point(2, graph)
        for st in slope_texts:
            st.next_to(label_coord, UP * 1 + LEFT * 1)

        st = TexMobject("")
        st.next_to(label_coord, UP * 1 + LEFT * 1)

        self.play(ShowCreation(graph))
        self.wait()
        for i in range(len(left_lines)):
            self.play(Transform(left_lines[0], left_lines[i]), Transform(right_lines[0], right_lines[i]), Transform(st, slope_texts[i]))
            self.wait(0.5)

        self.wait()


    def gfunc(self, x):
        return 1/3.0 * (x-3.5)**3 - (x-3.5)**2 - x + 3.5

class IntegralScene(GraphScene):
    CONFIG = {
            "x_min": -10,
            "x_max": 10,
            "y_min": -10,
            "y_max": 10,
            "graph_origin": ORIGIN,
    }

    def construct(self):
        self.setup_axes(animate=True)

        graph = self.get_graph(self.gfunc, RED)
        
        rect_list = self.get_riemann_rectangles_list(graph, 6, max_dx=1.0, x_min=0, x_max=3)
        
        riemann_sums = [self.get_riemann_sum(x) for x in [3, 6, 12, 24, 48, 96]]
        riemann_texts = [TexMobject("\\textrm{area} = " + str(z)[:7]) for z in riemann_sums]
        
        for rst in riemann_texts:
            rst.move_to(UP)

        st = TexMobject("")
        st.move_to(UP)

        self.play(ShowCreation(graph))
        self.wait()
        self.play(ShowCreation(rect_list[0]))

        for i in range(len(rect_list)):
            self.play(Transform(rect_list[0], rect_list[i]), Transform(st, riemann_texts[i]))
            self.wait()

    def get_riemann_sum(self, x):
        dx = 3.0 / x
        cx = 0
        s = 0
        for i in range(x):
            s += self.gfunc(cx) * dx
            cx += dx

        return s

    def gfunc(self, x):
        return 1/3.0 * (x-3.5)**3 - (x-3.5)**2 - x + 3.5
