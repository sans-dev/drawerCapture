import subprocess
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QListWidget
from PyQt6.QtCore import pyqtSignal, QObject, QThread

class SelectCameraSignal(QObject):
    signal = pyqtSignal(str)

class SelectCameraListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cameraFetcher = CameraFetcher()
        self.initUI()

    def initUI(self):
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

        layout = QVBoxLayout()
        layout.addWidget(self.refreshButton)
        layout.addWidget(self.cameraListWidget)
        layout.addWidget(self.confirmButton)
        layout.addWidget(self.exitButton)
        self.setLayout(layout)

        # add a wait for response widget while camera list is being fetched

        # add a signal to emit when a camera is selected
        self.selectedCameraChanged = SelectCameraSignal()

    def confirmSelection(self):
        selected_item = self.cameraListWidget.currentItem()
        if selected_item is not None:
            self.selectedCameraChanged.signal.emit(selected_item.text())
            self.selectedCameraData  = self.cameraFetcher.getCameraData(selected_item.text())
        self.hide()

    def refreshButtonClicked(self):
        self.refreshButton.setEnabled(False)
        self.confirmButton.setEnabled(False)
        self.cameraFetcher.finished.connect(self.updateCameraList)
        self.cameraFetcher.start()

    def updateCameraList(self, cameras):
        self.cameraListWidget.clear()
        if not cameras[0] == 'No cameras found':
            self.confirmButton.setEnabled(True)
        for camera in cameras:
            self.cameraListWidget.addItem(camera)
        self.refreshButton.setEnabled(True)

class CameraFetcher(QThread):
    finished  = pyqtSignal(list)

    def run(self):
        cmd = ['gphoto2', '--auto-detect']
        output = subprocess.run(cmd, capture_output=True)
        lines = output.stdout.decode('utf-8').split('\n')
        cameras = []
        self.cameras_data = []
        for line in lines:
            if 'usb:' in line:
                cameras.append(line.split('usb:')[0])
                self.cameras_data.append(line)
        # check if any cameras were found
        if len(cameras) == 0:
            cameras.append('No cameras found')
        self.finished.emit(cameras)

    def getCameraData(self, camera):
        for camera_data in self.cameras_data:
            if camera in camera_data:
                return camera_data
        return None

