# file path: main.py

from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Resizable Panels with QSplitter")

        # Create the main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create the layout for the main widget
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Create a QSplitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create left and right panels
        left_panel = QTextEdit("Left Panel")
        right_panel = QTextEdit("Right Panel")

        # Add panels to the splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)

        # Set initial proportions (optional)
        splitter.setSizes([200, 200])

        # Add the splitter to the layout
        layout.addWidget(splitter)

        # Set the initial size of the main window
        self.resize(600, 400)

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
