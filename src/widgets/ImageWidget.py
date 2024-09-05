'''
Module: ImageWidget

Author: Sebastian Sander

A module that contains the ImageWidget class, which is a widget that displays an image and provides buttons to crop, enhance, save, and close the image.

'''

import logging
import logging.config
import cv2
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QPushButton, QMessageBox, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from src.widgets.DataCollection import DataCollection

logging.config.fileConfig('configs/logging/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class HistogramWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        self.image_path = image_path
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Histogram')
        self.setWindowIcon(QIcon('resources/assets/histogram.png'))
        # Create Matplotlib figure and canvas
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot_histogram()

    def plot_histogram(self):
        # Load the image
        img = cv2.imread(self.image_path)

        if img is None:
            print("Error loading image.")
            return

        # Calculate RGB histograms
        hist_r = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([img], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([img], [2], None, [256], [0, 256])

        # Flatten the histogram arrays to 1D
        hist_r = hist_r.flatten()
        hist_g = hist_g.flatten()
        hist_b = hist_b.flatten()

        # Plot the histogram on the Matplotlib canvas
        ax = self.figure.add_subplot(111)
        ax.plot(hist_r, color='red', label='Red')
        ax.plot(hist_g, color='green', label='Green')
        ax.plot(hist_b, color='blue', label='Blue')
        # Fill the area under each histogram curve
        ax.fill_between(range(len(hist_r)), hist_r, alpha=0.3, color='red') 
        ax.fill_between(range(len(hist_g)), hist_g, alpha=0.3, color='green')
        ax.fill_between(range(len(hist_b)), hist_b, alpha=0.3, color='blue')
        ax.set_xlabel('Pixel Intensity')
        ax.set_ylabel('Frequency')

        self.canvas.draw()


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
        self.histogram_button.clicked.connect(self.show_histogram)

    def show_histogram(self):
        self.histogram_window = HistogramWidget(self.img_dir)
        self.histogram_window.show()

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
        try:
            if self.db_adapter.save_image_data(payload):
                if QMessageBox.question(self, 'Title', ' Image and metadata saved! Go to capture mode?').name == 'Yes':    
                    self.close()
        except Exception as e:
            QMessageBox.warning(self, "Something went wrong", str(e))

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