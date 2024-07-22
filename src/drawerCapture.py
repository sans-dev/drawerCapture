import sys
from argparse import ArgumentParser
import logging
import logging.config
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QToolBar
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize, Qt

from src.utils.load_style_sheet import load_style_sheet
from src.widgets.MainWidget import MainWidget
from src.widgets.LiveWidget import LiveWidget 
from src.db.DB import DBAdapter, FileAgnosticDB
from src.widgets.Project import ProjectCreator, ProjectLoader, ProjectViewer, LoginWidget
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

    def __init__(self, taxonomy, geo_data_dir, fs, db):
        """
        Initializes the main window.
        """
        logger.debug("initializing main window")
        super().__init__()
        logger.info("initlializing taxonomy")
        self.db = db
        self.db_adapter = DBAdapter(db_manager=self.db)
        project_creator = ProjectCreator(self.db_adapter)
        project_loader = ProjectLoader(self.db_adapter)
        project_viewer = ProjectViewer(self.db_adapter)
        liveWidget = LiveWidget(db_adapter = self.db_adapter, taxonomomy=taxonomy, geo_data_dir=geo_data_dir, fs=fs, panel_res=(1024,780))

        self.widgets = {
            "main": project_viewer,
            "live": liveWidget,
            "create": project_creator,
            "load" : project_loader,
            'project': project_viewer
        }
        self.stackedWidget = QStackedWidget()
        for widget in self.widgets.values():
            self.stackedWidget.addWidget(widget)
            widget.changed.connect(self.switchWidget)

        self.setWindowIcon(QIcon('resources/assets/logo.png')) 
        
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")
        help_menu = menu_bar.addMenu("Help")

        # Create actions
        new_project_action = QAction(QIcon('resources/assets/add.png'), "New Project", self)
        new_project_action.setStatusTip("Create a new capture project")
        file_menu.addAction(new_project_action)
        open_project_action = QAction(QIcon('resources/assets/open.png'), "Open Project", self)
        file_menu.addAction(open_project_action)
        file_menu.addSeparator()
        self.admin_login_action = QAction(QIcon('resources/assets/admin.png'), "Admin Login", self)
        file_menu.addAction(self.admin_login_action)
        file_menu.addSeparator()
        exit_action = QAction(QIcon('resources/assets/close.png'), "Exit", self)
        file_menu.addAction(exit_action)
        file_menu.addSeparator()
        file_menu.addSection("Session Actions")
        new_session_action = QAction(QIcon('resources/assets/capture_mode.png'), "New Capture Session", self)
        file_menu.addAction(new_session_action)

        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16,16))
        self.addToolBar(toolbar)
        toolbar.addAction(new_project_action)
        toolbar.addAction(open_project_action)
        toolbar.addSeparator()
        toolbar.addAction(self.admin_login_action)
        toolbar.addSeparator()
        toolbar.addAction(new_session_action)

        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)


        new_project_action.triggered.connect(self.create_project)
        open_project_action.triggered.connect(self.load_project)
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface.
        """
        # self.setFixedSize(QSize(1700, 1100))
        # Set the window title and size
        self.setWindowTitle("Drawer Capture")
        
        self.setCentralWidget(self.stackedWidget)
        self.stackedWidget.setCurrentWidget(self.widgets['project'])
        
    def switchWidget(self, widget):
        """
        Switches to the specified widget.

        Args:
            widget (str): The name of the widget to switch to.
        """
        logger.debug("switching to widget: %s", widget)
        self.stackedWidget.setCurrentWidget(self.widgets[widget])

    def create_project(self):
        self.setEnabled(False)
        self.project_creator = ProjectCreator(self.db_adapter)
        self.project_creator.close_signal.connect(self.setEnabled)
        self.project_creator.show()

    def load_project(self):
        self.setEnabled(False)
        self.loader = ProjectLoader(self.db_adapter)
        self.loader.close_signal.connect(self.setEnabled)
        self.loader.load_successful.connect(self.on_load_successful)
        self.loader.show()
        
    def login(self):
        self.setEnabled(False)
        self.login_widget = LoginWidget(self.db_adapter)
        self.login_widget.login_successful.connect(self.on_login_successful)
        self.login_widget.close_signal.connect(self.setEnabled)
        self.login_widget.show()

    def on_login_successful(self):
        # enable project edit options
        pass

    def on_load_successful(self):
        self.admin_login_action.triggered.connect(self.login)

if __name__ == '__main__':
    from src.configs.DataCollection import *

    styles = ["Default", "Photoxo", "Combinear", "Diffnes", "SyNet", "PicPax"]
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
    app.setWindowIcon(QIcon('resources/assets/logo.png'))
    if args.style != styles[0]:
        app.setStyleSheet(load_style_sheet(args.style))
    db = FileAgnosticDB()
    mainWindow = MainWindow(taxonomy, geo_data_dir=geo_data_dir, fs=args.fs, db=db)
    mainWindow.show()
    sys.exit(app.exec())