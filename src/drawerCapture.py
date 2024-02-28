import sys
import logging
import logging.config
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import QSize

from utils import load_style_sheet
from widgets import MainWidget 

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

logger.info("starting application")

class MainWindow(QMainWindow):
    """
    The main window of the DrawerCapture application.

    Attributes:
        widgets (dict): A dictionary containing the main, live, and image widgets.
        stackedWidget (QStackedWidget): A stacked widget containing all the widgets.
    """

    def __init__(self):
        """
        Initializes the main window.
        """
        logger.debug("initializing main window")
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface.
        """
        self.setFixedSize(QSize(1700, 1100))
        # Set the window title and size
        self.setWindowTitle("DrawerCapture")
        self.setCentralWidget(MainWidget())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    STYLES = ["Photoxo", "Combinear", "Diffnes", "SyNet"]
    CURRENT_STYLE = STYLES[2]
    # switch to the Photoxo style
    app.setStyleSheet(load_style_sheet(CURRENT_STYLE))
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())