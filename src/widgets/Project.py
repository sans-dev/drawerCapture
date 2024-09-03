from datetime import datetime
from pathlib import Path
import platform
import os
import subprocess
from PyQt6.QtCore import pyqtSignal, Qt, QDir, QRegularExpression, QAbstractTableModel, QModelIndex, QThread
from PyQt6.QtGui import QIcon, QRegularExpressionValidator, QStandardItemModel, QStandardItem, QAction
from PyQt6.QtWidgets import (QApplication, QDialog, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel, 
                             QListWidget, QHBoxLayout, QTableView, QAbstractItemView, QHeaderView, 
                             QCheckBox, QGridLayout, QMessageBox, QInputDialog, QComboBox, QTextEdit, QDialogButtonBox, QMenu, QProgressBar)
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class OpenDirThread(QThread):
    finished = pyqtSignal()

    def __init__(self, project_dir, parent=None):
        super().__init__(parent)
        self.project_dir = project_dir

    def run(self):
        logger.info("Open directory thread started")
        try:
            if platform.system() == 'Linux':
                out = subprocess.run(['./src/cmds/start_nautilus.sh', str(self.project_dir)])
                if out.returncode != 0:
                    out = subprocess.run(['nautilus', str(self.project_dir)])
                if out.returncode != 0:
                    raise FileNotFoundError("Nautlius is unavailable")

            elif platform.system() == 'Windows':
                os.startfile(self.project_dir)

        except FileNotFoundError as fne:
            # Use a signal to send the error back to the main thread
            self.emit(pyqtSignal('FileNotFoundError'), str(fne)) 
        except Exception as e:
            self.emit(pyqtSignal('Exception'), str(e))
        finally:
            self.finished.emit()


class ValidatorFactory:
    @staticmethod
    def create_password_validator(parent=None):
        regex = QRegularExpression(r'^[a-zA-Z_#$&*\d]+')
        return QRegularExpressionValidator(regex, parent=parent)
    
    @staticmethod
    def create_name_validator(parent=None):
        regex = QRegularExpression(r'^[A-Za-z_]+(?: [A-Za-z_]+)*$')
        return QRegularExpressionValidator(regex, parent=parent)
    
    @staticmethod
    def create_authors_validator(parent=None):
        regex = QRegularExpression(r'^[A-Za-z,]+(?: [A-Za-z,]+)*$')
        return QRegularExpressionValidator(regex, parent=parent)
    

class ValidationRules:
    @staticmethod
    def get_password_rule(password):
        return lambda: not password.text().strip() or len(set(password.text())) < 4 or any(char in password.text() for char in [';', ',', '.', ':'])

    @staticmethod
    def get_password_message():
        return "Provide a password that has at least 4 unique characters and does not contain any of these characters ; , . :"

    @staticmethod
    def get_confirm_password_rule(password, confirm):
        return lambda: not password.text().strip() == confirm.text().strip()

    @staticmethod
    def get_confirm_password_message():
        return "Passwords do not match"

    @staticmethod
    def get_admin_rule(admin):
        return lambda: not admin.text().strip()

    @staticmethod
    def get_project_rule(project_name):
        return lambda: not project_name.text().strip()

    @staticmethod
    def get_authors_rule(authors):
        return lambda: not len(authors.text().strip().split(",")) > 1 and not authors.text().strip()

    @staticmethod
    def get_description_rule(dir):
        return lambda: not dir.text() or not Path(dir.text()).exists()

class ValidationRule:
    def __init__(self, condition, error_message, error_label):
        self.condition = condition
        self.error_message = error_message
        self.error_label = error_label

    def validate(self):
        if not self.condition():
            self.error_label.setText(self.error_message)
            return False
        else:
            self.error_label.setText("")
            return True

    def has_passed(self):
        return self.passed
    
class InputValidator:
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

    def validate(self):
        all_valid = True
        for rule in self.rules:
            is_valid = rule.validate()
            all_valid = all_valid and is_valid
        return all_valid

class ErrorLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("color: darkred")
        self.setText("")


