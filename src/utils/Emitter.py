from PyQt6.QtCore import pyqtSignal, QObject


class ProcessEmitter(QObject):
    """
    A class that emits a signal when a process has been completed.
    """
    processed = pyqtSignal()

class TextEditEmitter(QObject):
    """
    A class that emits a signal when text has been entered into a text edit.
    """
    textChanged = pyqtSignal(dict)