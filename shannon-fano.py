import sys
from manim import *

class ShannonFanoTree(Scene):
    def __init__(self, symbols, probabilities):
        super().__init__()
        self.symbols = symbols
        self.probabilities = probabilities
        self.current_level = 0
        self.waiting_time = 0.3

    def construct(self):
        # Slow down the overall animation speed
        config.frame_rate = 60  # Default is 60, reducing it slows everything down
        
        self.tree_group = VGroup()
        
        root_text = f"{{{','.join(self.symbols)}}}\n{sum(self.probabilities):.2f}"
        root_position = UP * 3
        root_box, root_text = self.create_node(root_text, root_position)
        self.tree_group.add(root_box, root_text)
        self.play(Create(root_box, run_time=2), Write(root_text, run_time=2))
        self.wait(self.waiting_time)  # Add a pause after creating the root

        self.build_tree(self.symbols, self.probabilities, (root_box, root_text), 0)

    def build_tree(self, symbols, probabilities, parent_node, depth):
        if len(symbols) <= 1:
            return

        self.current_level = max(self.current_level, depth + 1)

        if self.current_level > 3:
            self.zoom_out()

        total = sum(probabilities)
        running_sum = 0
        split_point = 0

        for i, prob in enumerate(probabilities):
            if running_sum + prob > total / 2:
                if abs(running_sum - total/2) < abs(running_sum + prob - total/2):
                    split_point = i
                else:
                    split_point = i + 1
                break
            running_sum += prob
            split_point = i + 1

        left_symbols = symbols[:split_point]
        right_symbols = symbols[split_point:]
        left_prob = sum(probabilities[:split_point])
        right_prob = sum(probabilities[split_point:])

        left_text = f"{{{','.join(left_symbols)}}}\n{left_prob:.2f}"
        right_text = f"{{{','.join(right_symbols)}}}\n{right_prob:.2f}"

        vertical_spacing = 1.5
        horizontal_spacing = 3 / (2 ** depth)

        left_pos = parent_node[0].get_center() + DOWN * vertical_spacing + LEFT * horizontal_spacing
        right_pos = parent_node[0].get_center() + DOWN * vertical_spacing + RIGHT * horizontal_spacing

        left_box, left_text = self.create_node(left_text, left_pos)
        right_box, right_text = self.create_node(right_text, right_pos)

        left_edge = Line(parent_node[0].get_bottom(), left_box.get_top(), color=BLUE)
        right_edge = Line(parent_node[0].get_bottom(), right_box.get_top(), color=RED)

        self.tree_group.add(left_box, left_text, right_box, right_text, left_edge, right_edge)

        # Slow down the creation animations
        self.play(
            Create(left_edge, run_time=1.5),
            Create(right_edge, run_time=1.5),
            Create(left_box, run_time=1.5),
            Create(right_box, run_time=1.5),
            Write(left_text, run_time=1.5),
            Write(right_text, run_time=1.5)
        )
        self.wait(self.waiting_time)  # Add a short pause after creating nodes

        left_label = Text("0", font_size=24).next_to(left_edge, LEFT, buff=0.1)
        right_label = Text("1", font_size=24).next_to(right_edge, RIGHT, buff=0.1)
        self.tree_group.add(left_label, right_label)
        self.play(Write(left_label), Write(right_label))
        self.wait(self.waiting_time)  # Add a short pause after adding labels

        if len(left_symbols) > 1:
            self.build_tree(left_symbols, probabilities[:split_point], (left_box, left_text), depth + 1)
        if len(right_symbols) > 1:
            self.build_tree(right_symbols, probabilities[split_point:], (right_box, right_text), depth + 1)

    def create_node(self, text, position):
        symbol_set, prob = text.split('\n')
        
        symbol_text = Text(symbol_set, font_size=24)
        prob_text = Text(prob, font_size=24)
        
        vgroup = VGroup(symbol_text, prob_text).arrange(DOWN, buff=0.1)
        
        rectangle = Rectangle(
            width=vgroup.width + 0.2,
            height=vgroup.height + 0.2,
            color=WHITE
        ).move_to(vgroup)
        
        node = VGroup(rectangle, vgroup).move_to(position)
        return rectangle, vgroup

    def zoom_out(self):
        scale_factor = 0.85  # Adjust this value to control zoom intensity
        self.play(self.tree_group.animate.scale(scale_factor))
        self.wait(self.waiting_time)  # Add a pause after zooming out


# Hardcoded example
symbols = ['A', 'B', 'C', 'D', 'E','F','G','H']
probabilities = [0.10, 0.15, 0.05, 0.10, 0.20, 0.15, 0.05, 0.2]

# Create the scene
scene = ShannonFanoTree(symbols, probabilities)

# Render the scene
if __name__ == '__main__':
    scene.render()