from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel, QTabWidget, QSpacerItem, QSizePolicy, QDateEdit, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal, QDate
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class SynonymSearch(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # searchbar mit autocompletion
        pass         



if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication