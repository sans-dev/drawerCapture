import sys
import logging
import logging.config
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from src.utils.load_style_sheet import load_style_sheet
from src.widgets.MainWidget import MainWidget
from src.widgets.LiveWidget import LiveWidget 
from src.widgets.ImageWidget import ImageWidget
from src.db.DB import DBAdapter, DBManager
from src.widgets.Project import ProjectCreator, ProjectLoader

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
        self.db_adapter = DBAdapter()
        project_creator = ProjectCreator(self.db_adapter)
        project_loader = ProjectLoader(self.db_adapter)
        imageWidget = ImageWidget(self.db_adapter)
        self.widgets = {
            "main": MainWidget(),
            "live": LiveWidget(imageWidget),
            "image": imageWidget,
            "create": project_creator,
            "load" : project_loader
        }
        self.stackedWidget = QStackedWidget()
        for widget in self.widgets.values():
            self.stackedWidget.addWidget(widget)
            widget.changed.connect(self.switchWidget)
        
        self.dbManager = DBManager()
        self.dbManager.connect_db_adapter(self.db_adapter)

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
    # app.setStyleSheet(load_style_sheet(CURRENT_STYLE))
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())