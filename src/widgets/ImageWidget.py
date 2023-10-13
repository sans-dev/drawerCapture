import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout
from PyQt6.QtCore import pyqtSignal

from widgets import PreviewPanel, DataCollectionTextField

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class ImageWidget(QWidget):
    changed = pyqtSignal(str)

    def __init__(self):
        logger.debug("initializing image widget")
        super().__init__()
        self.initUI()
        self.connectSignals()

    def initUI(self):
        self.panel = PreviewPanel()
        self.collectionField = DataCollectionTextField()
        # create a horizontal layout for the buttons (crop, enahnce, save, close)
        self.buttonLayout = QGridLayout()
        self.cropButton = QPushButton("Crop")
        self.enhanceButton = QPushButton("Enhance")
        self.saveButton = QPushButton("Save")
        self.closeButton = QPushButton("Close")
        self.buttonLayout.addWidget(self.cropButton, 0, 0)
        self.buttonLayout.addWidget(self.enhanceButton, 0, 1)
        self.buttonLayout.addWidget(self.saveButton, 0, 2)
        self.buttonLayout.addWidget(self.closeButton, 0, 3)
        # create a vertical layout for the panel and buttons
        self.panelLayout = QGridLayout()
        self.panelLayout.addWidget(self.panel, 0, 0)
        self.panelLayout.addWidget(self.collectionField, 0, 1,1,1)
        self.panelLayout.addLayout(self.buttonLayout, 2, 0)
        # add the collectionField right to the layout
        self.layout = QGridLayout()
        self.layout.addLayout(self.panelLayout, 0, 0)
        self.layout.addWidget(self.collectionField, 0, 1)
        self.setLayout(self.layout)
        self.disableButtons()

    def connectSignals(self):
        self.closeButton.clicked.connect(self.close)

    def close(self):
        self.changed.emit("live")
        super().close()

    def enableButtons(self):
        self.cropButton.setEnabled(True)
        self.enhanceButton.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.closeButton.setEnabled(True)

    def disableButtons(self):
        self.cropButton.setEnabled(False)
        self.enhanceButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.closeButton.setEnabled(False)