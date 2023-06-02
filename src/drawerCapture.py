import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from utils.load_style_sheet import *
from widgets import MainWidget
from widgets import LiveWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widgets = {
            "main": MainWidget(),
            "live": LiveWidget()
        }
        self.stackedWidget = QStackedWidget()
        for widget in self.widgets.values():
            self.stackedWidget.addWidget(widget)
            widget.changed.connect(self.switchWidget)

        self.initUI()

    def initUI(self):
        # Set the window title and size
        self.setWindowTitle("DrawerCapture")
        self.setGeometry(1500, 1000, 1200, 500)

        self.setCentralWidget(self.stackedWidget)

    def switchWidget(self, widget):
        self.stackedWidget.setCurrentWidget(self.widgets[widget])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # switch to the Photoxo style
    app.setStyleSheet(load_combinear_style_sheet())
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())