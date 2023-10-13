import sys
import logging
import logging.config
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import QSize

from utils import load_style_sheet
from widgets import MainWidget, LiveWidget, ImageWidget

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

logger.info("starting application")

class MainWindow(QMainWindow):
    def __init__(self):
        logger.debug("initializing main window")
        super().__init__()
        self.widgets = {
            "main": MainWidget(),
            "live": LiveWidget(),
            "image": ImageWidget()
        }
        self.stackedWidget = QStackedWidget()
        for widget in self.widgets.values():
            self.stackedWidget.addWidget(widget)
            widget.changed.connect(self.switchWidget)

        self.initUI()

    def initUI(self):
        self.setFixedSize(QSize(1200, 900))
        # Set the window title and size
        self.setWindowTitle("DrawerCapture")
        self.setCentralWidget(self.stackedWidget)

    def switchWidget(self, widget):
        logger.debug("switching to widget: %s", widget)
        self.stackedWidget.setCurrentWidget(self.widgets[widget])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    STYLES = ["Photoxo", "Combinear", "Diffnes", "SyNet"]
    CURRENT_STYLE = STYLES[0]
    # switch to the Photoxo style
    app.setStyleSheet(load_style_sheet(CURRENT_STYLE))
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())