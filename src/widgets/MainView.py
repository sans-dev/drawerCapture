from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout
from PyQt6.QtCore import pyqtSignal

class MainView(QWidget):
    """
    This class represents the main widget of the DrawerCapture application.
    It contains two buttons to switch between live and offline mode.
    """
    new_project_requested = pyqtSignal()
    open_project_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface of the main widget.
        """
        self.setWindowTitle("DrawerCapture")

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Create the widgets
        self.create_new_project_bt = QPushButton("Create New Project")
        self.open_project_bt = QPushButton("Open Project")
        self.create_new_project_bt.clicked.connect(self.open_project_creation_view)
        
        # Add the widgets to the layout
        self.layout.addWidget(self.create_new_project_bt, 0, 0, 1, 1)
        self.layout.addWidget(self.open_project_bt, 0, 1, 1, 1)


    def open_project_creation_view(self):
        """
        Opens the project creation widget.
        """
        self.new_project_requested.emit()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    main_widget = MainView()
    main_widget.show()
    sys.exit(app.exec())