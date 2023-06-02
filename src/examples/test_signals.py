from PyQt6.QtCore import QObject, pyqtSignal


class MyObject(QObject):
    my_signal = pyqtSignal(int)

def my_slot(value):
    print(f"Slot called with value {value}")

obj = MyObject()
obj.my_signal.connect(my_slot)

obj.my_signal.emit(42)