class ProjectMerger(QWidget):
    close_signal = pyqtSignal(bool)
    def __init__(self, target_project_adapter, soure_project_adapter):
        super().__init__()
        self.target_project_adapter = target_project_adapter
        self.source_project_adapter = soure_project_adapter
        self.target_project_view = ProjectViewer(target_project_adapter)
        self.source_project_view = ProjectViewer(soure_project_adapter)
        self.target_project_view.set_enable_conext_menu(False)
        self.source_project_view.set_enable_conext_menu(False)
        ProjectLoader(target_project_adapter).load_project()

        self.setWindowTitle("Project Merger")

        # Create layouts
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        self.setLayout(main_layout) 
        self.keep_empty_checkbox = QCheckBox("Keep empty source sessions")
        # Left side (target project)
        target_label = QLabel("Target Project Information")
        self.merge_button = QPushButton("Merge Projects")
        left_layout.addWidget(target_label)
        left_layout.addWidget(self.target_project_view)
        left_layout.addWidget(self.keep_empty_checkbox)
        left_layout.addWidget(self.merge_button)
        self.merge_button.setEnabled(False)
        # Right side (source project - initially empty)
        source_label = QLabel("Source Project Information")
        
        right_layout.addWidget(source_label)

        # Load project button
        self.load_button = QPushButton("Load Project")
        self.load_button.clicked.connect(self.load_source_project)
        
        # Add layouts to main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        right_layout.addWidget(self.source_project_view)
        right_layout.addWidget(QLabel())
        right_layout.addWidget(self.load_button)
        
        self.connect_signals()

    def connect_signals(self):
        self.merge_button.clicked.connect(self.merge_projects)

    def merge_projects(self):
        if self.target_project_adapter.get_project_dir() == self.source_project_adapter.get_project_dir():
            QMessageBox.information(self, "Merge Projects", "You cannot merge the same project.")
            return
        self.setEnabled(False)
        self.target_project_adapter.merge_project(self.source_project_adapter, self.keep_empty_checkbox.isChecked())
        QMessageBox.information(self, "Merge Projects", "Done integrating sessions from source project into target project.")
        self.close()
    
    def load_source_project(self):
        try:        
            self.loader = ProjectLoader(self.source_project_adapter)  # Create ProjectLoader instance
            self.loader.choose_dir()
            self.loader.load_project()
            self.merge_button.setEnabled(True)
        except FileNotFoundError as fne:
            QMessageBox.warning(self, f"project file missing", str(fne))
        except ValueError as ve:
            QMessageBox.warning(self, f"project file corrupted", str(ve)) 
        except Exception as e:
            QMessageBox.warning(self, f"Something went wrong", str(e))

    def closeEvent(self, event):
        self.close_signal.emit(True)
        super().closeEvent(event)

