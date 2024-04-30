from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt6.QtCore import pyqtSignal

class ProjectCreator(QWidget):
    changed = pyqtSignal(str)

    def __init__(self, db_adapter):
        super().__init__()
        self.db_adapter = db_adapter

        layout = QVBoxLayout()

        self.project_name = QLineEdit()
        layout.addWidget(QLabel("Project Name"))
        layout.addWidget(self.project_name)

        self.author = QLineEdit()
        layout.addWidget(QLabel("Author"))
        layout.addWidget(self.author)

        self.description = QLineEdit()
        layout.addWidget(QLabel("Description"))
        layout.addWidget(self.description)

        self.dir = QLineEdit()
        layout.addWidget(QLabel("Dir"))
        layout.addWidget(self.dir)

        self.dir_dialog = QPushButton("Choose Directory")
        self.dir_dialog.clicked.connect(self.choose_dir)
        layout.addWidget(self.dir_dialog)

        self.create_button = QPushButton("Create Project")
        self.create_button.clicked.connect(self.create_project)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def choose_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose Directory")
        if directory:
            self.dir.setText(directory)

    def get_dir(self):
        return self.dir.text()
    
    def create_project(self):
        project_dir = self.dir.text()
        project_info = dict()
        project_info['INFO'] = {'Project Name': self.project_name.text(),
                             'Author': self.author.text(),
                             'Description': self.description.text()}
        project_info['VARS'] = { 'image-number' : 0}
        self.db_adapter.create_project(project_info, project_dir)
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
        directory = QFileDialog.getExistingDirectory(self, "Choose Project Directory")
        if directory:
            self.dir.setText(directory)

    def load_project(self):
        project_dir = self.dir.text()
        self.db_adapter.load_project(project_dir)
        self.changed.emit("live")
    
if __name__ == "__main__":
    app = QApplication([])
    window = ProjectCreator()
    window.show()
    app.exec()
