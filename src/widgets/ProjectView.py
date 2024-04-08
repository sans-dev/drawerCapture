from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QLineEdit, QGridLayout, QVBoxLayout, QScrollArea, QButtonGroup, QRadioButton

from .SessionDataButton import SessionDataButton
from .SessionDataList import SessionDataList

class ProjectView(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout(self)

        self.new_session_button = QPushButton("New Session")
        self.new_session_button.clicked.connect(self.open_new_session_dialog)
        self.layout.addWidget(self.new_session_button, 1, 1)

        self.search_bar = QLineEdit("Search Collection")
        self.layout.addWidget(self.search_bar, 1, 2)

        self.sort_button_group = QButtonGroup(self)
        self.drawer_button = QRadioButton("Drawers")
        self.drawer_button.clicked.connect(self.change_to_drawers)
        self.session_button = QRadioButton("Sessions")
        self.session_button.clicked.connect(self.change_to_sessions)
        self.sort_button_group.addButton(self.drawer_button, 1)
        self.sort_button_group.addButton(self.session_button, 2)
        self.layout.addWidget(self.drawer_button, 2, 1)
        self.layout.addWidget(self.session_button, 2, 2)

        self.project_data_view = QScrollArea(self)
        self.project_data_view.setWidgetResizable(True)
        self.project_data_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.project_data_list = SessionDataList()
        self.project_data_view.setWidget(self.project_data_list)

        self.project_data_list.add_session(SessionDataButton())
        self.project_data_list.add_session(SessionDataButton())
        
        self.layout.addWidget(self.project_data_view, 3, 1, 1, 2)

    def open_new_session_dialog(self):
        # Implement the functionality to open a dialog for creating a new session
        pass

    def change_to_drawers(self):
        # Implement the functionality to change the ProjectView to Drawers instead of Sessions
        pass

    def change_to_sessions(self):
        # Implement the functionality to change the ProjectView to Sessions instead of Drawers
        pass

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    project_view = ProjectView()
    project_view.show()
    sys.exit(app.exec())