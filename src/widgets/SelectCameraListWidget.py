import subprocess
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QListWidget
from PyQt6.QtCore import pyqtSignal, QObject

class SelectCameraSignal(QObject):
    signal = pyqtSignal(str)

class SelectCameraListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cameraList = self.getCameraList()
        self.initUI()

    def initUI(self):
        # apply style sheet
        self.cameraListWidget = QListWidget()
        self.cameraListWidget.addItems(self.cameraList)
        print(self.cameraList)

        self.confirmButton = QPushButton('Confirm')
        self.confirmButton.clicked.connect(self.confirmSelection)

        self.exitButton = QPushButton('Exit')
        self.exitButton.clicked.connect(self.close)

        # add a refresh button to get the latest list of cameras
        self.refreshButton = QPushButton('Refresh')
        self.refreshButton.clicked.connect(self.refreshCameraList)

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
            print('Selected item:', selected_item.text())
            self.selectedCameraChanged.signal.emit(selected_item.text())
        else:
            print('No item selected')
        self.hide()

    def getCameraList(self):
        cmd = ['gphoto2', '--auto-detect']
        output = subprocess.run(cmd, capture_output=True)
        lines = output.stdout.decode('utf-8').split('\n')
        cameras = []
        for line in lines:
            if line.startswith('usb:'):
                cameras.append(line.split()[0])
        # check if any cameras were found
        if len(cameras) == 0:
            cameras.append('No cameras found')
        return cameras
    
    def refreshCameraList(self):
        self.cameraList = self.getCameraList()
        self.cameraListWidget.clear()
        self.cameraListWidget.addItems(self.cameraList)
        print(self.cameraList)
