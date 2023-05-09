from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

class WidgetSignal(QWidget):
    modeChanged = pyqtSignal(QWidget)