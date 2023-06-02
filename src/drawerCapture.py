import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from utils import load_style_sheet
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
    STYLES = ["Photoxo", "Combinear", "Diffnes", "SyNet"]
    CURRENT_STYLE = STYLES[3]
    # switch to the Photoxo style
    app.setStyleSheet(load_style_sheet(CURRENT_STYLE))
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())