class ProjectCreator(QWidget):
    changed = pyqtSignal(str)
    close_signal = pyqtSignal(bool)
    create_successfull = pyqtSignal()

    def __init__(self, db_adapter, parent=None):
        super().__init__(parent)
        self.db_adapter = db_adapter
        self.setWindowTitle('Create Project')
        self.setGeometry(600, 500, 400, 800)
        self.validator = InputValidator()
        
        self.input_fields = {
            'admin': {
                'type': 'line', 'label': 'Administrator', 'max_length': 15, 'validator': 'name',
                'error_rule': lambda: ValidationRules.get_admin_rule(self.admin),
                'error_message': "Provide a valid name for admin login"
            },
            'password': {
                'type': 'line', 'label': 'Password', 'max_length': 16, 'echo_mode': QLineEdit.EchoMode.Password,
                'error_rule': lambda : ValidationRules.get_password_rule(self.password),
                'error_message': ValidationRules.get_password_message()
            },
            'password_confirm': {
                'type': 'line', 'label': 'Confirm Password', 'max_length': 16, 'echo_mode': QLineEdit.EchoMode.Password,
                'error_rule': lambda: ValidationRules.get_confirm_password_rule(self.password, self.password_confirm),
                'error_message': ValidationRules.get_confirm_password_message()
            },

            'project_name': {
                'type': 'line', 'label': 'Project Name', 'max_length': 16, 'validator': 'name',
                'error_rule': lambda: ValidationRules.get_project_rule(self.project_name),
                'error_message': "Project name cannot be empty"
            },
            'authors': {
                'type': 'line', 'label': 'Authors', 'max_length': 40, 'validator': 'authors',
                'error_rule': lambda: ValidationRules.get_authors_rule(self.authors) ,
                'error_message': "Author name cannot be empty"
            },
            'description': {'type': 'text', 'label': 'Description', 'min_height': 200},
            'dir': {
                'type': 'dir', 'label': 'Directory',
                'error_rule': lambda: ValidationRules.get_description_rule(self.dir),
                'error_message': "Directory does not exist"
            }
        }
        
        layout = QVBoxLayout()
        self.create_input_fields(layout)
        
        self.create_button = QPushButton("Next")
        self.create_button.clicked.connect(self.create_project)
        layout.addWidget(self.create_button)
        
        self.setLayout(layout)

    def create_input_fields(self, layout):
        for field_name, field_info in self.input_fields.items():
            field_layout = self.create_input_layout(field_name, field_info)
            layout.addLayout(field_layout)

    def create_input_layout(self, field_name, field_info):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(field_info['label']))
        
        if field_info['type'] == 'line':
            self.__dict__[field_name] = QLineEdit()
            self.setup_line_edit(self.__dict__[field_name], field_info)
            layout.addWidget(self.__dict__[field_name])
        elif field_info['type'] == 'text':
            self.__dict__[field_name] = QTextEdit()
            self.__dict__[field_name].setMinimumHeight(field_info['min_height'])
            layout.addWidget(self.__dict__[field_name])
        elif field_info['type'] == 'dir':
            dir_layout = QHBoxLayout()
            self.__dict__[field_name] = QLineEdit()
            dir_layout.addWidget(self.__dict__[field_name])
            self.dir_dialog = QPushButton(QIcon("resources/assets/folder.png"), "Select Dir")
            self.dir_dialog.clicked.connect(self.choose_dir)
            dir_layout.addWidget(self.dir_dialog)
            layout.addLayout(dir_layout)
        
        error_label = ErrorLabel()
        layout.addWidget(error_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        if 'error_rule' in field_info and 'error_message' in field_info:
            self.bind_error_handling(self.__dict__[field_name], error_label, field_info['error_rule'], field_info['error_message'])
        
        return layout

    def bind_error_handling(self, input_widget, error_label, error_rule, error_message):
        def check_error():
            if error_rule()():
                error_label.setText(error_message)
                error_label.setVisible(True)
            else:
                error_label.setVisible(False)

        if isinstance(input_widget, QLineEdit):
            input_widget.textChanged.connect(check_error)
        elif isinstance(input_widget, QTextEdit):
            input_widget.textChanged.connect(check_error)

        self.validator.add_rule(
            ValidationRule(
                error_rule,
                error_message,
                error_label
            )
        )

    def setup_line_edit(self, line_edit, field_info):
        line_edit.setMaxLength(field_info['max_length'])
        if 'validator' in field_info:
            validator_method = getattr(ValidatorFactory, f"create_{field_info['validator']}_validator")
            line_edit.setValidator(validator_method(line_edit))
        if 'echo_mode' in field_info:
            line_edit.setEchoMode(field_info['echo_mode'])

    def choose_dir(self):
        file_dialog = QFileDialog()
        file_dialog.setDirectory(QDir.homePath())
        directory = file_dialog.getExistingDirectory(self, "Choose Directory")
        if directory:
            self.dir.setText(directory)

    def get_dir(self):
        return self.dir.text()

    def get_project_name(self):
        return self.project_name.text()
    
    def create_project(self):
        if self.validator.validate():
            project_info = dict()
            project_dir = (Path(self.dir.text().strip()) / self.project_name.text().strip()).as_posix()
            project_info = {
                'project_dir': project_dir,
                'creation_date': datetime.now().strftime("%Y-%m-%d"),
                'name': self.project_name.text().strip(),
                'authors': self.authors.text().strip().split(","),
                'description': self.description.toPlainText().strip(),
                'num_captures': 0
            }
            
            admin_name = self.admin.text().strip()
            admin_password = self.password.text()
            admin = {"username": admin_name, "password": admin_password, "role": "admin"}
            try:
                self.db_adapter.create_project(project_info)
                self.db_adapter.save_encrypted_users(admin)
            except Exception as e:
                QMessageBox.warning(self, "Something went wrong", str(e))
            self.create_successfull.emit()

    def closeEvent(self, event):
        self.close_signal.emit(True)
        super().closeEvent(event)

class ProjectLoader(QWidget):
    changed = pyqtSignal(str)
    close_signal = pyqtSignal(bool)
    load_successful = pyqtSignal()

    def __init__(self, db_adapter):
        super().__init__()
        self.db_adapter = db_adapter

        self.setWindowTitle("Load Project")
        self.setGeometry(900,600,300,100)
        layout = QVBoxLayout()
        self.dir = QLineEdit()        
        if self.db_adapter.get_project_dir():
            self.dir.setText(str(self.db_adapter.get_project_dir()))
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Project Dir"))
        input_layout.addWidget(self.dir)
        layout.addLayout(input_layout)
        self.dir_dialog = QPushButton(QIcon("resources/assets/open.png"), "Select Dir")
        self.dir_dialog.clicked.connect(self.choose_dir)
        layout.addWidget(self.dir_dialog)

        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_project)
        layout.addWidget(self.load_button)

        self.setLayout(layout)

    def choose_dir(self):
        file_dialog = QFileDialog()
        file_dialog.setDirectory(QDir.homePath())
        directory = file_dialog.getExistingDirectory(
            self, "Choose Project Directory")
        if directory:
            self.dir.setText(directory)

    def load_project(self):
        try:
            project_dir = self.dir.text()
            self.db_adapter.load_project(project_dir)
            self.load_successful.emit()
        except FileNotFoundError as fne:
            QMessageBox.warning(self, f"project file missing", str(fne))
        except ValueError as ve:
            QMessageBox.warning(self, f"project file corrupted", str(ve)) 
        except Exception as e:
            QMessageBox.warning(self, f"Something went wrong", str(e))
        
    def get_project_name(self):
        return Path(self.dir.text()).parts[-1]

    def get_dir(self):
        return self.dir.text()
    
    def closeEvent(self, event):
        self.close_signal.emit(True)
        super().closeEvent(event)

