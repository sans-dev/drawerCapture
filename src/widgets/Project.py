from pathlib import Path

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtCore import pyqtSignal, Qt


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
            project_info['INFO'] = {'Name': self.project_name.text().strip(),
                                    'Author': self.authors.text().strip().split(","),
                                    'Description': self.description.text().strip()}
            project_info['VARS'] = {'image-number': 0}
            self.db_adapter.create_project(project_info, self.dir.text().strip())
            self.changed.emit("live")


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
        self.changed.emit("live")


if __name__ == "__main__":
    from src.db.DB import DBAdapter, DBManager
    db_adapter = DBAdapter()
    db_manager = DBManager()
    db_manager.connect_db_adapter(db_adapter)

    app = QApplication([])
    window = ProjectCreator(db_adapter)
    window.show()
    app.exec()
