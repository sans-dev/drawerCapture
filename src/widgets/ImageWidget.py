import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout
from PyQt6.QtCore import pyqtSignal

from widgets import PreviewPanel, DataCollectionTextField

import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QPushButton, QGridLayout
from PyQt6.QtCore import pyqtSignal

from widgets import PreviewPanel, DataCollectionTextField

import logging
import logging.config

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class ImageWidget(QWidget):
    """
    A widget for displaying and manipulating images.

    Signals:
        changed: A signal emitted when the image is changed.

    Methods:
        __init__: Initializes the ImageWidget.
        initUI: Initializes the user interface.
        connectSignals: Connects signals to slots.
        closeEvent: Overrides the close event to emit the changed signal.
    """
    changed = pyqtSignal(str)

    def __init__(self):
        logger.debug("initializing image widget")
        super(ImageWidget, self).__init__()
        self.initUI()
        self.connectSignals()

    def initUI(self):
        """
        Initializes the user interface.
        """
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

    def connectSignals(self):
        """
        Connects signals to slots.
        """
        pass

    def closeEvent(self, event):
        """
        Overrides the close event to emit the changed signal.
        """
        ImageWidget.changed.emit("live")
        super(ImageWidget, self).closeEvent(event)
