import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt

from utils.load_style_sheet import *
from widgets.LiveModeWindow import LiveModeWindow

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Set the window title and size
        self.setWindowTitle("DrawerCapture")
        self.setGeometry(100, 100, 800, 800)

        # Create the layout
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

        # Show the window
        self.show()

    def enterOfflineMode(self):
        pass

    def enterLiveMode(self):
        # create a new window for live mode
        self.hide()
        self.liveModeWindow = LiveModeWindow()
        self.liveModeWindow.show()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # switch to the Photoxo style
    app.setStyleSheet(load_combiniear_style_sheet())
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())