class LoginWidget(QWidget):
    login_successful = pyqtSignal(dict)
    close_signal = pyqtSignal(bool)

    def __init__(self, db_adapter):
        super().__init__()
        self.db_adapter = db_adapter
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setWindowTitle("Login")
        self.setGeometry(600,500,300,200)
        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.returnPressed.connect(self.attempt_login)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.attempt_login)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.attempt_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        user = self.db_adapter.verify_credentials(username, password)
        if user:
            self.login_successful.emit(user)
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def closeEvent(self, event):
        self.close_signal.emit(True)
        super().closeEvent(event)
        
class SessionViewer(QWidget):
    def __init__(self, parent=None, db_adapter=None, current_user=None):
        super().__init__(parent)
        self.db_adapter = db_adapter
        self.current_user = current_user
        self.fields = ["Name", "Capturer", "Museum", "Collection Name", "Session Dir", "# Captures"] # besser als uebergabe parameter, damit backend und hier immer gleich
        self.row_ids = {}
        # Create the table view
        self.table_view = QTableView()
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.create_context_menu)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setSortingEnabled(True)
        # Set the table model (you need to provide the data)
        self.table_model = None  # Replace with your data model
        self.table_view.setModel(self.table_model)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        self.setLayout(layout)

        self.table_model = QStandardItemModel(1, 5)
        self.table_model.setHorizontalHeaderLabels(self.fields)
        self.table_view.setModel(self.table_model)

    def set_data(self, data):
        # Create and set the table model with the provided data
        self.table_model = QStandardItemModel(len(data), 5)
        self.table_model.setHorizontalHeaderLabels(self.fields)
        fields = [field.replace(" ","_").lower().replace("#", "num") for field in self.fields]
        for row, session_entry in enumerate(data.items()):
            key, session = session_entry
            for column, field in enumerate(fields):
                item = QStandardItem(str(session.get(field,None)))
                self.table_model.setItem(row, column, item)
            self.row_ids[row] = key
        self.table_view.setModel(self.table_model)

    def sort_by_column(self, column):
        self.table_model.sort(column, Qt.AscendingOrder)

    def column_clicked(self, column):
        self.sort_by_column(column)

    def set_enable_context_menu(self, enable):
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu if enable else Qt.ContextMenuPolicy.NoContextMenu)

    def create_context_menu(self, position):
        menu = QMenu(self.table_view)
        
        # Erstelle die Aktionen für das Menü
        delete_action = QAction("Delete Session", self.table_view)
        open_in_file_browser_action = QAction("Open in filebrowser", self.table_view)
        
        # Füge die Aktionen dem Menü hinzu
        menu.addAction(delete_action)
        menu.addAction(open_in_file_browser_action)
        
        # Verbinde die Aktionen mit Slots
        delete_action.triggered.connect(self.delete_session)
        open_in_file_browser_action.triggered.connect(self.open_in_file_browser)
        user = self.db_adapter.get_current_user()
        if not user:
            return
        if user['role'] != 'admin':
            delete_action.setEnabled(False)
        # Zeige das Menü an der angeklickten Position
        menu.exec(self.table_view.mapToGlobal(position))

    def open_in_file_browser(self):
            row = self.table_view.currentIndex().row()
            column = self.fields.index("Session Dir")
            relative_dir = self.table_model.item(row, column).text()
            project_dir = self.db_adapter.get_project_dir() / relative_dir

            if not project_dir.is_dir():
                raise FileNotFoundError(f"Directory does not exists: {str(project_dir)}")
            
            # Create and start the thread
            self.open_dir_thread = OpenDirThread(project_dir)
            self.open_dir_thread.start()

    def delete_session(self):
        row = self.table_view.currentIndex().row()
        session_id = self.row_ids[row]
        session_name = self.table_model.item(row,0).text()
        captures_column = self.fields.index('# Captures')
        num_captures = self.table_model.item(row, captures_column).text()
        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       f"{session_name} contains {num_captures} captures! Are you shure you want to delete it?")
        if not confirm:
            return                             
        try:
            self.db_adapter.delete_session(session_id)
        except FileNotFoundError as fne:
            QMessageBox.warning(self, "Missing Data", str(fne))
        except Exception as e:
            QMessageBox.warning(self, "Something went wrong", str(e))

