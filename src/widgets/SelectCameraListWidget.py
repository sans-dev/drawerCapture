import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QListWidget, QLabel, QStackedWidget
from PyQt6.QtCore import pyqtSignal, Qt

from src.threads.CameraFetcher import CameraFetcher
from src.widgets.SpinnerWidget import LoadingSpinner
logger = logging.getLogger(__name__)

class SelectCameraListWidget(QWidget):
    """
    A widget that displays a list of available cameras and allows the user to select one.

    Attributes:
        selectedCameraChanged (pyqtSignal): A signal emitted when the selected camera changes.
        closed (pyqtSignal): A signal emitted when the widget is closed.
        refreshing (pyqtSignal): A signal emitted when the camera list is being refreshed.

    """
    selectedCameraChanged = pyqtSignal(str)
    closed = pyqtSignal()
    refreshing = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initializes the widget.

        Args:
            parent (QWidget): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.isRefreshed = False
        self.cameraFetcher = CameraFetcher()
        self.loadingSpinner = LoadingSpinner()
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface of the widget.
        """
        # apply style sheet
        self.cameraListWidget = QListWidget()

        self.confirmButton = QPushButton('Confirm')
        self.confirmButton.clicked.connect(self.confirmSelection)
        self.confirmButton.setEnabled(False)

        self.exitButton = QPushButton('Exit')
        self.exitButton.clicked.connect(self.close)

        # add a refresh button to get the latest list of cameras
        self.refreshButton = QPushButton('Refresh')
        self.refreshButton.clicked.connect(self.refreshButtonClicked)

        # add a label to the widget with bigger text
        self.widgetLabel = QLabel('Select a camera')
        self.widgetLabel.setStyleSheet('font-size: 20px;')

        self.list_spinner_stack = QStackedWidget()
        self.list_spinner_stack.addWidget(self.cameraListWidget)
        self.list_spinner_stack.addWidget(self.loadingSpinner)

        layout = QVBoxLayout()
        layout.addWidget(self.widgetLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.list_spinner_stack)
        layout.addWidget(self.refreshButton)
        layout.addWidget(self.confirmButton)
        layout.addWidget(self.exitButton)
        self.setLayout(layout)

        self.cameraListWidget.itemSelectionChanged.connect(self.enableConfirmButton)
        self.cameraFetcher.finished.connect(self.updateCameraList)
        self.cameraFetcher.finished.connect(self.enableRefrehsButton)

        self.cameraFetcher.started.connect(self.loadingSpinner.start)
        self.cameraFetcher.started.connect(self.loadingSpinner.show)
        self.cameraFetcher.started.connect(self.show_spinner)
        self.cameraFetcher.finished.connect(self.loadingSpinner.stop)
        self.cameraFetcher.finished.connect(self.loadingSpinner.hide)
        self.cameraFetcher.finished.connect(self.hide_spinner)

    def show_spinner(self):
        self.list_spinner_stack.setCurrentWidget(self.loadingSpinner)

    def hide_spinner(self):
        self.list_spinner_stack.setCurrentWidget(self.cameraListWidget)

    def confirmSelection(self):
        """
        Confirms the selected camera and emits the selectedCameraChanged signal.
        """
        logger.debug("confirming selection")
        selected_item = self.cameraListWidget.currentItem()
        if selected_item is not None:
            self.selectedCameraData  = self.cameraFetcher.getCameraData(selected_item.text())
            self.selectedCameraChanged.emit(self.selectedCameraData)

    def refreshButtonClicked(self):
        """
        Refreshes the list of available cameras.
        """
        logger.debug("refreshing camera list")
        self.refreshButton.setEnabled(False)
        self.confirmButton.setEnabled(False)
        self.refreshing.emit()
        self.cameraFetcher.start()
        self.isRefreshed = True

    def updateCameraList(self, cameras):
        """
        Updates the list of available cameras.

        Args:
            cameras (list): A list of available cameras.
        """
        logger.debug("updating camera list")
        self.cameraListWidget.clear()
        for camera in cameras:
            self.cameraListWidget.addItem(camera)
        self.cameraFetcher.quit()

    def enableConfirmButton(self):
        """
        Enables the confirm button if a camera is selected.
        """
        logger.debug("enabling confirm button")
        if self.cameraListWidget.currentItem().text() != 'No cameras found':
            self.confirmButton.setEnabled(True)

    def enableRefrehsButton(self):
        """
        Enables the refresh button.
        """
        logger.debug("enabling refresh button")
        self.refreshButton.setEnabled(True)

    def close(self):
        """
        Closes the widget and emits the closed signal.
        """
        logger.debug("closing select camera list widget")
        self.cameraFetcher.quit() 
        self.closed.emit()

        super().close()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from argparse import ArgumentParser
    
    app = QApplication(sys.argv)
    window = SelectCameraListWidget()
    window.show()
    sys.exit(app.exec())
