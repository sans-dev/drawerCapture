from PyQt6.QtCore import pyqtSignal, QObject

class ProcessEmitter(QObject):
    processed = pyqtSignal()