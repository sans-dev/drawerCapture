import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout
from PyQt6.QtCore import pyqtSignal, Qt

from widgets import ImagePanel, DataCollectionTextField
from signals import ProcessEmitter

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class ImageWidget(QWidget):
    changed = pyqtSignal(str)
    procClicked = pyqtSignal(str)
    processed = pyqtSignal()

    def __init__(self):
        self.emitter = ProcessEmitter()
        self.panel = ImagePanel(self.emitter)
        logger.debug("initializing image widget")
        super().__init__()
        self.initUI()
        self.connectSignals()

    def initUI(self):
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
        self.panelLayout.addLayout(self.buttonLayout, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # add the collectionField right to the layout
        self.layout = QGridLayout()
        self.layout.addLayout(self.panelLayout, 0, 0)
        self.layout.addWidget(self.collectionField, 0, 1)
        self.setLayout(self.layout)

    def connectSignals(self):
        self.closeButton.clicked.connect(self.close)
        self.enhanceButton.clicked.connect(self.enhanceButtonClicked)
        self.procClicked.connect(self.panel.processImage)
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.emitter.processed.connect(self.enableButtons)

    def close(self):
        self.changed.emit("live")
        super().close()

    def enableButtons(self):
        logger.debug("enabling buttons")
        self.cropButton.setEnabled(True)
        self.enhanceButton.setEnabled(True)
        self.saveButton.setEnabled(True)
        self.closeButton.setEnabled(True)

    def disableButtons(self):
        logger.debug("disabling buttons")
        self.cropButton.setEnabled(False)
        self.enhanceButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.closeButton.setEnabled(False)
    
    def setImage(self, image_path):
        logger.debug("updating image widget with new image: %s", image_path)
        self.panel.loadImage(image_path)
        self.enableButtons()

    def enhanceButtonClicked(self):
        self.procClicked.emit("adaptive_he")

    def saveButtonClicked(self):
        # open a file dialog to save the image
        logger.info("saving image")
        self.panel.saveImage()