import sys
from argparse import ArgumentParser
import logging
import logging.config
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QToolBar
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize, Qt

from src.utils.load_style_sheet import load_style_sheet
from src.widgets.CaptureView import CaptureView
from src.widgets.ImageWidget import ImageWidget
from src.db.DB import DBAdapter, FileAgnosticDB
from src.widgets.Project import ProjectCreator, ProjectLoader, ProjectViewer, LoginWidget, UserManager, UserSettings
from src.utils.searching import init_taxonomy

logging.config.fileConfig('configs/logging.conf',
                          disable_existing_loggers=False)
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
        super().__init__()
        logger.debug("initializing main window")
        self.db = db
        self.db_adapter = DBAdapter(db_manager=self.db)
        self.taxonomy = taxonomy
        self.geo_data_dir = geo_data_dir
        self.fs = fs

        self.initUI()
        self.disable_admin_features()
        self.connect_signals()

    def initUI(self):
        """
        Initializes the user interface.setWindowTitle
        """
        self.mode = "Project Mode"
        self.current_user = None
        self.project_name = ''
        self.set_window_title()
        self.setGeometry(0, 0, 1920, 1024)
        self.setWindowIcon(QIcon('resources/assets/logo.png'))
        self.stacked_widget = QStackedWidget(self)
        self.project_view = ProjectViewer(self.db_adapter)
        self.capture_view = CaptureView(db_adapter=self.db_adapter,
                                       fs=self.fs, panel_res=(1024, 780))
        # self.image_view = ImageWidget(
        #    db_adapter=db_adapter, taxonomy=taxonomomy, geo_data_dir=geo_data_dir)
        self.stacked_widget.addWidget(self.project_view)
        self.stacked_widget.addWidget(self.capture_view)
        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.setCurrentWidget(self.project_view)
        self.create_menus()
        self.create_actions()
        self.setup_toolbar()

    def set_window_title(self):
        username = self.current_user['username'] if self.current_user is not None else ''
        title = f"Drawer Capture - {self.mode} - {self.project_name} - {username}"
        self.setWindowTitle(title)

    def create_menus(self):
        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu("File")
        self.user_menu = menu_bar.addMenu("User")
        edit_menu = menu_bar.addMenu("Edit")
        self.project_menu = edit_menu.addMenu('Project')
        self.help_menu = menu_bar.addMenu("Help")

    def create_actions(self):
        # File menu actions
        self.new_project_action = QAction(
            QIcon('resources/assets/add.png'), "New Project", self)
        self.open_project_action = QAction(
            QIcon('resources/assets/open.png'), "Open Project", self)
        self.exit_action = QAction(
            QIcon('resources/assets/close.png'), "Exit", self)
        self.new_session_action = QAction(
            QIcon('resources/assets/add2.png'), "New Capture Session", self)
        # self.new_session_action.setEnabled(False)

        # Project menu actions
        self.manage_user_action = QAction(QIcon(
            'resources/assets/user-management-icon-2048x2048-kv1zlmf8.png'), "Manage Users", self)
        self.manage_museums_action = QAction(
            QIcon('resources/assets/museum.png'), "Manage Museums", self)

        # User menu actions
        self.login_action = QAction(
            QIcon('resources/assets/user.png'), "Change User", self)
        self.user_settings = QAction(
            QIcon('resources/assets/user_settings.png'), "User Settings", self)

        # Add actions to menus
        self.file_menu.addAction(self.new_project_action)
        self.file_menu.addAction(self.open_project_action)
        self.file_menu.addSeparator()
        self.file_menu.addSection("Session Actions")
        self.file_menu.addAction(self.new_session_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.project_menu.addAction(self.manage_user_action)
        self.project_menu.addAction(self.manage_museums_action)

        self.user_menu.addAction(self.login_action)
        self.user_menu.addSeparator()
        self.user_menu.addAction(self.user_settings)

        self.set_enabled_user_actions(False)

    def setup_toolbar(self):
        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        toolbar.addAction(self.new_project_action)
        toolbar.addAction(self.open_project_action)
        toolbar.addSeparator()
        toolbar.addAction(self.manage_user_action)
        toolbar.addAction(self.user_settings)
        toolbar.addSeparator()
        toolbar.addAction(self.new_session_action)

        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

    def connect_signals(self):
        self.login_action.triggered.connect(self.login)
        self.new_project_action.triggered.connect(self.create_project)
        self.open_project_action.triggered.connect(self.load_project)
        self.manage_user_action.triggered.connect(self.open_user_manager)
        self.user_settings.triggered.connect(self.edit_user)
        self.new_session_action.triggered.connect(self.new_session)

    def new_session(self):
        self.stacked_widget.setCurrentWidget(self.capture_view)
        self.mode = "Capture Mode"
        self.set_window_title()

    def edit_user(self):
        self.user_settings = UserSettings(self.db_adapter, self.current_user)
        self.user_settings.close_signal.connect(self.setEnabled)
        self.setEnabled(False)
        self.user_settings.show()

    def create_project(self):
        self.setEnabled(False)
        self.project_creator = ProjectCreator(self.db_adapter)
        self.project_creator.close_signal.connect(self.setEnabled)
        self.project_creator.create_successfull.connect(
            self.on_create_successful)
        self.project_creator.show()

    def load_project(self):
        self.setEnabled(False)
        self.loader = ProjectLoader(self.db_adapter)
        self.loader.close_signal.connect(self.setEnabled)
        self.loader.load_successful.connect(self.on_load_successful)
        self.loader.show()

    def login(self):
        self.login_widget = LoginWidget(self.db_adapter)
        self.login_widget.login_successful.connect(self.on_login_successful)
        self.login_widget.close_signal.connect(self.setEnabled)
        self.login_widget.show()
        self.setEnabled(False)

    def open_user_manager(self):
        self.user_manager = UserManager(self.db_adapter, self.current_user)
        self.user_manager.close_signal.connect(self.setEnabled)
        self.user_manager.show()

    def update_ui_based_on_role(self):
        self.new_session_action.setEnabled(True)
        if self.current_user['role'] == 'admin':
            self.enable_admin_features()
        else:
            self.disable_admin_features()

    def enable_admin_features(self):
        # Show admin-only buttons, menus, etc.
        self.project_menu.setEnabled(True)
        self.manage_museums_action.setEnabled(True)
        self.manage_user_action.setEnabled(True)

    def set_enabled_user_actions(self, is_enabled):
        self.login_action.setEnabled(is_enabled)
        self.user_settings.setEnabled(is_enabled)

    def disable_admin_features(self):
        # Hide admin-only buttons, menus, etc.
        self.manage_museums_action.setEnabled(False)
        self.manage_user_action.setEnabled(False)

    def on_login_successful(self, user):
        # enable project edit options
        self.current_user = user
        print(
            f"Login successful! Welcome, {user['username']} ({user['role']})")
        self.update_ui_based_on_role()
        self.set_window_title()

    def on_load_successful(self):
        self.project_name = self.loader.get_project_name()
        self.loader.close()
        self.login()
        self.set_enabled_user_actions(True)

    def on_create_successful(self):
        self.project_name = self.project_creator.get_project_name()
        self.project_creator.close()
        self.login()
        self.set_enabled_user_actions(True)


if __name__ == '__main__':
    from src.configs.DataCollection import *

    styles = ["Default", "Photoxo", "Combinear", "Diffnes", "SyNet", "PicPax"]
    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true",
                        help="enable debug mode")
    parser.add_argument("--style", type=str, choices=styles,
                        help="set the style", default=styles[0])
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
    mainWindow = MainWindow(
        taxonomy, geo_data_dir=geo_data_dir, fs=args.fs, db=db)
    mainWindow.show()
    sys.exit(app.exec())
