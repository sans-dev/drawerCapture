import sys
import logging
import logging.config
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from utils import load_style_sheet
from widgets import MainWidget, LiveWidget, ImageWidget
from db import DBAdapter, DBManager

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
        self.dbAdapter = DBAdapter()
        self.dbManager = DBManager('tests/test-project')
        self.dbManager.connect_db_adapter(self.dbAdapter)

        imageWidget = ImageWidget(self.dbAdapter)
        self.widgets = {
            "main": MainWidget(),
            "live": LiveWidget(imageWidget),
            "image": imageWidget
        }
        self.stackedWidget = QStackedWidget()
        for widget in self.widgets.values():
            self.stackedWidget.addWidget(widget)
            widget.changed.connect(self.switchWidget)

        self.initUI()

    def initUI(self):
        """
        Initializes the user interface.
        """
        # self.setFixedSize(QSize(1700, 1100))
        # Set the window title and size
        self.setWindowTitle("DrawerCapture")
        self.setCentralWidget(self.stackedWidget)

    def switchWidget(self, widget):
        """
        Switches to the specified widget.

        Args:
            widget (str): The name of the widget to switch to.
        """
        logger.debug("switching to widget: %s", widget)
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