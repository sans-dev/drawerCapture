from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt6.QtCore import QDir
import os
import configparser
from PyQt6.QtCore import pyqtSignal

class ProjectCreator(QWidget):
    changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

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

    def create_project(self):
        directory = self.dir.text()
        if not QDir().exists(directory):
            QDir().mkpath(directory)

        config = configparser.ConfigParser()
        config['PROJECT'] = {'Project Name': self.project_name.text(),
                             'Author': self.author.text(),
                             'Description': self.description.text()}
        config['VARS'] = {
            'img-number'
        }

        with open(os.path.join(directory, 'project.ini'), 'w') as configfile:
            config.write(configfile)

        QDir().mkdir(os.path.join(directory, "Captures"))
        with open(os.path.join(directory, "captures.csv"), 'w') as f:
            f.write("date, session, museum, order, family, genus, species\n")
        self.changed.emit("live")

if __name__ == "__main__":
    app = QApplication([])
    window = ProjectCreator()
    window.show()
    app.exec()
