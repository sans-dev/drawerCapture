import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication, QPainter
from PyQt6.QtWidgets import QApplication, QWidget

# Create a custom widget for the loading spinner
class LoadingSpinner(QWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(20)  # Set the animation update interval in milliseconds

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set the size and position of the spinner
        size = min(self.width(), self.height())
        x = (self.width() - size) // 2
        y = (self.height() - size) // 2

        # Draw the spinner using CSS
        css = """
        background-color: transparent;
        border: 5px solid #f3f3f3;
        border-top: 5px solid #3498db;
        border-radius: 50%;
        """
        painter.save()
        painter.translate(x + size / 2, y + size / 2)
        painter.rotate(self.angle)
        painter.drawEllipse(-size / 2, -size / 2, size, size)
        painter.restore()

        self.angle += 1

# Create the main application window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading Spinner")
        self.resize(200, 200)
        self.spinner = LoadingSpinner()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.GlobalColor.white)

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
