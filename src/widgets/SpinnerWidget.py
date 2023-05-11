from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import  QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QSize


class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Set the widget's layout as a vertical box layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Create a QLabel to display the GIF image
        self.label = QLabel(self)
        layout.addWidget(self.label)

        # Load and start the GIF animation
        self.movie = QMovie("resources/assets/Spinner-1s-200px.gif")
        # make movie smaller
        self.movie.setScaledSize(QSize(100, 100))
        self.label.setMovie(self.movie)

    def start(self):
        self.movie.start()

    def stop(self):
        self.movie.stop()