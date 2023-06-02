from PyQt6.QtGui import QMovie, QIcon
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel
from PyQt6.QtCore import Qt

from ..utils import load_style_sheet

class RefreshButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setText("Refresh")

        self.textLabel = QLabel("Refresh", self)
        self.textLabel.setGeometry(0, 0, self.width(), self.height())
        self.textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # make label larger so it fits the size of the spinner

        self.movie = QMovie(self)
        self.movie.setFileName(r"resources\assets\loading_spinner.gif")  # Replace with the actual path to your GIF file
        self.movie.frameChanged.connect(self.update_button_icon)
        self.setIcon(QIcon(self.movie.currentPixmap()))

        self.clicked.connect(self.on_button_clicked)

    def on_button_clicked(self):
        self.textLabel.hide()
        self.movie.start()

    def update_button_icon(self, frame_number):
        movie = self.sender()
        if movie:
            pixmap = movie.currentPixmap()
            self.setIcon(QIcon(pixmap))
            self.setIconSize(pixmap.size()/2)


if __name__ == '__main__':
    app = QApplication([])
    window = RefreshButton()
    window.setGeometry(300, 300, 300, 200)
    window.setStyleSheet(load_style_sheet("Combinear"))
    window.show()
    app.exec()
