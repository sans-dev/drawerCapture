from PyQt6.QtCore import pyqtSignal, QObject


class ProcessEmitter(QObject):
    """
    A class that emits a signal when a process has been completed.
    """
    processed = pyqtSignal()
