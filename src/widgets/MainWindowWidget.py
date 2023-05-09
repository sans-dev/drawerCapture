from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout

from widgets.LiveModeWidget import LiveModeWidget

class MainWindowWidget(QWidget):

    def __init__(self, modeSignal=None):
        super().__init__()
        self.modeSignal = modeSignal

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
        self.liveMode = LiveModeWidget(parent=self, modeSignal=self.modeSignal)

    def enterOfflineMode(self):
        pass

    def enterLiveMode(self):
        self.modeSignal.modeChanged.emit(self.liveMode)

    def show(self):
        self.modeSignal.modeChanged.emit(self)