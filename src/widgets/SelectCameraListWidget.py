from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QListWidget
from PyQt6.QtCore import pyqtSignal, QObject

class SelectCameraSignal(QObject):
    signal = pyqtSignal(str)

class SelectCameraListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # apply style sheet
        self.listWidget = QListWidget()
        self.listWidget.addItems(['Item 0', 'Item 2', 'Item 3'])

        self.confirmButton = QPushButton('Confirm')
        self.confirmButton.clicked.connect(self.confirmSelection)

        self.exitButton = QPushButton('Exit')
        self.exitButton.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.listWidget)
        layout.addWidget(self.confirmButton)
        self.setLayout(layout)

        self.selectedCameraChanged = SelectCameraSignal()
        print(self.selectedCameraChanged.__dict__)

    def confirmSelection(self):
        selected_item = self.listWidget.currentItem()
        if selected_item is not None:
            print('Selected item:', selected_item.text())
            self.selectedCameraChanged.signal.emit(selected_item.text())
        else:
            print('No item selected')
        self.close()

    def close(self):
        self.hide()
