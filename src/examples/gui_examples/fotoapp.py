import sys
import subprocess
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmapCache
QPixmapCache.setCacheLimit(512 * 1024 * 1024)

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Camera App")
        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_image)

        vbox = QVBoxLayout()
        vbox.addWidget(self.preview_label)
        vbox.addWidget(self.capture_button)
        self.setLayout(vbox)

        # Start the timer to update the live preview every 50 milliseconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(500)

    def update_preview(self):
        max_width = 640
        pixmap = QPixmap(r"data\tmp\DSCF0678.jpg")
        if pixmap.width() > max_width:
            pixmap = pixmap.scaledToWidth(max_width)
            
        self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def capture_image(self):
        # Use gphoto2 to capture a still image from the camera and save it to a file
        pass
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec())