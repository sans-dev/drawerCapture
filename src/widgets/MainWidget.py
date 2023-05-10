from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout
from PyQt6.QtCore import pyqtSignal
from widgets.LiveWidget import LiveModeWidget
from signals.WidgetSignal import WidgetSignal

class MainWidget(QWidget):
    changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Create the widgets
        self.liveModeButton = QPushButton("Live Mode")
        self.liveModeButton.clicked.connect(self.enterLiveMode)
        self.offlineModeButton = QPushButton("Offline Mode")
        self.offlineModeButton.clicked.connect(self.enterOfflineMode)

        # Add the widgets to the layout
        self.layout.addWidget(self.liveModeButton, 0, 0)
        self.layout.addWidget(self.offlineModeButton, 0, 1)
        
    def enterOfflineMode(self):
        pass

    def enterLiveMode(self):
        self.changed.emit("live")