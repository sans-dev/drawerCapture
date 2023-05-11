from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt
from threads.CameraStreamer import CameraStreamer
from widgets.SpinnerWidget import LoadingSpinner

class PreviewPanel(QLabel):
    def __init__(self):
        super().__init__()
        self.cameraStreamer = CameraStreamer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePreview)
        self.initUI()
    
    def initUI(self):
        # set the size of the preview panel
        panel_size = (int(1920/2), int(1080/2))
        self.setFixedSize(panel_size[0], panel_size[1])
        self.setFrameStyle(1)
        self.setLineWidth(1)

    def updatePreview(self):
        pass