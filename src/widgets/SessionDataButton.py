import logging
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton
from PyQt6.QtGui import QEnterEvent, QPixmap

class SessionDataButton(QWidget):
    def __init__(self, parent=None):
        logger.debug("initializing SessionDataButton")
        super(SessionDataButton, self).__init__(parent)
        # set background color to black
        self.layout = QGridLayout(self)

        self.thumbnail_image = QLabel(self)
        self.thumbnail_image.setPixmap(QPixmap("path_to_image"))  # replace with actual path
        self.layout.addWidget(self.thumbnail_image, 1, 2)

        self.session_id = QLabel("Session ID", self)
        self.layout.addWidget(self.session_id, 1, 2)

        self.museum = QLabel("Museum", self)
        self.layout.addWidget(self.museum, 2, 2)

        self.date = QLabel("Date", self)
        self.layout.addWidget(self.date, 1, 3)

        self.number_of_captured_drawers = QLabel("Number of captured drawers", self)
        self.layout.addWidget(self.number_of_captured_drawers, 2, 3)

        self.created_by = QLabel("Created by", self)
        self.layout.addWidget(self.created_by, 1, 4)
        self.setFixedSize(800, 150)

        self.setLayout(self.layout)

    def mousePressEvent(self, event):
        # Override this method to handle button click
        logger.debug("SessionDataButton clicked")
        pass

    def enterEvent(self, event: QEnterEvent) -> None:
        # set background color to light gray
        logger.debug("mouse entered SessionDataButton")
        return super().enterEvent(event)
    
    def leaveEvent(self, event: QEnterEvent) -> None:
        # set background color to black
        logger.debug("mouse left SessionDataButton")
        return super().leaveEvent(event)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    # Configure logger
    logging.basicConfig(level=logging.DEBUG)
    
    app = QApplication(sys.argv)
    session_data_button = SessionDataButton()
    session_data_button.show()
    sys.exit(app.exec())