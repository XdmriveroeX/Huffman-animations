import sys
import numpy as np
import os
import platform

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QUrl, QCoreApplication
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWebEngineWidgets import QWebEngineView


from manim import (
    Scene, VGroup, UP, DOWN, LEFT, RIGHT, Text, Rectangle, Line, config,
    WHITE, BLUE, RED, GREEN, Create, Write, ReplacementTransform
)


class ShannonFanoTree(Scene):
    """Class to create and animate a Shannon-Fano tree using Manim."""

    def __init__(self, symbols, probabilities):
        super().__init__()
        self.symbols = symbols
        self.probabilities = probabilities
        self.current_level = 0
        self.waiting_time = 0.3
        self.codes = {}
        self.edges_map = {}

    def construct(self):
        """Constructs the Manim scene by building and animating the Shannon-Fano tree."""
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
        """Recursively builds the Shannon-Fano tree and animates it."""
        if len(symbols) == 1:
            self.codes[symbols[0]] = current_code
            return

        self.current_level = max(self.current_level, depth + 1)
        if self.current_level > 3:
            self._zoom_out()

        split_point = self._find_split_point(probabilities)
        left_symbols = symbols[:split_point]
        right_symbols = symbols[split_point:]
        left_probabilities = probabilities[:split_point]
        right_probabilities = probabilities[split_point:]

        left_text = self._format_node_text(left_symbols, left_probabilities)
        right_text = self._format_node_text(right_symbols, right_probabilities)

        vertical_spacing = 1.5
        horizontal_spacing = 3 / (2 ** depth)
        left_pos = (parent_node.get_center() +
                    DOWN * vertical_spacing +
                    LEFT * horizontal_spacing)
        right_pos = (parent_node.get_center() +
                     DOWN * vertical_spacing +
                     RIGHT * horizontal_spacing)

        left_node = self._create_node(left_text, left_pos)
        right_node = self._create_node(right_text, right_pos)

        left_edge = Line(parent_node.get_bottom(), left_node.get_top(), color=BLUE)
        right_edge = Line(parent_node.get_bottom(), right_node.get_top(), color=RED)

        self._animate_node_creation(left_edge, right_edge, left_node, right_node)

        left_label = self._create_label("0", left_edge, LEFT)
        right_label = self._create_label("1", right_edge, RIGHT)

        self._update_edges_map(current_code, left_label, right_label, left_edge, right_edge)

        if len(left_symbols) > 1:
            self._build_tree(
                left_symbols, left_probabilities, left_node, depth + 1, current_code + "0"
            )
        else:
            self.codes[left_symbols[0]] = current_code + "0"

        if len(right_symbols) > 1:
            self._build_tree(
                right_symbols, right_probabilities, right_node, depth + 1, current_code + "1"
            )
        else:
            self.codes[right_symbols[0]] = current_code + "1"

    def _create_node(self, text, position):
        """Creates a node in the tree with the given text at the specified position."""
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

    def _find_split_point(self, probabilities):
        """Finds the split point to partition the symbols for the Shannon-Fano algorithm."""
        total = sum(probabilities)
        running_sum = 0

        for i, prob in enumerate(probabilities):
            if running_sum + prob > total / 2:
                return i if abs(running_sum - total / 2) < abs(running_sum + prob - total / 2) else i + 1
            running_sum += prob
        return len(probabilities)

    def _animate_node_creation(self, left_edge, right_edge, left_node, right_node):
        """Animates the creation of nodes and edges in the tree."""
        self.tree_group.add(left_edge, right_edge)
        self.play(
            Create(left_edge, run_time=1.5),
            Create(right_edge, run_time=1.5),
            Create(left_node, run_time=1.5),
            Create(right_node, run_time=1.5)
        )
        self.wait(self.waiting_time)

    def _create_label(self, text, edge, direction):
        """Creates a label ('0' or '1') next to an edge."""
        label = Text(text, font_size=24).next_to(edge, direction, buff=0.1)
        self.tree_group.add(label)
        self.play(Write(label))
        self.wait(self.waiting_time)
        return label

    def _update_edges_map(self, current_code, left_label, right_label, left_edge, right_edge):
        """Updates the mapping of edges and labels for path highlighting."""
        self.edges_map[current_code + "0"] = (left_edge, left_label)
        self.edges_map[current_code + "1"] = (right_edge, right_label)

    def _zoom_out(self):
        """Zooms out the tree animation when the tree becomes too large."""
        scale_factor = 0.85
        self.play(self.tree_group.animate.scale(scale_factor))
        self.wait(self.waiting_time)

    def _show_final_codes(self):
        """Highlights the paths and displays the final codes for each symbol."""
        for symbol, code in self.codes.items():
            self._highlight_path(symbol, code)

    def _highlight_path(self, symbol, code):
        """Highlights the path corresponding to the code of a symbol."""
        original_colors = []
        for i, bit in enumerate(code):
            edge, label = self.edges_map[code[:i + 1]]
            original_colors.append((edge.get_color(), label.get_color()))
            self.play(edge.animate.set_color(GREEN), label.animate.set_color(GREEN))

        self._show_code(symbol, code)

        for i, (edge, label) in enumerate([self.edges_map[code[:i + 1]] for i in range(len(code))]):
            original_edge_color, original_label_color = original_colors[i]
            self.play(edge.animate.set_color(original_edge_color), run_time=0.3)
            new_label = Text(label.text, font_size=24).move_to(label.get_center())
            self.play(ReplacementTransform(label, new_label), run_time=0.3)
            self.edges_map[code[:i + 1]] = (edge, new_label)

    def _show_code(self, symbol, code):
        """Displays the code next to the leaf node of the symbol."""
        code_text = Text(f"{symbol}: {code}", font_size=24, color=GREEN)
        leaf_node = self._find_leaf_node(symbol)

        if leaf_node:
            self.play(Write(code_text.next_to(leaf_node, DOWN, buff=0.2)))
            self.wait(1)
            self.play(code_text.animate.set_color(WHITE))

    def _find_leaf_node(self, symbol):
        """Finds the leaf node corresponding to the given symbol."""
        for node in self.tree_group:
            if isinstance(node, VGroup) and len(node) > 1:
                text_group = node[1]
                if len(text_group) > 0 and isinstance(text_group[0], Text):
                    if text_group[0].text == f"{{{symbol}}}":
                        return node
        return None

    def _format_node_text(self, symbols, probabilities):
        """Formats the text to be displayed in a node."""
        return f"{{{','.join(symbols)}}}\n{sum(probabilities):.2f}"


