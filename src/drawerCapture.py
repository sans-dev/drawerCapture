import sys
import logging
import logging.config
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import QSize

from utils import load_style_sheet
from widgets import MainView, ProjectView
from widgets import ProjectCreationView

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

logger.info("starting application")

class MainWindow(QMainWindow):
    """
    The main window of the DrawerCapture application.

    Attributes:
        widgets (dict): A dictionary containing the main, live, and image widgets.
        stacked_widget (QStackedWidget): A stacked widget containing all the widgets.
    """

    def __init__(self):
        """
        Initializes the main window.
        """
        logger.debug("initializing main window")
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface.
        """
        self.setFixedSize(QSize(1700, 1100))
        # Set the window title and size
        self.setWindowTitle("DrawerCapture")

        # create Views
        self.main_view = MainView()
        self.project_view = ProjectView()

        # Create the stacked widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.main_view)
        self.stacked_widget.addWidget(self.project_view)
        
        # connect signals
        self.main_view.new_project_requested.connect(self.open_project_creation_view)
        self.main_view.open_project_requested.connect(self.open_project_loading_view)

        self.setCentralWidget(self.stacked_widget)

    def open_project_creation_view(self):
        """
        Opens the project creation widget.
        """
        logger.debug("opening project creation widget")
        self.project_creation_widget = ProjectCreationView()
        self.project_creation_widget.request_open_project_view.connect(self.open_project_view)
        self.stacked_widget.addWidget(self.project_creation_widget)
        self.stacked_widget.setCurrentWidget(self.project_creation_widget)

    def open_project_loading_view(self):
        """
        Opens the project loading widget.
        """
        logger.debug("opening project loading widget")
        pass

    def open_project_view(self):
        """
        Opens the project view widget.
        """
        logger.debug("opening project view widget")
        self.stacked_widget.setCurrentWidget(self.project_view)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    STYLES = ["Photoxo", "Combinear", "Diffnes", "SyNet"]
    CURRENT_STYLE = STYLES[1]
    # switch to the Photoxo style
    app.setStyleSheet(load_style_sheet(CURRENT_STYLE))
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())