class CaptureViewer(QWidget):
    pass

class SessionCreator(QDialog):
    close_signal = pyqtSignal(bool)
    session_created = pyqtSignal()

    def __init__(self, db_adapter, sessions, parent=None):
        super().__init__(parent)
        self.db_adapter = db_adapter
        self.sessions = sessions
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("New Session")
        self.setGeometry(500,300,400,300)
        layout = QVBoxLayout()

        # Capturer
        capturer_layout = QVBoxLayout()
        self.capturer_label = QLabel("Capturer*")
        self.capturer_edit = QComboBox()
        capturer_layout.addWidget(self.capturer_label)
        capturer_layout.addWidget(self.capturer_edit)
        layout.addLayout(capturer_layout)

        # Museum
        museum_layout = QVBoxLayout()
        self.museum_label = QLabel("Museum*")
        self.museum_edit = QComboBox()
        museum_layout.addWidget(self.museum_label)
        museum_layout.addWidget(self.museum_edit)
        layout.addLayout(museum_layout)

        # Collection Name
        collection_name_layout = QVBoxLayout()
        self.collection_name_label = QLabel("Collection Name")
        self.collection_name_edit = QLineEdit()
        collection_name_layout.addWidget(self.collection_name_label)
        collection_name_layout.addWidget(self.collection_name_edit)
        layout.addLayout(collection_name_layout)

        # Create Session Button
        self.create_session_button = QPushButton("Create Session")
        self.create_session_button.clicked.connect(self.create_session)
        layout.addWidget(self.create_session_button)

        self.setLayout(layout)
        
    def set_user(self, user):
        if not user:
            QMessageBox.warning(self, "You have to load or create a project before you can start a capture session.")
        self.capturer_edit.addItem(user['username'])

    def set_museums(self, museums):
        for museum in museums.values():
            self.museum_edit.addItem(f"{museum['name']} - {museum['city']}")

    def create_session(self):
        capturer = self.capturer_edit.currentText().strip()
        museum = self.museum_edit.currentText().strip()
        collection_name = self.collection_name_edit.text().strip()
        if museum == '':
            QMessageBox.information(self, "Missing Data", "You must select a museum before you can create a session.")
            return
        session_data = {
            "capturer": capturer,
            "museum": museum,
            "collection_name": collection_name if collection_name else None,
        }
        self.db_adapter.create_session(session_data)
        self.session_created.emit()
        
    def closeEvent(self, event):
        self.close_signal.emit(True)
        super().closeEvent(event)

class ProjectViewer(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, db_adapter):
        super().__init__()
        self.session_view = SessionViewer(self, db_adapter=db_adapter)
        self.db_adapter = db_adapter
        main_layout = QGridLayout()
        top_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.project_info_list = QListWidget()
        project_info_layout = QVBoxLayout()
        session_layout = QVBoxLayout()
        session_layout.addWidget(self.session_view)
        project_info_layout.addWidget(self.project_info_list)
        self.project_info_list.addItem("No Project loaded")
        top_layout.addLayout(button_layout)
        top_layout.addLayout(project_info_layout)

        main_layout.addLayout(top_layout, 0, 0)
        main_layout.addLayout(session_layout, 1, 0)
        self.setLayout(main_layout)

        self.db_adapter.project_changed_signal.connect(self.update_project_list)
        self.db_adapter.sessions_signal.connect(self.update_session_view)

    def set_enable_conext_menu(self, enable):
        self.session_view.set_enable_context_menu(enable)
        
    def close_project(self):
        self.changed.emit("main")
        super().close()

    def update_project_list(self, project_info):
        if isinstance(project_info, Exception):
            logger.info(f"{project_info}")
            return
        self.project_info_list.clear()
        item_strings = self._create_project_info_item_str_list(project_info)
        self.project_info_list.addItems(item_strings)

    def _create_project_info_item_str_list(self, project_info):
        item_strings = []
        for key, value in project_info.items():
            key = key.replace("_", " ").capitalize()
            item_strings.append(f"{key}: {value}")
        return item_strings
    
    def update_session_view(self, sessions):
        self.sessions = sessions
        self.session_view.set_data(self.sessions)

    def set_camera_data(self, camera_data):
        pass # think about how to implement this

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        self.setGeometry(500,600,200,200)
        self.validator = InputValidator()
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_confirm = QLineEdit()
        self.password_confirm.setEchoMode(QLineEdit.EchoMode.Password)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        
        self.password_error = ErrorLabel(self)
        self.confirm_error = ErrorLabel(self)

        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.password_error)
        layout.addWidget(QLabel("Confirm Password:"))
        layout.addWidget(self.password_confirm)
        layout.addWidget(self.confirm_error)
        layout.addWidget(QLabel("Role:"))
        layout.addWidget(self.role_combo)
        
        self.bind_error_handling(
            self.password_input, 
            self.password_error,
            ValidationRules.get_password_rule(self.password_input),
            ValidationRules.get_password_message(),
        )
        self.bind_error_handling(
            self.password_confirm, 
            self.confirm_error,
            ValidationRules.get_confirm_password_rule(self.password_input, self.password_confirm),
            ValidationRules.get_confirm_password_message(),
        )
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        self.setLayout(layout)

    def bind_error_handling(self, input_widget, error_label, error_rule, error_message):
        def check_error():
            if error_rule():
                error_label.setText(error_message)
                error_label.setVisible(True)
            else:
                error_label.setVisible(False)

        if isinstance(input_widget, QLineEdit):
            input_widget.textChanged.connect(check_error)

        self.validator.add_rule(
            ValidationRule(
                error_rule,
                error_message,
                error_label
            )
        )

