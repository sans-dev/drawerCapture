import logging
import logging.config

from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import  QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QSize

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        logger.debug("initializing loading spinner")
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Set the widget's layout as a vertical box layout
        logger.debug("initializing loading spinner UI")
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Create a QLabel to display the GIF image
        self.label = QLabel(self)
        layout.addWidget(self.label)

        # Load and start the GIF animation
        self.movie = QMovie("resources/assets/Spinner-1s-200px.gif")
        # make movie smaller
        self.movie.setScaledSize(QSize(100, 100))
        self.label.setMovie(self.movie)

    def start(self):
        logger.debug("starting loading spinner")
        self.movie.start()

    def stop(self):
        logger.debug("stopping loading spinner")
        self.movie.stop()