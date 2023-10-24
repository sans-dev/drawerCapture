import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLineEdit, QVBoxLayout, QSizePolicy

app = QApplication(sys.argv)
window = QMainWindow()
central_widget = QWidget()
window.setCentralWidget(central_widget)

line_edit = QLineEdit()
layout = QVBoxLayout(central_widget)
layout.addWidget(line_edit)
central_widget.setLayout(layout)

line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

window.show()
sys.exit(app.exec())