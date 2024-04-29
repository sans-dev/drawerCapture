import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)

from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QListWidget, QLabel
from PyQt6.QtCore import pyqtSignal, Qt

from src.threads.CameraFetcher import CameraFetcher

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
        self.cameraFetcher = CameraFetcher()
        self.initUI()

        self.isRefreshed = False

    def initUI(self):
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

        layout = QVBoxLayout()
        layout.addWidget(self.widgetLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.cameraListWidget)
        layout.addWidget(self.refreshButton)
        layout.addWidget(self.confirmButton)
        layout.addWidget(self.exitButton)
        self.setLayout(layout)

        self.cameraListWidget.itemSelectionChanged.connect(self.enableConfirmButton)
        self.cameraFetcher.finished.connect(self.updateCameraList)
        self.cameraFetcher.finished.connect(self.enableRefrehsButton)

    def confirmSelection(self):
        """
        Confirms the selected camera and emits the selectedCameraChanged signal.
        """
        logger.debug("confirming selection")
        selected_item = self.cameraListWidget.currentItem()
        if selected_item is not None:
            self.selectedCameraData  = self.cameraFetcher.getCameraData(selected_item.text())
            self.selectedCameraChanged.emit(self.selectedCameraData)
        self.hide()

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