class UserManager(QWidget):
    user_updated = pyqtSignal()  # Signal to notify of user changes
    close_signal = pyqtSignal(bool)

    def __init__(self, db_adapter, current_user, parent=None):
        super().__init__(parent)
        self.db_adapter = db_adapter
        self.current_user = current_user

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mange Users")
        layout = QVBoxLayout()
        
        self.user_list = QListWidget()
        layout.addWidget(self.user_list)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add User")
        remove_button = QPushButton("Remove User")
        change_role_button = QPushButton("Change Role")
        
        add_button.clicked.connect(self.add_user)
        remove_button.clicked.connect(self.remove_user)
        change_role_button.clicked.connect(self.change_role)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(change_role_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.refresh_user_list()

    def refresh_user_list(self):
        self.user_list.clear()
        users = self.db_adapter.get_users()
        for user in users:
            self.user_list.addItem(f"{user['username']} ({user['role']})")

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec():
            username = dialog.username_input.text()
            password = dialog.password_input.text()
            password_confirm = dialog.password_confirm.text()
            role = dialog.role_combo.currentText()
            
            if not username or not password:
                QMessageBox.warning(self, "Input Error", "Username and password cannot be empty.")
                return
            if password != password_confirm:
                QMessageBox.warning(self, "Input Error", "Passwords do not match.")
                return
            if not dialog.validator.validate():
                try:
                    new_user = {'username': username, 'password': password, 'role': role}
                    self.db_adapter.add_user(new_user)
                    self.refresh_user_list()
                    self.user_updated.emit()
                    QMessageBox.information(self, "Success", f"User {username} added successfully.")
                except ValueError as e:
                    QMessageBox.critical(self, {str(e)})
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")

    def remove_user(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a user to remove.")
            return
        
        user_to_remove = selected_items[0].text().split(' ')[0]  # Extract username
        
        confirm = QMessageBox.question(self, "Confirm Removal", f"Are you sure you want to remove {user_to_remove}?")
        if confirm == QMessageBox.StandardButton.Yes:
            admin_password, ok = QInputDialog.getText(self, "Admin Confirmation", 
                                                      "Enter admin password:", QLineEdit.EchoMode.Password)
            if ok:
                try:
                    if self.db_adapter.validate_admin(self.current_user['username'], admin_password):
                        self.db_adapter.remove_user(user_to_remove)
                        self.refresh_user_list()
                        self.user_updated.emit()
                        QMessageBox.information(self, "Success", f"User {user_to_remove} removed successfully.")
                    else:
                        QMessageBox.warning(self, "Authentication Failed", "Invalid admin password.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to remove user: {str(e)}")

    def change_role(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a user to change role.")
            return
        
        user_to_change = selected_items[0].text().split(' ')[0]  # Extract username
        current_role = selected_items[0].text().split('(')[1].strip(')')  # Extract current role
        new_role = "admin" if current_role == "user" else "user"
        
        confirm = QMessageBox.question(self, "Confirm Role Change", 
                                       f"Change {user_to_change}'s role to {new_role}?")
        if confirm == QMessageBox.StandardButton.Yes:
            admin_password, ok = QInputDialog.getText(self, "Admin Confirmation", 
                                                      "Enter admin password:", QLineEdit.EchoMode.Password)
            if ok:
                try:
                    if self.db_adapter.validate_admin(self.current_user['username'], admin_password):
                        if new_role == "user" and self.db_adapter.count_admins() <= 1:
                            QMessageBox.warning(self, "Error", "Cannot change the last admin to a user.")
                        else:
                            self.db_adapter.change_user_role(user_to_change, new_role)
                            self.refresh_user_list()
                            self.user_updated.emit()
                            QMessageBox.information(self, "Success", f"{user_to_change}'s role changed to {new_role}.")
                    else:
                        QMessageBox.warning(self, "Authentication Failed", "Invalid admin password.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to change user role: {str(e)}")
    
    def get_current_user(self):
        return self.current_user
    
    def closeEvent(self, event):
        self.close_signal.emit(True)
        super().closeEvent(event)

class UserSettings(QWidget):
    finished = pyqtSignal()
    close_signal = pyqtSignal(bool)

    def __init__(self, db_adapter, user):
        super().__init__()

        self.db_adapter = db_adapter
        self.username = user['username']
        self.role = user['role']
        self.resetter = ResetPasswordWidget(self.db_adapter, self.username, self.role)
        self.resetter.hide()
        self.setWindowTitle("User Settings")
        self.setGeometry(600,700,200,90)
        # UI Elements
        self.username_label = QLabel(f"Username: {self.username}")
        self.role_label = QLabel(f"Role: {self.role}")
        self.reset_password_button = QPushButton("Reset Password")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.role_label)
        layout.addWidget(self.reset_password_button)
        layout.addWidget(self.resetter)

        self.setLayout(layout)

        # Connections
        self.reset_password_button.clicked.connect(self.reset_password)
        self.resetter.finished.connect(self.enable_main_window)

    def reset_password(self):
        self.reset_password_button.hide()
        self.resetter.show()

    def enable_main_window(self):
        self.setDisabled(False)
        self.resetter.hide()
        self.reset_password_button.show()
    
    def closeEvent(self, event):
        self.close_signal.emit(True)
        super().closeEvent(event)

class ResetPasswordWidget(QWidget):
    finished = pyqtSignal()

    def __init__(self, db_adapter, username, role):
        super().__init__()

        self.db_adapter = db_adapter
        self.username = username
        self.role = role

        self.setWindowTitle("Reset Password")

        # UI Elements
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setPlaceholderText("Old password")
        self.old_password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.new_password_edit = QLineEdit()
        self.new_password_edit.setPlaceholderText("New password")
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_edit.setValidator(ValidatorFactory.create_password_validator(self))

        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("Confirm new password")
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit.setValidator(ValidatorFactory.create_password_validator(self))

        self.reset_button = QPushButton("Reset")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.old_password_edit)
        layout.addWidget(self.new_password_edit)
        layout.addWidget(self.confirm_password_edit)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

        # Connections
        self.reset_button.clicked.connect(self.reset_password)

    def reset_password(self):
        old_password = self.old_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        if not self.new_password_edit.hasAcceptableInput() or not self.confirm_password_edit.hasAcceptableInput():
            QMessageBox.warning(self, "Invalid Password", "New password must contain at least 4 unique characters and no ', . ;'.")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "New passwords do not match.")
            return

        if self.db_adapter.reset_password(self.username, self.role, old_password, new_password):
            QMessageBox.information(self, "Success", "Password reset successfully.")
            self.finished.emit()
            self.close()
        else:
            QMessageBox.warning(self, "Failure", "Failed to reset password.")

class MuseumTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.headers = ["Museum Name", "City", "Street", "Number"]
        self.data = [["", "", "", ""]]

    def rowCount(self, parent=QModelIndex()):
        return len(self.data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return self.data[index.row()][index.column()]
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            self.data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

class AddMuseumDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Museum")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Museum Name")
        layout.addWidget(self.name_input)

        self.city_input = QLineEdit(self)
        self.city_input.setPlaceholderText("City")
        layout.addWidget(self.city_input)

        address_layout = QHBoxLayout()
        self.street_input = QLineEdit(self)
        self.street_input.setPlaceholderText("Street")
        address_layout.addWidget(self.street_input)

        self.number_input = QLineEdit(self)
        self.number_input.setPlaceholderText("Number")
        self.number_input.setFixedWidth(60)  # Make the number input smaller
        address_layout.addWidget(self.number_input)

        layout.addLayout(address_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_museum_data(self):
        return [
            self.name_input.text(),
            self.city_input.text(),
            self.street_input.text(),
            self.number_input.text()
        ]

class MuseumManager(QWidget):
    museum_updated = pyqtSignal()  # Signal to notify of museum changes
    close_signal = pyqtSignal(bool)

    def __init__(self, db_adapter, current_user, parent=None):
        super().__init__(parent)
        self.db_adapter = db_adapter
        self.current_user = current_user
        self.original_data = []  # To store the original data for comparison

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setWindowTitle("Manage Museums")
        self.museum_table = QTableView()
        self.model = QStandardItemModel()
        self.museum_table.setModel(self.model)
        layout.addWidget(self.museum_table)
        
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Museum")
        remove_button = QPushButton("Remove Museum")
        save_button = QPushButton("Save Changes")
        
        add_button.clicked.connect(self.add_museum)
        remove_button.clicked.connect(self.remove_museum)
        save_button.clicked.connect(self.save_changes)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.refresh_museum_list()

    def refresh_museum_list(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Museum Name", "City", "Street", "Number"])
        museums = self.db_adapter.get_museums()
        self.original_data = []
        for _, museum in museums.items():
            row = [
                QStandardItem(museum['name']),
                QStandardItem(museum['city']),
                QStandardItem(museum['street']),
                QStandardItem(museum['number'])
            ]
            self.model.appendRow(row)
            self.original_data.append(museum)
        self.museum_table.resizeColumnsToContents()

    def add_museum(self):
        dialog = AddMuseumDialog(self)
        if dialog.exec():
            museum_data = dialog.get_museum_data()
            name, city, street, number = museum_data
            
            if not name or not city or not street:
                QMessageBox.warning(self, "Input Error", "Name, city, and street must be filled.")
                return
            
            try:
                new_museum = {'name': name, 'city': city, 'street': street, 'number': number}
                if self.db_adapter.add_museum(new_museum):
                    self.refresh_museum_list()
                    self.museum_updated.emit()
                    QMessageBox.information(self, "Success", f"Museum {name} added successfully.")
                else:
                    raise Exception("Some problems with the database")
            except IndexError as e:
                QMessageBox.critical(self, "Error", f"Failed to add museum: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add museum: {str(e)}")

    def remove_museum(self):
        selected_indexes = self.museum_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Selection Error", "Please select a museum to remove.")
            return
        for selected_index in selected_indexes:
            selected_row = selected_index.row()
            museum_name = self.model.item(selected_row, 0).text()
            museum_city = self.model.item(selected_row, 1).text()
            museum_street = self.model.item(selected_row, 2).text()
            museum_number = self.model.item(selected_row, 3).text()
            museum_to_remove = {
                'name': museum_name, 
                'city': museum_city, 
                'street': museum_street, 
                'number': museum_number
            }
        
            confirm = QMessageBox.question(self, "Confirm Removal", f"Are you sure you want to remove {museum_name}?")
            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    self.db_adapter.remove_museum(museum_to_remove)
                    self.refresh_museum_list()
                    self.museum_updated.emit()
                    QMessageBox.information(self, "Success", f"Museum {museum_name} removed successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to remove museum: {str(e)}")

    def save_changes(self):
        changes = []
        for row in range(self.model.rowCount()):
            new_data = {
                'name': self.model.item(row, 0).text(),
                'city': self.model.item(row, 1).text(),
                'street': self.model.item(row, 2).text(),
                'number': self.model.item(row, 3).text()
            }
            if new_data != self.original_data[row]:
                changes.append((self.original_data[row], new_data))

        if not changes:
            QMessageBox.information(self, "No Changes", "No changes were made.")
            return

        try:
            for original, updated in changes:
                self.db_adapter.edit_museum(original, updated)
            self.refresh_museum_list()
            self.museum_updated.emit()
            QMessageBox.information(self, "Success", f"{len(changes)} museum(s) updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update museums: {str(e)}")

    def closeEvent(self, event):
        self.close_signal.emit(True)
        super().closeEvent(event)


def init_project_viewer(db_adapter):
    db_adapter.load_project()

def init_project_creator():
    pass

def init_project_loader():
    pass

if __name__ == "__main__":
    from argparse import ArgumentParser
    from src.db.DB import DBAdapter, FileAgnosticDB
    widgets = ["creator", "loader", "viewer"]
    widgets_dict = {
        "creator": ProjectCreator,
        "loader": ProjectLoader,
        "viewer": ProjectViewer
    }

    parser = ArgumentParser()
    parser.add_argument("--widget", choices=widgets, default="creator")
    args = parser.parse_args()
    db_manager = FileAgnosticDB()
    db_adapter = DBAdapter(db_manager=db_manager)

    app = QApplication([])
    window = widgets_dict[args.widget](db_adapter)
    if args.widget == "viewer":
        db_adapter.load_project('tests/data/')
    window.show()
    app.exec()
