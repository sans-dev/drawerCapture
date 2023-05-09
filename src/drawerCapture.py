import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from utils.load_style_sheet import *
from widgets.MainWindowWidget import MainWindowWidget
from signals.WidgetSignal import WidgetSignal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.modeSignal = WidgetSignal()
        self.initUI()

    def initUI(self):
        # Set the window title and size
        self.setWindowTitle("DrawerCapture")
        self.setGeometry(1000, 500, 800, 800)
        self.mainWindowUI = MainWindowWidget(modeSignal=self.modeSignal)
        self.modeSignal.modeChanged.connect(self.setCentralWidget)
        self.mainWindowUI.show()


    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # switch to the Photoxo style
    app.setStyleSheet(load_combinear_style_sheet())
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())