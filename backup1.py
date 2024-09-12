import numpy as np
from manim import *

class ShannonFanoTree(Scene):
    def __init__(self, symbols, probabilities):
        super().__init__()
        self.symbols = symbols
        self.probabilities = probabilities
        self.current_level = 0
        self.waiting_time = 0.3
        self.codes = {}
        self.edges_map = {}  # To store the edges and labels for highlighting later

    def construct(self):
        config.frame_rate = 60  # Default is 60, reducing it slows everything down
        
        self.tree_group = VGroup()
        
        root_text = f"{{{','.join(self.symbols)}}}\n{sum(self.probabilities):.2f}"
        root_position = UP * 3
        root_node = self.create_node(root_text, root_position)
        self.play(Create(root_node, run_time=2))
        self.wait(self.waiting_time)  # Add a pause after creating the root

        self.build_tree(self.symbols, self.probabilities, root_node, 0, "")
        
        self.show_final_codes()


    def build_tree(self, symbols, probabilities, parent_node, depth, current_code):
        print(f"Building tree for symbols: {symbols}, depth: {depth}, current_code: {current_code}")
        if len(symbols) == 1:
            self.codes[symbols[0]] = current_code
            print(f"Leaf node reached: Symbol {symbols[0]}, Code {current_code}")
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

        left_pos = parent_node.get_center() + DOWN * vertical_spacing + LEFT * horizontal_spacing
        right_pos = parent_node.get_center() + DOWN * vertical_spacing + RIGHT * horizontal_spacing

        left_node = self.create_node(left_text, left_pos)
        right_node = self.create_node(right_text, right_pos)

        left_edge = Line(parent_node.get_bottom(), left_node.get_top(), color=BLUE)
        right_edge = Line(parent_node.get_bottom(), right_node.get_top(), color=RED)

        self.tree_group.add(left_edge, right_edge)

        # Slow down the creation animations
        self.play(
            Create(left_edge, run_time=1.5),
            Create(right_edge, run_time=1.5),
            Create(left_node, run_time=1.5),
            Create(right_node, run_time=1.5)
        )
        self.wait(self.waiting_time)  # Add a short pause after creating nodes

        left_label = Text("0", font_size=24).next_to(left_edge, LEFT, buff=0.1)
        right_label = Text("1", font_size=24).next_to(right_edge, RIGHT, buff=0.1)
        self.tree_group.add(left_label, right_label)
        self.play(Write(left_label), Write(right_label))
        self.wait(self.waiting_time)  # Add a short pause after adding labels
        
        self.edges_map[current_code + "0"] = (left_edge, left_label)
        self.edges_map[current_code + "1"] = (right_edge, right_label)

        if len(left_symbols) > 1:
            self.build_tree(left_symbols, probabilities[:split_point], left_node, depth + 1, current_code + "0")
        else:
            self.codes[left_symbols[0]] = current_code + "0"
            print(f"Left leaf node: Symbol {left_symbols[0]}, Code {current_code + '0'}")

        if len(right_symbols) > 1:
            self.build_tree(right_symbols, probabilities[split_point:], right_node, depth + 1, current_code + "1")
        else:
            self.codes[right_symbols[0]] = current_code + "1"
            print(f"Right leaf node: Symbol {right_symbols[0]}, Code {current_code + '1'}")
        
        print(f"Finished processing depth {depth}")
    
    
    def create_node(self, text, position):
        symbol_set, prob = text.split('\n')
        
        symbol_text = Text(symbol_set, font_size=24)
        prob_text = Text(prob, font_size=24)
        
        text_group = VGroup(symbol_text, prob_text).arrange(DOWN, buff=0.1)
        
        rectangle = Rectangle(
            width=text_group.width + 0.2,
            height=text_group.height + 0.2,
            color=WHITE
        ).move_to(text_group)
        
        node = VGroup(rectangle, text_group).move_to(position)
        self.tree_group.add(node)
        
        return node

    def zoom_out(self):
        scale_factor = 0.85  # Adjust this value to control zoom intensity
        self.play(self.tree_group.animate.scale(scale_factor))
        self.wait(self.waiting_time)  # Add a pause after zooming out
        
    def show_final_codes(self):
        # Highlight the path and color the codes
        for symbol, code in self.codes.items():
            self.highlight_path(symbol, code)
            self.show_code(symbol, code)

    def highlight_path(self, symbol, code):
        original_colors = []  # To store the original colors of the edges and labels

        # Highlight the edges and labels that correspond to the path for the given code
        for i, bit in enumerate(code):
            edge, label = self.edges_map[code[:i+1]]

            # Store the original colors
            original_colors.append((edge.get_color(), label.get_color()))

            # Change the color of the edges and labels to green
            self.play(edge.animate.set_color(GREEN), label.animate.set_color(GREEN))

        # Show the code for the symbol
        self.show_code(symbol, code)

        # After displaying the code, revert the edges and labels to their original colors
        for i, (edge, label) in enumerate([self.edges_map[code[:i+1]] for i in range(len(code))]):
            original_edge_color, original_label_color = original_colors[i]

            # Restore the edge color
            self.play(edge.animate.set_color(original_edge_color), run_time=0.3)

            # Instead of just changing the label color, rewrite the label to ensure it's restored properly
            label_text = label.text  # Get the current text of the label
            new_label = Text(label_text, font_size=24).move_to(label.get_center())  # Create a new label at the same position
            self.play(ReplacementTransform(label, new_label), run_time=0.3)
            self.edges_map[code[:i+1]] = (edge, new_label)  # Update the edges_map with the new label




    def show_code(self, symbol, code):
        # Create the code text
        code_text = Text(f"{symbol}: {code}", font_size=24, color=WHITE)
        
        # Find the leaf node for the given symbol
        leaf_node = self.find_leaf_node(symbol)
        
        if leaf_node:
            # Place the code text below the leaf node
            self.play(Write(code_text.next_to(leaf_node, DOWN, buff=0.2)))
        self.wait(1)

    def find_leaf_node(self, symbol):
        # Search for the leaf node containing only the given symbol
        for node in self.tree_group:
            if isinstance(node, VGroup) and len(node) > 1:
                text_group = node[1]
                if len(text_group) > 0 and isinstance(text_group[0], Text):
                    if text_group[0].text == f"{{{symbol}}}":
                        return node
        return None

    
# Hardcoded example
symbols = ['A', 'B', 'C', 'D', 'E','F','G']
probabilities = [0.10, 0.15, 0.05, 0.10, 0.20, 0.15, 0.25]

# Create the scene
scene = ShannonFanoTree(symbols, probabilities)

# Render the scene
if __name__ == '__main__':
    scene.render() 
