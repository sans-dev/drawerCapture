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
from src.widgets.PreviewPanel import PreviewPanel
from src.widgets.SelectCameraListWidget import SelectCameraListWidget
from src.db.DB import DBAdapter, FileAgnosticDB, DummyDB
from src.widgets.Project import (ProjectCreator, ProjectLoader, ProjectViewer, LoginWidget, 
                                 UserManager, MuseumManager, UserSettings, SessionCreator, ProjectMerger) 
from src.utils.searching import init_taxonomy

logging.config.fileConfig('configs/logging/logging.conf',
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
        self.mode = "Default Mode"
        self.current_user = None
        self.project_name = ''
        self.is_creating_project = False
        self.camera_connected = False
        self.initUI()
        self.set_enabled_admin_features(False)
        self.update_ui_based_on_mode()
        self.connect_signals()

    def initUI(self):
        """
        Initializes the user interface.setWindowTitle
        """
        self.set_window_title()
        self.setGeometry(0, 0, 1920, 1024)
        self.setWindowIcon(QIcon('assets/icons/app_icon.png'))
        self.stacked_widget = QStackedWidget(self)
        self.project_view = ProjectViewer(self.db_adapter)

        self.image_view = ImageWidget(
            db_adapter=self.db_adapter, 
            taxonomy=self.taxonomy, 
            geo_data_dir=geo_data_dir, 
            panel=PreviewPanel(fs=self.fs, panel_res=(1024, 780)))
        self.capture_view = CaptureView(db_adapter=self.db_adapter,
                                       panel=PreviewPanel(fs=self.fs, panel_res=(1024, 780)))

        self.stacked_widget.addWidget(self.project_view)
        self.stacked_widget.addWidget(self.capture_view)
        self.stacked_widget.addWidget(self.image_view)
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
            QIcon('assets/icons/add.png'), "New Project", self)
        self.open_project_action = QAction(
            QIcon('assets/icons/open.png'), "Open Project", self)
        self.exit_action = QAction(
            QIcon('assets/icons/close.png'), "Exit", self)
        self.new_session_action = QAction(
            QIcon('assets/icons/add2.png'), "New Capture Session", self)
        # self.new_session_action.setEnabled(False)

        # Project menu actions
        self.manage_user_action = QAction(QIcon(
            'assets/icons/user-management-icon-2048x2048-kv1zlmf8.png'), "Manage Users", self)
        self.manage_museums_action = QAction(
            QIcon('assets/icons/museum.png'), "Manage Museums", self)
        self.merge_projects_action = QAction(
            QIcon('assets/icons/add2.png'), "Merge Projects", self)

        # User menu actions
        self.login_action = QAction(
            QIcon('assets/icons/user.png'), "Change User", self)
        self.user_settings = QAction(
            QIcon('assets/icons/user_settings.png'), "User Settings", self)
        
        # Camera Settings
        self.add_camera_action = QAction(
            QIcon("assets/icons/camera_off.png"), "Connect Camera", self)

        # Capture mode actions
        self.capture_image = QAction(
            QIcon("assets/icons/capture_image.png"), "Capture Image", self)
        self.start_live_preview = QAction(
            QIcon("assets/icons/play.png"), "Capture Image", self)
        self.stop_live_preview = QAction(
            QIcon("assets/icons/stop.png"), "Capture Image", self)

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
        self.project_menu.addSeparator()
        self.project_menu.addAction(self.merge_projects_action)
        
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
        toolbar.addAction(self.manage_museums_action)
        toolbar.addSeparator()
        toolbar.addAction(self.new_session_action)
        toolbar.addAction(self.add_camera_action)
        toolbar.addSeparator()
        toolbar.addAction(self.start_live_preview)
        toolbar.addAction(self.stop_live_preview)
        toolbar.addAction(self.capture_image)
        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

    def connect_signals(self):
        self.login_action.triggered.connect(self.login)
        self.new_project_action.triggered.connect(self.create_project)
        self.open_project_action.triggered.connect(self.load_project)
        self.manage_user_action.triggered.connect(self.open_user_manager)
        self.user_settings.triggered.connect(self.edit_user)
        self.new_session_action.triggered.connect(self.new_session)
        self.manage_museums_action.triggered.connect(self.manage_museums)
        self.add_camera_action.triggered.connect(self.add_camera)
        self.capture_image.triggered.connect(self.capture_view.capture_image)
        self.capture_view.save_button.clicked.connect(self.on_save_image)
        self.exit_action.triggered.connect(self.exit_application)
        self.capture_view.panel.image_captured.connect(self.image_view.panel.on_image_captured)
        self.capture_view.close_signal.connect(self.on_capture_mode_ended)
        self.db_adapter.project_changed_signal.connect(self.capture_view.panel.set_image_dir)
        self.image_view.close_signal.connect(self.on_data_collected)
        self.merge_projects_action.triggered.connect(self.merge_projects)

    def exit_application(self):
        self.close()

    def merge_projects(self):
        source_project_adapter = DBAdapter(FileAgnosticDB())
        self.project_merger = ProjectMerger(target_project_adapter=self.db_adapter, 
                                            soure_project_adapter=source_project_adapter)
        self.setEnabled(False)
        self.project_merger.close_signal.connect(self.setEnabled)
        self.project_merger.show()

    def manage_museums(self):
        self.museum_manager = MuseumManager(self.db_adapter, self.db_adapter.get_current_user())
        self.museum_manager.show()

    def new_session(self):
        self.session_creator = SessionCreator(self.db_adapter,[])
        self.setEnabled(False)
        self.session_creator.set_user(self.db_adapter.get_current_user())
        self.session_creator.set_museums(self.db_adapter.get_museums())
        self.session_creator.session_created.connect(self.on_session_created)
        self.session_creator.close_signal.connect(self.setEnabled)
        self.session_creator.show()

    def edit_user(self):
        self.user_settings = UserSettings(self.db_adapter, self.current_user)
        self.user_settings.close_signal.connect(self.setEnabled)
        self.setEnabled(False)
        self.user_settings.show()

    def create_project(self):
        self.setEnabled(False)
        self.is_creating_project = True
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
            self.set_enabled_admin_features(True)
        else:
            self.set_enabled_admin_features(False)

    def update_ui_based_on_mode(self):
        if self.mode =='Default Mode': # no project loaded
            self.set_enabled_project_features(True)
            self.set_enabled_capture_features(False)
        if self.mode == 'Project Mode': # Project loaded
            self.set_enabled_project_features(True)
            self.set_enabled_capture_features(True)
            self.stacked_widget.setCurrentWidget(self.project_view)
        elif self.mode == 'Data Collection Mode': # image view active
            self.set_enabled_project_features(False)
            self.set_enabled_capture_features(False)
            self.stacked_widget.setCurrentWidget(self.image_view)
        elif self.mode == 'Capture Mode': # capture view is active
            self.set_enabled_project_features(False)
            self.set_enabled_capture_features(True)
            self.stacked_widget.setCurrentWidget(self.capture_view)
        self.set_window_title()

    def set_enabled_capture_features(self, is_enabled):
        self.start_live_preview.setEnabled(is_enabled)
        self.stop_live_preview.setEnabled(is_enabled)
        self.capture_image.setEnabled(is_enabled)
        self.add_camera_action.setEnabled(is_enabled)
        self.new_session_action.setEnabled(is_enabled) #Enable later. leave now for testing

    def set_enabled_project_features(self, is_enabled):
        self.new_project_action.setEnabled(is_enabled)
        self.open_project_action.setEnabled(is_enabled)
        self.exit_action.setEnabled(is_enabled)

    def set_enabled_admin_features(self, is_enabled):
        # Show admin-only buttons, menus, etc.
        self.manage_museums_action.setEnabled(is_enabled)
        self.manage_user_action.setEnabled(is_enabled)

    def set_enabled_user_actions(self, is_enabled):
        self.login_action.setEnabled(is_enabled)
        self.user_settings.setEnabled(is_enabled)

    def on_login_successful(self, user):
        # enable project edit options
        self.current_user = user
        print(
            f"Login successful! Welcome, {user['username']} ({user['role']})")
        self.update_ui_based_on_role()
        self.set_window_title()

        if self.is_creating_project:
            self.open_user_manager_for_project()
        else:
            self.set_enabled_user_actions(True)

    def add_camera(self):
        self.setEnabled(False)
        self.camera_fetcher = SelectCameraListWidget()
        self.camera_fetcher.close_signal.connect(self.setEnabled)
        self.camera_fetcher.camera_selected.connect(self.on_camera_selected)
        self.camera_fetcher.show()

    def on_camera_selected(self, camera):
        self.camera_fetcher.close()
        self.project_view.set_camera_data(camera)
        self.camera_connected = True
        self.capture_view.set_camera_data(camera)

    def on_session_created(self):
        self.session_creator.close()
        self.mode = "Capture Mode"
        self.update_ui_based_on_mode()
        if not self.camera_connected:
            self.add_camera()

    def on_load_successful(self):
        self.project_name = self.loader.get_project_name()
        self.loader.close()
        self.login()
        self.set_enabled_user_actions(True)

    def on_create_successful(self):
        self.project_name = self.project_creator.get_project_name()
        self.project_creator.close()
        self.login()

    def on_save_image(self):
        self.mode = "Data Collection Mode"
        self.update_ui_based_on_mode()

    def on_data_collected(self):
        self.mode = "Capture Mode"
        self.update_ui_based_on_mode()

    def on_capture_mode_ended(self):
        self.mode = "Project Mode"
        self.update_ui_based_on_mode()

    def open_user_manager_for_project(self):
        self.user_manager = UserManager(self.db_adapter, self.current_user)
        self.user_manager.close_signal.connect(self.finish_project_creation)
        self.user_manager.show()

    def finish_project_creation(self):
        self.is_creating_project = False
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
        db = FileAgnosticDB()
    else:
        logger.setLevel(level=logging.INFO)
        logger.debug("debug mode disabled")
        logger.info("loading taxonomy")
        taxonomy = init_taxonomy(TAXONOMY['prod'])
        db = FileAgnosticDB()
    geo_data_dir = GEO[args.geo_data]

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('assets/icons/app_icon.png'))
    if args.style != styles[0]:
        app.setStyleSheet(load_style_sheet(args.style))

    mainWindow = MainWindow(
        taxonomy, geo_data_dir=geo_data_dir, fs=args.fs, db=db)
    mainWindow.show()
    sys.exit(app.exec())
