from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, Qt, QDir, QRegularExpression
from PyQt6.QtGui import QIcon, QRegularExpressionValidator, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (QApplication, QDialog, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel, 
                             QListWidget, QHBoxLayout, QTableView, QAbstractItemView, QHeaderView, QCheckBox, 
                             QSpacerItem, QSizePolicy, QGridLayout, QMessageBox, QInputDialog, QComboBox)
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class ValidationRule:
    def __init__(self, condition, error_message, error_label):
        self.condition = condition
        self.error_message = error_message
        self.error_label = error_label

    def validate(self):
        if self.condition():
            self.error_label.setText(self.error_message)
            self.error_label.show()
            return False
        else:
            self.error_label.hide()
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

class ProjectCreator(QWidget):
    changed = pyqtSignal(str)
    close_signal = pyqtSignal(bool)

    def __init__(self, db_adapter, parent=None):
        super().__init__(parent)
        self.db_adapter = db_adapter
        layout = QVBoxLayout()
        self.setWindowTitle('Create Project')

        admin_layout = QVBoxLayout()
        self.admin = QLineEdit()
        self.admin_error_label = QLabel()
        self.admin_error_label.setStyleSheet("color: red")
        admin_layout.addWidget(self.admin_error_label)
        admin_layout.addWidget(QLabel("Administrator"))
        admin_layout.addWidget(self.admin)
        admin_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(admin_layout)

        password_layout = QVBoxLayout()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_error_label = QLabel()
        self.password_error_label.setStyleSheet("color: red")
        password_layout.addWidget(self.password_error_label)
        password_layout.addWidget(QLabel("Password"))
        password_layout.addWidget(self.password)
        password_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(password_layout) 
        
        project_name_layout = QVBoxLayout()
        self.project_name = QLineEdit()
        self.project_error_label = QLabel()
        self.project_error_label.setStyleSheet("color: red")
        project_name_layout.addWidget(self.project_error_label)
        project_name_layout.addWidget(QLabel("Project Name"))
        project_name_layout.addWidget(self.project_name)
        project_name_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(project_name_layout)

        author_layout = QVBoxLayout()
        self.authors = QLineEdit()
        regex = QRegularExpression(r'^[a-zA-Z\s,]+$')
        validator = QRegularExpressionValidator(regex)
        self.authors.setValidator(validator)
        self.author_error_label = QLabel()
        self.author_error_label.setStyleSheet("color: red")
        author_layout.addWidget(self.author_error_label)
        author_layout.addWidget(QLabel("Authors"))
        author_layout.addWidget(self.authors)
        author_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(author_layout)

        description_layout = QVBoxLayout()
        self.description = QLineEdit()
        self.description_errror_label = QLabel()
        self.description_errror_label.setStyleSheet("color: red")
        description_layout.addWidget(self.description_errror_label)
        description_layout.addWidget(QLabel("Description"))
        description_layout.addWidget(self.description)
        description_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(description_layout)

        dir_main_layout = QVBoxLayout()
        dir_layout = QHBoxLayout()
        self.dir = QLineEdit()

        self.dir_dialog = QPushButton(QIcon("resources/assets/folder.png"), "Choose")
        self.dir_dialog.clicked.connect(self.choose_dir)
        self.dir_error_label = QLabel()
        self.dir_error_label.setStyleSheet("color: red")
        
        dir_layout.addWidget(self.dir)
        dir_layout.addWidget(self.dir_dialog)

        dir_layout.setAlignment(Qt.AlignmentFlag.AlignTop) 
        dir_main_layout.addWidget(self.dir_error_label)
        dir_main_layout.addWidget(QLabel("Directory"))
        dir_main_layout.addLayout(dir_layout)
        layout.addLayout(dir_main_layout)

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_project)
        layout.addWidget(self.create_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.setLayout(layout)

    def choose_dir(self):
        file_dialog = QFileDialog()
        file_dialog.setDirectory(QDir.homePath())
        directory = file_dialog.getExistingDirectory(self, "Choose Directory")
        if directory:
            self.dir.setText(directory)

    def get_dir(self):
        return self.dir.text()

    def handle_errors(self):
        # Hide all error labels
        for label in [self.author_error_label, self.project_error_label, 
                    self.dir_error_label, self.description_errror_label]:
            label.hide()

        # Get input values
        admin = self.admin.text().strip()
        pw = self.password.text().strip()
        authors = self.authors.text().strip().split(",")
        description = self.description.text().strip()
        project_name = self.project_name.text().strip()
        project_dir = self.dir.text()

        # Create validator and add rules
        validator = InputValidator()
        validator.add_rule(ValidationRule(
            lambda: not project_name,
            "Project name cannot be empty",
            self.project_error_label
        ))
        validator.add_rule(ValidationRule(
            lambda: not project_dir or not Path(project_dir).exists(),
            "Directory does not exist",
            self.dir_error_label
        ))
        validator.add_rule(ValidationRule(
            lambda: (Path(project_dir) / project_name / 'project.ini').exists(),
            "Project already exists",
            self.dir_error_label
        ))
        validator.add_rule(ValidationRule(
            lambda: not len(authors) > 1 and not authors[0],
            "Author name cannot be empty",
            self.author_error_label
        ))
        validator.add_rule(ValidationRule(
            lambda: not description,
            "Description cannot be empty",
            self.description_errror_label
        ))
        validator.add_rule(ValidationRule(
            lambda: not admin,
            "Provide a valid name for admin login",
            self.admin_error_label
        ))
        validator.add_rule(ValidationRule(
            lambda: not pw or len(set(pw)) < 4 or any(char in pw for char in [';',',','.',':']),
            "Provide a password that has at least 4 unique characters",
            self.password_error_label
        ))
        # Run validation
        return validator.validate()

    def create_project(self):
        if self.handle_errors():
            project_info = dict()
            project_dir = (Path(self.dir.text().strip()) / self.project_name.text().strip()).as_posix()
            project_info['Project Info'] = {
                'project_dir' : project_dir,
                'creation_date': datetime.now().strftime("%Y-%m-%d"),
                'name': self.project_name.text().strip(),
                'authors': self.authors.text().strip().split(","),
                'description': self.description.text().strip(),
                'num_captures' : 0}
            
            admin_name = self.admin.text().strip()
            admin_password = self.password.text()
            users = [
                {"username": admin_name, "password": admin_password, "role": "admin"},
            ]
            self.db_adapter.create_project(project_info)
            self.db_adapter.save_encrypted_users(project_dir, users)
            self.close()

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

        layout = QVBoxLayout()

        self.dir = QLineEdit()
        layout.addWidget(QLabel("Project Directory"))
        layout.addWidget(self.dir)

        self.dir_dialog = QPushButton(QIcon("resources/assets/open.png"), "Choose Dir")
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
            self.close()
        else:
            QMessageBox.warning(self, "Failed to load project.", "INI file is invalid.")
        

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
    def __init__(self, db_adapter, sessions, parent=None):
        super().__init__(parent)
        self.db_adapter = db_adapter
        self.sessions = sessions
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Capturer
        capturer_layout = QVBoxLayout()
        self.capturer_label = QLabel("Capturer*")
        self.capturer_edit = QLineEdit()
        capturer_layout.addWidget(self.capturer_label)
        capturer_layout.addWidget(self.capturer_edit)
        layout.addLayout(capturer_layout)

        # Museum
        museum_layout = QVBoxLayout()
        self.museum_label = QLabel("Museum*")
        self.museum_edit = QLineEdit()
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

        # Keep Data Checkbox
        self.keep_data_checkbox = QCheckBox("Keep Data")
        layout.addWidget(self.keep_data_checkbox)

        # Error Label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red")
        layout.addWidget(self.error_label)

        # Spacer
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # Create Session Button
        self.create_session_button = QPushButton("Create Session")
        self.create_session_button.clicked.connect(self.create_session)
        layout.addWidget(self.create_session_button)

        self.setLayout(layout)
        self.setWindowTitle("Create Capture Session")

    def create_session(self):
        capturer = self.capturer_edit.text().strip()
        museum = self.museum_edit.text().strip()
        collection_name = self.collection_name_edit.text().strip()

        if not capturer or not museum:
            self.show_error("Capturer and Museum are mandatory fields.")
            return
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
        self.close()

        # Clear the input fields
        self.capturer_edit.clear()
        self.museum_edit.clear()
        self.collection_name_edit.clear()
        self.keep_data_checkbox.setChecked(False)
        self.hide_error()

    def show_error(self, message):
        self.error_label.setText(message)

    def hide_error(self):
        self.error_label.clear()


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
        self.project_info_list.addItem("No Project open")
        top_layout.addLayout(button_layout)
        top_layout.addLayout(project_info_layout)

        main_layout.addLayout(top_layout, 0, 0)
        main_layout.addLayout(session_layout, 1, 0)
        self.setLayout(main_layout)

        self.db_adapter.project_changed_signal.connect(self.update_project_list)
        self.db_adapter.project_changed_signal.connect(self.update_session_view)

    def create_new_session(self):
        self.new_session_window = SessionCreator(self.db_adapter, self.sessions, parent=self)
        self.new_session_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.new_session_window.exec()
        self.changed.emit("live")

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
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("Role:"))
        layout.addWidget(self.role_combo)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        
        layout.addLayout(buttons)
        self.setLayout(layout)

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
        users = self.db_adapter.get_users()  # Implement this method in your db_adapter
        for user in users:
            self.user_list.addItem(f"{user['username']} ({user['role']})")

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec():
            username = dialog.username_input.text()
            password = dialog.password_input.text()
            role = dialog.role_combo.currentText()
            
            if not username or not password:
                QMessageBox.warning(self, "Input Error", "Username and password cannot be empty.")
                return
            
            try:
                self.db_adapter.add_user(username, password, role)
                self.refresh_user_list()
                self.user_updated.emit()
                QMessageBox.information(self, "Success", f"User {username} added successfully.")
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
                    if self.db_adapter.validate_admin(admin_password):
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
