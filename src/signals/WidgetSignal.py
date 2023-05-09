from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QObject

class WidgetSignal(QObject):
    modeChanged = pyqtSignal(QWidget)
