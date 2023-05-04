from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QObject

from widgets.SelectCameraListWidget import SelectCameraListWidget

class LiveModeWindow(QWidget):
    def __init__(self):
        # Set the calling window as the parent
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the window title and size
        self.setWindowTitle("Live Mode")
        self.setGeometry(100, 100, 800, 800)

        # Create the layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Create the widgets
        self.exitModeButton = QPushButton("Exit")
        self.exitModeButton.clicked.connect(self.exitLiveMode)

        self.selectCameraButton = QPushButton("Select Camera")
        self.selectCameraButton.clicked.connect(self.selectCamera)

        # create a live preview for a video stream using label 
        self.livePreviewLabel = QLabel("Live Preview")
        self.livePreviewLabel.setFixedSize(400, 300)
        self.livePreviewLabel.setFrameStyle(1)
        self.livePreviewLabel.setLineWidth(1)
        self.livePreviewLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # disable and hide the label
        self.livePreviewLabel.setEnabled(False)
        self.livePreviewLabel.hide()

        self.selectCameraListWidget = SelectCameraListWidget()
        self.selectCameraListWidget.selectedCameraChanged.signal.connect(self.showLivePreviewOnCameraSelect)
        self.selectCameraListWidget.hide()

        # Add the widgets to the layout
        self.layout.addWidget(self.exitModeButton, 2, 0)
        self.layout.addWidget(self.livePreviewLabel, 1, 0)
        self.layout.addWidget(self.selectCameraButton, 0, 0)

    def selectCamera(self):
        self.selectCameraListWidget.show()

    def showLivePreviewOnCameraSelect(self, cameraName):
        self.livePreviewLabel.setText(cameraName)
        self.livePreviewLabel.show()
        self.selectCameraListWidget.hide()
    
    def exitLiveMode(self):
        self.close()