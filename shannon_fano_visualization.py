from manim import *
import numpy as np

class ShannonFanoTree(Scene):
    def construct(self):
        symbols = ['A', 'B', 'C', 'D', 'E']
        probabilities = [0.4, 0.2, 0.2, 0.1, 0.1]

        root = self.create_node("ABCDE\n1.0", ORIGIN)
        self.play(Create(root))

        self.build_tree(symbols, probabilities, root, 0)

    def build_tree(self, symbols, probabilities, parent_node, depth, direction=0):
        if len(symbols) <= 1:
            return

        total = sum(probabilities)
        split_point = 0
        split_sum = 0
        while split_sum < total / 2 and split_point < len(probabilities) - 1:
            split_sum += probabilities[split_point]
            split_point += 1

        left_symbols = symbols[:split_point]
        right_symbols = symbols[split_point:]
        left_prob = sum(probabilities[:split_point])
        right_prob = sum(probabilities[split_point:])

        left_text = f"{''.join(left_symbols)}\n{left_prob:.2f}"
        right_text = f"{''.join(right_symbols)}\n{right_prob:.2f}"

        offset = 3 / (2 ** depth)
        left_pos = parent_node.get_center() + DOWN * 1.5 + LEFT * offset
        right_pos = parent_node.get_center() + DOWN * 1.5 + RIGHT * offset

        left_node = self.create_node(left_text, left_pos)
        right_node = self.create_node(right_text, right_pos)

        left_edge = Line(parent_node.get_bottom(), left_node.get_top(), color=BLUE)
        right_edge = Line(parent_node.get_bottom(), right_node.get_top(), color=RED)

        self.play(
            Create(left_node),
            Create(right_node),
            Create(left_edge),
            Create(right_edge)
        )

        left_label = Text("0", font_size=24).next_to(left_edge, LEFT, buff=0.1)
        right_label = Text("1", font_size=24).next_to(right_edge, RIGHT, buff=0.1)
        self.play(Write(left_label), Write(right_label))

        self.build_tree(left_symbols, probabilities[:split_point], left_node, depth + 1, -1)
        self.build_tree(right_symbols, probabilities[split_point:], right_node, depth + 1, 1)

    def create_node(self, text, position):
        return Text(text, font_size=24).move_to(position)
