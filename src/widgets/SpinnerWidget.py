import logging
import logging.config

from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import  QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QSize

logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class LoadingSpinner(QWidget):
    """
    A widget that displays a loading spinner animation.
    """
    def __init__(self, parent=None):
        """
        Initializes the LoadingSpinner widget.

        Args:
            parent (QWidget): The parent widget. Defaults to None.
        """
        logger.debug("initializing loading spinner")
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface of the LoadingSpinner widget.
        """
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
        """
        Starts the loading spinner animation.
        """
        logger.debug("starting loading spinner")
        self.movie.start()

    def stop(self):
        """
        Stops the loading spinner animation.
        """
        logger.debug("stopping loading spinner")
        self.movie.stop()