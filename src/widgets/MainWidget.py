from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout

class MainWidget(QWidget):
    """
    This class represents the main widget of the DrawerCapture application.
    It contains two buttons to switch between live and offline mode.
    """
    def __init__(self):
        super().__init__()
        self.ProjectCreationWidget = None
        self.ProjectLoadingWidget = None
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface of the main widget.
        """
        self.setWindowTitle("DrawerCapture")

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Create the widgets
        self.create_new_project_bt = QPushButton("Create New Project")
        self.open_project_bt = QPushButton("Open Project")
        
        # Add the widgets to the layout
        self.layout.addWidget(self.create_new_project_bt, 0, 0, 1, 1)
        self.layout.addWidget(self.open_project_bt, 0, 1, 1, 1)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
    sys.exit(app.exec())