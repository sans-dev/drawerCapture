import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal

from src.widgets.DataCollection import DataCollection
from src.widgets.ImagePanel import ImagePanel
from src.signals.ProcessEmitter import ProcessEmitter

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class ImageWidget(QWidget):
    """
    A widget that displays an image and provides buttons to crop, enhance, save and close the image.
    """
    changed = pyqtSignal(str)
    procClicked = pyqtSignal(str)
    processed = pyqtSignal()

    def __init__(self, db_adapter, taxonomy, geo_data_dir):
        self.taxonomy = taxonomy
        self.db_adapter = db_adapter
        self.geo_data_dir = geo_data_dir
        self.emitter = ProcessEmitter()
        self.panel = ImagePanel(self.emitter)
        logger.debug("initializing image widget")
        super().__init__()
        self.initUI()
        self.connectSignals()

    def initUI(self):
        """
        Initializes the user interface of the widget.
        """
        self.data_collector = DataCollection(self.taxonomy, geo_data_dir=self.geo_data_dir)
        # create a horizontal layout for the buttons (crop, enahnce, save, close)
        # create a vertical layout for the panel and buttons
        # add the collectionField right to the layout
        layout = QGridLayout()
        layout.addWidget(self.panel, 0, 0)
        layout.addWidget(self.data_collector, 0, 1)

        button_layout = QHBoxLayout()
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_data)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout,1,1)

        self.setLayout(layout)

    def connectSignals(self):
        """
        Connects the signals of the buttons to their respective functions.
        """
        self.procClicked.connect(self.panel.processImage)
        self.emitter.processed.connect(self.enableButtons)
        self.db_adapter.session_created_signal.connect(self.data_collector.set_session_data)

    def close(self):
        """
        Closes the widget and emits a signal to switch to live mode. 
        """
        self.changed.emit("live")
        super().close()

    def enableButtons(self):
        """
        Enables the buttons of the widget.
        """
        logger.debug("enabling buttons")

    def disableButtons(self):
        """
        Disables the buttons of the widget.
        """
        logger.debug("disabling buttons")
    
    def setImage(self, image_path):
        """
        Sets the image of the widget to the specified image path.
        """
        logger.debug("updating image widget with new image: %s", image_path)
        self.panel.loadImage(image_path)
        self.enableButtons()

    def enhanceButtonClicked(self):
        """
        Emits a signal indicating that the enhance button has been clicked.
        """
        self.procClicked.emit("adaptive_he")

    def save_data(self):
        """
        Opens a file dialog to save the image.
        """
        logger.info("Retreiving image data from Panel")
        image_data = self.panel.get_image()
        logger.info("Retreiving meta info from Panel")
        meta_info = self.data_collector.get_data()
        logger.info("Send data to db")
        
        if self.db_adapter.send_data_to_db(image_data, meta_info):
            if QMessageBox.question(self, 'Title', 'Data where saved into database. Continue capturing?').name == 'Yes':    
                self.close()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from src.db.DB import DBAdapter, DummyDB
    from argparse import ArgumentParser
    from src.utils.searching import init_taxonomy
    from src.configs.DataCollection import *

    parser = ArgumentParser()
    parser.add_argument('--taxonomy', choices=['test', 'prod'])
    parser.add_argument('--geo-data', choices=['level-0', 'level-1'])
    args = parser.parse_args()
    taxonomy = init_taxonomy(TAXONOMY[args.taxonomy])
    db = DummyDB()
    db_adapter = DBAdapter(db)
    geo_data_dir = GEO[args.geo_data]
    
    app = QApplication(sys.argv)
    window = ImageWidget(db_adapter, taxonomy, geo_data_dir)
    window.setImage("tests/data/test_img.jpg")
    window.show()
    db_adapter.session_created_signal.emit(
        {
            'Name' : 'Session 1',
            'ID' : '1',
            'Capturer' : 'Sebastian',
            'Museum' : 'Senkenberg Frankfurt'
        }
    )
    sys.exit(app.exec())
