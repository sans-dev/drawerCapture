from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QGridLayout, QHBoxLayout, QPushButton

class ProjectCreationView(QWidget):
    request_open_project_view = pyqtSignal()
    def __init__(self):
        super().__init__()

        # Create a grid layout
        layout = QGridLayout()

        # Create a label
        label_names = ["Project Name", "Owner", "Description"]
        inputs = {}

        for idx, label in enumerate(label_names):
            label = label + ":"
            inputs[label] = QLineEdit()
            horizontal_layout = QHBoxLayout()
            labelWidget = QLabel(label)
            labelWidget.setFixedWidth(100)
            horizontal_layout.addWidget(labelWidget, stretch=1)
            horizontal_layout.addWidget(inputs[label], stretch=3)
            layout.addLayout(horizontal_layout, idx, 0, alignment=Qt.AlignmentFlag.AlignRight)

        # create layout for directory selection
        directory_layout = QHBoxLayout()
        directory_layout.addWidget(QLabel("Directory"))
        dir_text_label = QLabel("No directory selected")
        directory_layout.addWidget(dir_text_label, alignment=Qt.AlignmentFlag.AlignLeft)
        directory_layout.addWidget(QPushButton("Select Directory"), alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(directory_layout, 3, 0)

        self.createButton = QPushButton("Create")
        self.cancelButton = QPushButton("Cancel")        
        layout.addWidget(self.createButton, 4, 0)
        layout.addWidget(self.cancelButton, 4, 1)
        layout.setVerticalSpacing(10)
        self.createButton.clicked.connect(self.request_open_project_view)

        # Set the layout on the application's window
        self.setLayout(layout)

    def open_project_view(self):
        self.request_open_project_view.emit()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    project_creation_view = ProjectCreationView()
    project_creation_view.show()
    sys.exit(app.exec())
