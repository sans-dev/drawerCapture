from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, Qt, QDir, QRegularExpression
from PyQt6.QtGui import QIcon, QRegularExpressionValidator, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (QApplication, QDialog, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel, 
                             QListWidget, QHBoxLayout, QTableView, QAbstractItemView, QHeaderView, QCheckBox, 
                             QSpacerItem, QSizePolicy, QGridLayout, QMessageBox, QInputDialog, QComboBox, QTextEdit)
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


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
        return lambda: not password.text().strip() or len(set(password.text())) < 4 or any(char in password.text() for char in [';',',','.',':'])
    
    @staticmethod
    def get_password_message():
        return "Provide a password that has at least 4 unique characters and does not contain any of these characters ; , . :"
    
    @staticmethod
    def get_confirm_password_rule(password, confirm):
        return lambda: not password.text().strip() == confirm.text().strip()
    
    @staticmethod
    def get_confirm_password_message():
        return "Passwords do not match"
    # add wrong login data

class ValidationRule:
    def __init__(self, condition, error_message, error_label):
        self.condition = condition
        self.error_message = error_message
        self.error_label = error_label

    def validate(self):
        if self.condition():
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
                'error_rule': lambda: not self.admin.text().strip(),
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
                'error_rule': lambda: not self.project_name.text().strip(),
                'error_message': "Project name cannot be empty"
            },
            'authors': {
                'type': 'line', 'label': 'Authors', 'max_length': 40, 'validator': 'authors',
                'error_rule': lambda: not len(self.authors.text().strip().split(",")) > 1 and not self.authors.text().strip(),
                'error_message': "Author name cannot be empty"
            },
            'description': {'type': 'text', 'label': 'Description', 'min_height': 200},
            'dir': {
                'type': 'dir', 'label': 'Directory',
                'error_rule': lambda: not self.dir.text() or not Path(self.dir.text()).exists(),
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
            project_info['Project Info'] = {
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
            self.db_adapter.create_project(project_info)
            self.db_adapter.save_encrypted_users(admin)
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
        project_dir = self.dir.text()
        if self.db_adapter.load_project(project_dir):
            self.load_successful.emit()
        else:
            QMessageBox.warning(self, "Failed to load project.", "INI file is invalid.")
        
    def get_project_name(self):
        return Path(self.dir.text()).parts[-1]

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
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Login button
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.attempt_login)
        layout.addWidget(login_button)

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
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create the table view
        self.table_view = QTableView()
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
        self.table_model.setHorizontalHeaderLabels(["Session ID", "Date", "Capturer", "Museum", "# Captures"])
        self.table_view.setModel(self.table_model)

    def set_data(self, data):
        # Create and set the table model with the provided data
        self.table_model = QStandardItemModel(len(data), 5)
        self.table_model.setHorizontalHeaderLabels(["Session ID", "Date", "Capturer", "Museum", "# Captures"])

        for row, session in enumerate(data):
            session_id = QStandardItem(str(session["session_id"]))
            date = QStandardItem(session["date"])
            capturer = QStandardItem(session["capturer"])
            museum = QStandardItem(session["museum"])
            num_captures = QStandardItem(str(session["num_captures"]))

            self.table_model.setItem(row, 0, session_id)
            self.table_model.setItem(row, 1, date)
            self.table_model.setItem(row, 2, capturer)
            self.table_model.setItem(row, 3, museum)
            self.table_model.setItem(row, 4, num_captures)

        self.table_view.setModel(self.table_model)

    def sort_by_column(self, column):
        self.table_model.sort(column, Qt.AscendingOrder)

    def column_clicked(self, column):
        self.sort_by_column(column)

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
        self.capturer_edit.addItem(user['username'])

    def set_museums(self, museums):
        for museum in museums:
            self.museum_edit.addItem(museum)

    def create_session(self):
        #TODO needs big refactoring
        capturer = self.capturer_edit.currentText().strip()
        museum = self.museum_edit.currentText().strip()
        collection_name = self.collection_name_edit.text().strip()

        max_id = 0
        for session in self.sessions:
            _id = int(session.get("session_id"))
            if _id > max_id:
                max_id = _id
        session_id = max_id + 1
        session_name = f"Session {session_id}"
        session_data = {
            "name" : session_name,
            "id": str(session_id),
            "capturer": capturer,
            "museum": museum,
            "collection_name": collection_name if collection_name else None,
            "date" : datetime.now().strftime("%Y-%m-%d"),
            "num_captures" : 0
        }
        # Call the appropriate function in your db_adapter to create the session
        self.db_adapter.create_session(session_data)
        self.session_created.emit()
        
    def closeEvent(self, event):
        self.close_signal.emit(True)
        super().closeEvent(event)

class ProjectViewer(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, db_adapter):
        super().__init__()
        self.session_view = SessionViewer()
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
        self.db_adapter.project_changed_signal.connect(self.update_session_view)

    def close_project(self):
        self.changed.emit("main")
        super().close()

    def update_project_list(self, project_info):
        if isinstance(project_info, Exception):
            logger.info(f"{project_info}")
            return
        self.project_info_list.clear()
        project_info = project_info['Project Info']
        item_strings = self._create_project_info_item_str_list(project_info)
        self.project_info_list.addItems(item_strings)

    def _create_project_info_item_str_list(self, project_info):
        item_strings = []
        for key, value in project_info.items():
            key = key.replace("_", " ").capitalize()
            item_strings.append(f"{key}: {value}")
        return item_strings
    
    def update_session_view(self, project_info):
        self.sessions = []
        for key, value in project_info.items():
            if "Session" in key:
                data = dict()
                data['session_id'] = value.get('id')
                data['date'] = value.get('date')
                data['capturer'] = value.get('capturer')
                data['museum'] = value.get('museum')
                data['num_captures'] = value.get('num_captures')
                self.sessions.append(data)
            continue
        self.session_view.set_data(self.sessions)

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
            if dialog.validator.validate():
                try:
                    new_user = {'username': username, 'password': password, 'role': role}
                    self.db_adapter.add_users(new_user)
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
