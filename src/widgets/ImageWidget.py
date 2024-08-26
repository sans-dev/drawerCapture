import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
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
    close_signal = pyqtSignal(bool)

    def __init__(self, db_adapter, taxonomy, geo_data_dir, panel):
        self.taxonomy = taxonomy
        self.db_adapter = db_adapter
        self.geo_data_dir = geo_data_dir
        self.panel = panel
        self.panel.label.hide()
        logger.debug("initializing image widget")
        super().__init__()
        self.initUI()
        self.connect_signals()

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
        self.save_button = QPushButton("Save")
        self.histogram_button = QPushButton(QIcon('resources/assets/histogram.png'), "Show Histogram")
        self.add_box_button = QPushButton(QIcon('resources/assets/rectangle.png'), "Add Bounding Box")

        image_button_layout = QHBoxLayout()
        image_button_layout.addWidget(self.add_box_button)
        image_button_layout.addWidget(self.histogram_button)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(image_button_layout, 1,0)
        layout.addLayout(button_layout,1,1)

        self.setLayout(layout)

    def connect_signals(self):
        self.close_button.clicked.connect(self.close)
        self.save_button.clicked.connect(self.savedata)
        self.db_adapter.sessions_signal.connect(self.set_session_data)
        self.panel.image_captured.connect(self.set_img_dir)

    def set_session_data(self, sessions):
        sessions_ids = list(sessions.keys())
        if sessions_ids:
            self.sid = sessions_ids[-1]
            self.current_session = sessions[self.sid]
            self.data_collector.set_session_data(self.current_session)

    def set_img_dir(self, img_dir):
        self.img_dir = img_dir

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

    def enhanceButtonClicked(self):
        """
        Emits a signal indicating that the enhance button has been clicked.
        """
        self.procClicked.emit("adaptive_he")

    def savedata(self):
        """
        Opens a file dialog to save the image.
        """
        logger.info("Retreiving meta info from Panel")
        meta_info = self.data_collector.get_data()
        logger.info("Send data to db")
        payload = {
            'img_dir' : self.img_dir,
            'meta_info' : meta_info,
            'sid' : self.sid
        }
        if self.db_adapter.save_image_data(payload):
            if QMessageBox.question(self, 'Title', ' Image and metadata saved! Go to capture mode?').name == 'Yes':    
                self.close()

    def closeEvent(self, event):
        self.close_signal.emit(True)
        super().closeEvent(event)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from src.db.DB import DBAdapter, DummyDB
    from argparse import ArgumentParser
    from src.utils.searching import init_taxonomy
    from src.configs.DataCollection import *
    from src.utils.load_style_sheet import load_style_sheet
    from src.widgets.PreviewPanel import PreviewPanel

    parser = ArgumentParser()
    parser.add_argument('--taxonomy', choices=['test', 'prod'])
    parser.add_argument('--geo-data', choices=['level-0', 'level-1'])
    args = parser.parse_args()
    taxonomy = init_taxonomy(TAXONOMY[args.taxonomy])
    db = DummyDB()
    db_adapter = DBAdapter(db)
    db_adapter.load_project("")
    geo_data_dir = GEO[args.geo_data]
    app = QApplication(sys.argv)
    app.setStyleSheet(load_style_sheet('PicPax'))
    panel = PreviewPanel(fs=1, panel_res=(1024, 780))
    window = ImageWidget(db_adapter, taxonomy, geo_data_dir, panel)
    session_data = {
            "capturer": "Bernd",
            "museum": "das",
            "collection_name": "Brot",
            "date": "1231231",
            "num_captures": "0"
        }
    db_adapter.create_session(session_data)
    window.panel.on_image_captured("tests/data/test_img.jpg")
    window.show()
    sys.exit(app.exec())