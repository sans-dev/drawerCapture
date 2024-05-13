from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel, QListWidget, QHBoxLayout,QTableView, QAbstractItemView, QHeaderView
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem


class ProjectCreator(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, db_adapter):
        super().__init__()
        self.db_adapter = db_adapter

        layout = QVBoxLayout()

        project_name_layout = QVBoxLayout()
        self.project_name = QLineEdit()
        self.project_error_label = QLabel()
        self.project_error_label.setStyleSheet("color: red")
        project_name_layout.addWidget(QLabel("Project Name"))
        project_name_layout.addWidget(self.project_name)
        project_name_layout.addWidget(self.project_error_label)
        project_name_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(project_name_layout)

        author_layout = QVBoxLayout()
        self.authors = QLineEdit()
        regex = QRegularExpression(r'^[a-zA-Z\s,]+$')
        validator = QRegularExpressionValidator(regex)
        self.authors.setValidator(validator)
        self.author_error_label = QLabel()
        self.author_error_label.setStyleSheet("color: red")
        author_layout.addWidget(QLabel("Author"))
        author_layout.addWidget(self.authors)
        author_layout.addWidget(self.author_error_label)
        author_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(author_layout)

        description_layout = QVBoxLayout()
        self.description = QLineEdit()
        self.description_errror_label = QLabel()
        self.description_errror_label.setStyleSheet("color: red")
        description_layout.addWidget(QLabel("Description"))
        description_layout.addWidget(self.description)
        description_layout.addWidget(self.description_errror_label)
        description_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(description_layout)

        dir_layout = QVBoxLayout()
        self.dir = QLineEdit()

        self.dir_dialog = QPushButton("Choose Directory")
        self.dir_dialog.clicked.connect(self.choose_dir)
        self.dir_error_label = QLabel()
        self.dir_error_label.setStyleSheet("color: red")
        dir_layout.addWidget(QLabel("Project Directory"))
        dir_layout.addWidget(self.dir)
        dir_layout.addWidget(self.dir_error_label)
        dir_layout.addWidget(self.dir_dialog)
        dir_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(dir_layout)

        self.create_button = QPushButton("Create Project")
        self.create_button.clicked.connect(self.create_project)
        layout.addWidget(self.create_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.setLayout(layout)

    def choose_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose Directory")
        if directory:
            self.dir.setText(directory)

    def get_dir(self):
        return self.dir.text()

    def handle_errors(self):
        self.author_error_label.hide()
        self.project_error_label.hide()
        self.dir_error_label.hide()
        self.description_errror_label.hide()

        authors = self.authors.text().strip().split(",")
        description = self.description.text().strip()
        project_name = self.project_name.text().strip()
        project_dir = self.dir.text()

        is_valid = True 
        if not project_name:
            self.project_error_label.setText("Project name cannot be empty")
            self.project_error_label.show()
            is_valid = False
        if not project_dir or not Path(project_dir).exists():
            self.dir_error_label.setText("Directory does not exist")
            self.dir_error_label.show()
            is_valid = False
        if (Path(project_dir) / project_name / 'project.ini').exists():
            self.dir_error_label.setText("Project already exists")
            self.dir_error_label.show()
            is_valid = False
        if not authors:
            self.author_error_label.setText("Author name cannot be empty")
            self.author_error_label.show()
            is_valid = False
        if not description:
            self.description_errror_label.setText("Description cannot be empty")
            self.description_errror_label.show()
            is_valid = False
        return is_valid

    def create_project(self):
        if self.handle_errors():
            project_info = dict()
            project_info['Project Info'] = {
                'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'name': self.project_name.text().strip(),
                'authors': self.authors.text().strip().split(","),
                'description': self.description.text().strip()}
            project_info['Captures Info'] = {'num_imgs': 0}
            self.db_adapter.create_project(project_info, self.dir.text().strip())
            self.changed.emit("project")


class ProjectLoader(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, db_adapter):
        super().__init__()
        self.db_adapter = db_adapter

        layout = QVBoxLayout()

        self.dir = QLineEdit()
        layout.addWidget(QLabel("Project Directory"))
        layout.addWidget(self.dir)

        self.dir_dialog = QPushButton("Choose Project Directory")
        self.dir_dialog.clicked.connect(self.choose_dir)
        layout.addWidget(self.dir_dialog)

        self.load_button = QPushButton("Load Project")
        self.load_button.clicked.connect(self.load_project)
        layout.addWidget(self.load_button)

        self.setLayout(layout)

    def choose_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Choose Project Directory")
        if directory:
            self.dir.setText(directory)

    def load_project(self):
        project_dir = self.dir.text()
        self.db_adapter.load_project(project_dir)
        self.changed.emit("project")


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

        # Set the table model (you need to provide the data)
        self.table_model = None  # Replace with your data model

        self.table_view.setModel(self.table_model)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        self.setLayout(layout)

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
class CaptureViewer(QWidget):
    pass

class ProjectViewer(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, db_adapter):
        super().__init__()
        self.session_view = SessionViewer()
        self.db_adapter = db_adapter
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        button_layout = QVBoxLayout()
        self.project_info_list = QListWidget()
        top_layout.addWidget(self.project_info_list)
        self.new_session_button = QPushButton("New Capture Session")
        self.close_project_button = QPushButton("Close Project")
        button_layout.addWidget(self.new_session_button)
        button_layout.addWidget(self.close_project_button)
        top_layout.addLayout(button_layout)
        self.new_session_button.clicked.connect(self.new_session)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.session_view)
        self.setLayout(main_layout)
        self.db_adapter.project_changed_signal.connect(self.update_project_list)
        self.db_adapter.project_changed_signal.connect(self.update_session_view)
        self.close_project_button.clicked.connect(self.close_project)

    def close_project(self):
        self.changed.emit("main")
        super().close()

    def update_project_list(self, project_info):
        print(project_info)
        self.project_info_list.clear()
        project_info = project_info['Project Info']
        item_strings = self._create_project_info_item_str_list(project_info)
        self.project_info_list.addItems(item_strings)

    def _create_project_info_item_str_list(self, project_info):
        item_strings = []
        for key, value in project_info.items():
            item_strings.append(f"{key}: {value}")
        return item_strings
    
    def update_session_view(self, project_info):
        print(project_info)
        pass

    def new_session(self):
        self.changed.emit("live")



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
