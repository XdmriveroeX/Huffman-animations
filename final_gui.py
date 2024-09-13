import sys
import numpy as np
import os
import platform
import subprocess
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from manim import config
from huffman_visualization import HuffmanTree  # Assuming you modify HuffmanTree accordingly
from Shannon_pygui_final import ShannonFanoTree


class InputWindow(QWidget):
    """GUI window for user input to select algorithm and generate the corresponding tree."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initializes the user interface."""
        layout = QVBoxLayout()

        # Algorithm Selection
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Select Algorithm:"))
        self.algorithm_selector = QComboBox()
        self.algorithm_selector.addItem("Shannon-Fano")
        self.algorithm_selector.addItem("Huffman")
        hbox.addWidget(self.algorithm_selector)
        layout.addLayout(hbox)

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

        # Table for symbol inputs (inputSymbols and probabilities)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Symbol", "Probability"])
        layout.addWidget(self.table)

        # Input for output symbols (for Huffman)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Output Symbols (comma-separated):"))
        self.output_symbols_input = QLineEdit()
        hbox.addWidget(self.output_symbols_input)
        layout.addLayout(hbox)

        # Button to generate tree
        generate_tree_btn = QPushButton("Generate Tree")
        generate_tree_btn.clicked.connect(self.generate_tree)
        layout.addWidget(generate_tree_btn)

        self.setLayout(layout)
        self.setWindowTitle('Tree Generator')
        self.show()

    def generate_input_fields(self):
        """Generates input fields in the table based on the number of symbols."""
        try:
            num_symbols = int(self.num_symbols_input.text())
            self.table.setRowCount(num_symbols)
            for i in range(num_symbols):
                self.table.setItem(i, 0, QTableWidgetItem(""))  # For input symbols
                self.table.setItem(i, 1, QTableWidgetItem(""))  # For probabilities
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number of symbols.")

    def generate_tree(self):
        """Generates the selected algorithm's tree and renders the animation."""
        symbols = []
        probabilities = []
        output_symbols = self.output_symbols_input.text().split(',')

        # Gather inputSymbols and probabilities from the table
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

        # Ensure probabilities sum to 1.0
        if not np.isclose(sum(probabilities), 1.0):
            QMessageBox.warning(self, "Invalid Input", "Probabilities must sum up to 1.")
            return

        # Select algorithm and generate animation
        algorithm = self.algorithm_selector.currentText()

        if algorithm == "Shannon-Fano":
            scene = ShannonFanoTree(symbols, probabilities)
            output_file_name = "ShannonFanoTree.mp4"
        else:
            # Use the outputSymbols provided by the user for Huffman encoding
            if not output_symbols or len(output_symbols) < 2:
                QMessageBox.warning(self, "Invalid Input", "Please provide at least two output symbols.")
                return
            scene = HuffmanTree(symbols, output_symbols, probabilities)  # Passing 3 inputs here
            output_file_name = "HuffmanTree.mp4"

        # Correct file path to save the video
        file_path = os.path.abspath(
            f"C:/Users/dmriv/Documents/GitHub/Quickfins/Huffman-animations/media/videos/1080p60/{output_file_name}"
        )

        # Set the output file path for Manim
        config.output_file = file_path
        scene.render()

        # Open the video externally
        self.open_video_externally(file_path)

    def open_video_externally(self, file_path):
        """Opens the video file after generation."""
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", file_path])
        else:  # Linux and others
            subprocess.call(["xdg-open", file_path])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InputWindow()
    sys.exit(app.exec())
