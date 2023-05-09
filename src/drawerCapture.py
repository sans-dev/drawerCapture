import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QMainWindow, QLabel, QComboBox
from PyQt6.QtGui import QScreen

from utils.load_style_sheet import *
from widgets.LiveModeWindow import LiveModeWindow

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Set the window title and size
        self.setWindowTitle("DrawerCapture")
        self.setGeometry(1000, 500, 800, 800)

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

        # Create a new window for live mode
        self.liveModeWindow = LiveModeWindow()
        self.liveModeWindow.hide()
        self.liveModeWindow.liveModeClosedSignal.signal.connect(self.show)
        self.show()
        self.centerWindowMainMonitor()
        

    def centerWindowMainMonitor(self):
        # Get the screen resolution
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def enterOfflineMode(self):
        pass

    def enterLiveMode(self):
        # create a new window for live mode
        self.hide()
        self.liveModeWindow.show()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # switch to the Photoxo style
    app.setStyleSheet(load_combinear_style_sheet())
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())