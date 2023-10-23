from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout
from PyQt6.QtCore import pyqtSignal

class MainWidget(QWidget):
    """
    This class represents the main widget of the DrawerCapture application.
    It contains two buttons to switch between live and offline mode.
    """
    changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface of the main widget.
        """
        self.setWindowTitle("DrawerCapture")

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Create the widgets
        self.liveModeButton = QPushButton("Live Mode")
        self.liveModeButton.clicked.connect(self.enterLiveMode)
        self.offlineModeButton = QPushButton("Offline Mode")
        self.offlineModeButton.clicked.connect(self.enterOfflineMode)

        # Add the widgets to the layout
        self.layout.addWidget(self.liveModeButton, 0, 0, 1, 1)
        self.layout.addWidget(self.offlineModeButton, 0, 1, 1, 1)
        
    def enterOfflineMode(self):
        """
        This method is called when the user clicks the "Offline Mode" button.
        """
        pass

    def enterLiveMode(self):
        """
        This method is called when the user clicks the "Live Mode" button.
        It emits a signal with the string "live".
        """
        self.changed.emit("live")