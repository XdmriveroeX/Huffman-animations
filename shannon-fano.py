import sys
from manim import *
import numpy as np

class ShannonFanoTree(Scene):
    def __init__(self, symbols, probabilities):
        super().__init__()
        self.symbols = symbols
        self.probabilities = probabilities
        self.current_level = 0
        self.waiting_time = 0.3
        self.codes = {}

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
        print("Entering show_final_codes method")
        print(f"Total objects in tree_group: {len(self.tree_group)}")
        
        # Find all leaf nodes and non-leaf objects
        leaf_nodes = []
        objects_to_remove = []
        for node in self.tree_group:
            if isinstance(node, VGroup) and len(node) == 2:
                rectangle, text_group = node
                if isinstance(rectangle, Rectangle) and isinstance(text_group, VGroup):
                    symbol_text = text_group[0].text
                    if symbol_text.startswith('{') and symbol_text.endswith('}') and len(symbol_text) == 3:
                        leaf_nodes.append(node)
                        print(f"Found leaf node: {symbol_text}")
                    else:
                        objects_to_remove.append(node)
            else:
                objects_to_remove.append(node)
        
        print(f"Number of leaf nodes found: {len(leaf_nodes)}")
        print(f"Codes generated: {self.codes}")
        
        if not leaf_nodes:
            print("No leaf nodes found. Skipping final codes animation.")
            return

        # Remove non-leaf nodes and edges
        self.play(*[FadeOut(obj) for obj in objects_to_remove], run_time=1.5)
        
        # Move leaf nodes to the center, arranged in two rows
        num_leaves = len(leaf_nodes)
        num_per_row = (num_leaves + 1) // 2
        new_positions = []
        for i in range(num_leaves):
            row = i // num_per_row
            col = i % num_per_row
            x = (col - (num_per_row - 1) / 2) * 1.5
            y = 1 - row * 2
            new_positions.append(np.array([x, y, 0]))
        
        animations = [node.animate.move_to(pos) for node, pos in zip(leaf_nodes, new_positions)]
        self.play(*animations, run_time=2)
        self.wait(1)
        
        # Show codes
        code_texts = []
        for node in leaf_nodes:
            symbol = node[1][0].text[1]  # Get the symbol from the text object
            if symbol in self.codes:
                code = self.codes[symbol]
                code_text = Text(f"{symbol}: {code}", font_size=24).next_to(node, DOWN)
                code_texts.append(code_text)
            else:
                print(f"No code found for symbol: {symbol}")
        
        if code_texts:
            self.play(*[Write(text) for text in code_texts], run_time=2)
            self.wait(2)
        else:
            print("No codes to display.")
        
        print("Exiting show_final_codes method")
    
# Hardcoded example
symbols = ['A', 'B', 'C', 'D', 'E','F','G','H']
probabilities = [0.10, 0.15, 0.05, 0.10, 0.20, 0.15, 0.05, 0.2]

# Create the scene
scene = ShannonFanoTree(symbols, probabilities)

# Render the scene
if __name__ == '__main__':
    scene.render()