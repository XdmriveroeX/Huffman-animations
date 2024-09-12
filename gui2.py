import numpy as np
import PySimpleGUI as sg
from manim import *

class ShannonFanoTree(Scene):
    def __init__(self, symbols, probabilities):
        super().__init__()
        self.symbols = symbols
        self.probabilities = probabilities
        self.current_level = 0
        self.waiting_time = 0.3
        self.codes = {}
        self.edges_map = {}

    def construct(self):
        config.frame_rate = 60
        self.tree_group = VGroup()

        root_text = self._format_node_text(self.symbols, self.probabilities)
        root_position = UP * 3
        root_node = self._create_node(root_text, root_position)
        
        self.play(Create(root_node, run_time=2))
        self.wait(self.waiting_time)

        self._build_tree(self.symbols, self.probabilities, root_node, 0, "")
        self._show_final_codes()

    def _build_tree(self, symbols, probabilities, parent_node, depth, current_code):
        if len(symbols) == 1:
            self.codes[symbols[0]] = current_code
            return

        self.current_level = max(self.current_level, depth + 1)
        if self.current_level > 3:
            self._zoom_out()

        split_point = self._find_split_point(probabilities)
        left_symbols, right_symbols = symbols[:split_point], symbols[split_point:]
        left_prob, right_prob = sum(probabilities[:split_point]), sum(probabilities[split_point:])

        left_text = self._format_node_text(left_symbols, probabilities[:split_point])
        right_text = self._format_node_text(right_symbols, probabilities[split_point:])

        vertical_spacing, horizontal_spacing = 1.5, 3 / (2 ** depth)
        left_pos = parent_node.get_center() + DOWN * vertical_spacing + LEFT * horizontal_spacing
        right_pos = parent_node.get_center() + DOWN * vertical_spacing + RIGHT * horizontal_spacing

        left_node = self._create_node(left_text, left_pos)
        right_node = self._create_node(right_text, right_pos)

        left_edge = Line(parent_node.get_bottom(), left_node.get_top(), color=BLUE)
        right_edge = Line(parent_node.get_bottom(), right_node.get_top(), color=RED)

        self._animate_node_creation(left_edge, right_edge, left_node, right_node)

        left_label = self._create_label("0", left_edge, LEFT)
        right_label = self._create_label("1", right_edge, RIGHT)

        self._update_edges_map(current_code, left_label, right_label, left_edge, right_edge)

        if len(left_symbols) > 1:
            self._build_tree(left_symbols, probabilities[:split_point], left_node, depth + 1, current_code + "0")
        else:
            self.codes[left_symbols[0]] = current_code + "0"

        if len(right_symbols) > 1:
            self._build_tree(right_symbols, probabilities[split_point:], right_node, depth + 1, current_code + "1")
        else:
            self.codes[right_symbols[0]] = current_code + "1"

    def _create_node(self, text, position):
        symbol_set, prob = text.split('\n')
        symbol_text = Text(symbol_set, font_size=24)
        prob_text = Text(prob, font_size=24)

        text_group = VGroup(symbol_text, prob_text).arrange(DOWN, buff=0.1)
        rectangle = Rectangle(width=text_group.width + 0.2, height=text_group.height + 0.2, color=WHITE).move_to(text_group)

        node = VGroup(rectangle, text_group).move_to(position)
        self.tree_group.add(node)
        return node

    def _find_split_point(self, probabilities):
        total = sum(probabilities)
        running_sum = 0

        for i, prob in enumerate(probabilities):
            if running_sum + prob > total / 2:
                return i if abs(running_sum - total/2) < abs(running_sum + prob - total/2) else i + 1
            running_sum += prob
        return len(probabilities)

    def _animate_node_creation(self, left_edge, right_edge, left_node, right_node):
        self.tree_group.add(left_edge, right_edge)
        self.play(Create(left_edge, run_time=1.5), Create(right_edge, run_time=1.5), Create(left_node, run_time=1.5), Create(right_node, run_time=1.5))
        self.wait(self.waiting_time)

    def _create_label(self, text, edge, direction):
        label = Text(text, font_size=24).next_to(edge, direction, buff=0.1)
        self.tree_group.add(label)
        self.play(Write(label))
        self.wait(self.waiting_time)
        return label

    def _update_edges_map(self, current_code, left_label, right_label, left_edge, right_edge):
        self.edges_map[current_code + "0"] = (left_edge, left_label)
        self.edges_map[current_code + "1"] = (right_edge, right_label)

    def _zoom_out(self):
        scale_factor = 0.85
        self.play(self.tree_group.animate.scale(scale_factor))
        self.wait(self.waiting_time)

    def _show_final_codes(self):
        for symbol, code in self.codes.items():
            self._highlight_path(symbol, code)

    def _highlight_path(self, symbol, code):
        original_colors = []
        for i, bit in enumerate(code):
            edge, label = self.edges_map[code[:i+1]]
            original_colors.append((edge.get_color(), label.get_color()))
            self.play(edge.animate.set_color(GREEN), label.animate.set_color(GREEN))

        self._show_code(symbol, code)

        for i, (edge, label) in enumerate([self.edges_map[code[:i+1]] for i in range(len(code))]):
            original_edge_color, original_label_color = original_colors[i]
            self.play(edge.animate.set_color(original_edge_color), run_time=0.3)
            new_label = Text(label.text, font_size=24).move_to(label.get_center())
            self.play(ReplacementTransform(label, new_label), run_time=0.3)
            self.edges_map[code[:i+1]] = (edge, new_label)

    def _show_code(self, symbol, code):
        code_text = Text(f"{symbol}: {code}", font_size=24, color=GREEN)
        leaf_node = self._find_leaf_node(symbol)

        if leaf_node:
            self.play(Write(code_text.next_to(leaf_node, DOWN, buff=0.2)))
            self.wait(1)
            self.play(code_text.animate.set_color(WHITE))

    def _find_leaf_node(self, symbol):
        for node in self.tree_group:
            if isinstance(node, VGroup) and len(node) > 1:
                text_group = node[1]
                if len(text_group) > 0 and isinstance(text_group[0], Text):
                    if text_group[0].text == f"{{{symbol}}}":
                        return node
        return None

    def _format_node_text(self, symbols, probabilities):
        return f"{{{','.join(symbols)}}}\n{sum(probabilities):.2f}"