class InputWindow(QWidget):
    """GUI window for user input to generate the Shannon-Fano tree."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initializes the user interface."""
        layout = QVBoxLayout()

        # Input for number of symbols
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Number of symbols:"))
        self.num_symbols_input = QLineEdit()
        hbox.addWidget(self.num_symbols_input)
        layout.addLayout(hbox)

        # Button to generate input fields
        generate_btn = QPushButton("Generate Input Fields")
        generate_btn.clicked.connect(self.generate_input_fields)
        layout.addWidget(generate_btn)

        # Table for symbol inputs
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Symbol", "Probability"])
        layout.addWidget(self.table)

        # Button to generate tree
        generate_tree_btn = QPushButton("Generate Shannon-Fano Tree")
        generate_tree_btn.clicked.connect(self.generate_tree)
        layout.addWidget(generate_tree_btn)

        self.setLayout(layout)
        self.setWindowTitle('Shannon-Fano Tree Generator')
        self.show()

    def generate_input_fields(self):
        """Generates input fields in the table based on the number of symbols."""
        try:
            num_symbols = int(self.num_symbols_input.text())
            self.table.setRowCount(num_symbols)
            for i in range(num_symbols):
                self.table.setItem(i, 0, QTableWidgetItem(""))
                self.table.setItem(i, 1, QTableWidgetItem(""))
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number of symbols.")

    def generate_tree(self):
        """Generates the Shannon-Fano tree and renders the animation."""
        symbols = []
        probabilities = []
        for row in range(self.table.rowCount()):
            symbol_item = self.table.item(row, 0)
            prob_item = self.table.item(row, 1)
            if symbol_item and prob_item:
                symbol = symbol_item.text()
                prob_text = prob_item.text()
                if symbol and prob_text:
                    symbols.append(symbol)
                    try:
                        probabilities.append(float(prob_text))
                    except ValueError:
                        QMessageBox.warning(
                            self, "Invalid Input", f"Invalid probability for symbol {symbol}"
                        )
                        return
                else:
                    QMessageBox.warning(
                        self, "Incomplete Input", "Please fill all symbol and probability fields."
                    )
                    return
            else:
                QMessageBox.warning(
                    self, "Incomplete Input", "Please fill all symbol and probability fields."
                )
                return

        if not np.isclose(sum(probabilities), 1.0):
            QMessageBox.warning(self, "Invalid Input", "Probabilities must sum up to 1.")
            return

        # Instead of asking for a file path, we'll use a fixed file path
        file_path = os.path.abspath(
            "C:/Users/dmriv/Documents/GitHub/Quickfins/Huffman-animations/media/videos/1080p60/ShannonFanoTree.mp4"
        )

        # Ensure the directory exists
        output_dir = os.path.dirname(file_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        scene = ShannonFanoTree(symbols, probabilities)
        # Set output file path
        config.output_file = file_path
        scene.render()

        # Open the video externally
        self.open_video_externally(file_path)

    def open_video_externally(self, file_path):
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", file_path])
        else:  # Linux and others
            subprocess.call(["xdg-open", file_path])


class VideoPlayerWindow(QWidget):
    """Window to play the rendered Shannon-Fano tree animation."""

    def __init__(self, video_path):
        super().__init__()
        self.init_ui(video_path)

    def init_ui(self, video_path):
        """Initializes the video player interface."""
        layout = QVBoxLayout()

        self.web_view = QWebEngineView()

        # Correctly format the video URL
        video_url = QUrl.fromLocalFile(video_path)
        video_url_str = video_url.toString()

        html_content = f"""
        <html>
            <body style="margin:0;">
                <video width="100%" height="100%" controls autoplay>
                    <source src="{video_url_str}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </body>
        </html>
        """
        self.web_view.setHtml(html_content)
        layout.addWidget(self.web_view)

        self.setLayout(layout)
        self.setWindowTitle("Shannon-Fano Tree Video")
        self.resize(640, 480)



    def play(self):
        """Toggles play and pause for the video."""
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def media_status_changed(self, status):
        """Updates the play button text based on media status."""
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.play_button.setText("Pause")
        else:
            self.play_button.setText("Play")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InputWindow()
    sys.exit(app.exec())
