import sys
from argparse import ArgumentParser
import logging
import logging.config
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from src.utils.load_style_sheet import load_style_sheet
from src.widgets.MainWidget import MainWidget
from src.widgets.LiveWidget import LiveWidget 
from src.db.DB import DBAdapter, FileAgnosticDB
from src.widgets.Project import ProjectCreator, ProjectLoader, ProjectViewer
from src.utils.searching import init_taxonomy

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

    def __init__(self, taxonomy, geo_data_dir, fs):
        """
        Initializes the main window.
        """
        logger.debug("initializing main window")
        super().__init__()
        logger.info("initlializing taxonomy")
        self.db = FileAgnosticDB()
        self.db_adapter = DBAdapter(db_manager=self.db)
        project_creator = ProjectCreator(self.db_adapter)
        project_loader = ProjectLoader(self.db_adapter)
        project_viewer = ProjectViewer(self.db_adapter)
        liveWidget = LiveWidget(db_adapter = self.db_adapter, taxonomomy=taxonomy, geo_data_dir=geo_data_dir, fs=fs)

        self.widgets = {
            "main": MainWidget(),
            "live": liveWidget,
            "create": project_creator,
            "load" : project_loader,
            'project': project_viewer
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
    from src.configs.DataCollection import *

    styles = ["Default", "Photoxo", "Combinear", "Diffnes", "SyNet"]
    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="enable debug mode")
    parser.add_argument("--style", type=str, choices=styles, help="set the style", default=styles[0])
    parser.add_argument('--geo-data', choices=['level-0', 'level-1'])
    parser.add_argument('--fs', type=int, default=1)

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(level=logging.DEBUG)
        logger.debug("debug mode enabled")
        logger.info("loading taxonomy")
        taxonomy = init_taxonomy(TAXONOMY['test'])
    else:
        logger.setLevel(level=logging.INFO)
        logger.debug("debug mode disabled")
        logger.info("loading taxonomy")
        taxonomy = init_taxonomy(TAXONOMY['prod'])
    geo_data_dir = GEO[args.geo_data]
    
    app = QApplication(sys.argv)
    if args.style != styles[0]:
        app.setStyleSheet(load_style_sheet(args.style))
    mainWindow = MainWindow(taxonomy, geo_data_dir=geo_data_dir, fs=args.fs)
    mainWindow.show()
    sys.exit(app.exec())