# GUI Layout
def create_gui():
    layout = [
        [sg.Text('Enter Symbols and Probabilities')],
        [sg.Text('Number of Symbols:'), sg.InputText(key='num_symbols')],
        [sg.Button('Next', key='next')],
        [sg.Text('', size=(50, 1), key='feedback')],
        [sg.Button('Submit', key='submit', visible=False)],
        [sg.Image(key='video')],
    ]
    window = sg.Window('Shannon-Fano Coding', layout, finalize=True)
    return window

# Function to get user input via GUI
def get_input_from_gui():
    window = create_gui()
    num_symbols = 0
    input_rows = []  # To store dynamically added input elements

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        # Handling "Next" button to add symbol/probability inputs dynamically
        if event == 'next':
            try:
                num_symbols = int(values['num_symbols'])
                if num_symbols <= 0:
                    raise ValueError
                # Dynamically add rows for symbol and probability inputs
                for i in range(num_symbols):
                    input_rows.append([
                        sg.Text(f"Symbol {i + 1}:", size=(10, 1)), sg.InputText(key=f'symbol_{i}'),
                        sg.Text(f"Probability {i + 1}:", size=(15, 1)), sg.InputText(key=f'prob_{i}')
                    ])
                window.extend_layout(window, input_rows)  # Add new input fields to window
                window['submit'].update(visible=True)  # Show the submit button after adding inputs
                window['next'].update(visible=False)  # Hide the "Next" button after clicking
            except ValueError:
                window['feedback'].update('Please enter a valid number of symbols.')

        # Handling "Submit" button click to process input and render animation
        if event == 'submit':
            symbols = []
            probabilities = []
            try:
                # Collect symbols and probabilities from user inputs
                for i in range(num_symbols):
                    symbol = values[f'symbol_{i}']
                    prob = float(values[f'prob_{i}'])
                    symbols.append(symbol)
                    probabilities.append(prob)

                # Validate that probabilities sum up to 1
                if np.isclose(sum(probabilities), 1):
                    window['feedback'].update('Rendering the Shannon-Fano Tree...')
                    # Here you would render the video using the ShannonFanoTree class
                    scene = ShannonFanoTree(symbols, probabilities)
                    scene.render()  # This will generate the video

                    window['feedback'].update('Rendering complete! The video is now ready.')
                    # You would load the video file into the GUI here
                    # Example: window['video'].update(filename='path_to_video.png')
                else:
                    window['feedback'].update('Error: The probabilities must sum to 1.')
            except ValueError:
                window['feedback'].update('Please enter valid probabilities.')

    window.close()

# Start the GUI
if __name__ == '__main__':
    get_input_from_gui()
