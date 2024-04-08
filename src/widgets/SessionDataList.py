from PyQt6.QtWidgets import (QWidget, QSlider, QLineEdit, QLabel, QPushButton, QScrollArea,QApplication,
                             QHBoxLayout, QVBoxLayout, QMainWindow)
from PyQt6.QtCore import Qt, QSize
from PyQt6 import QtWidgets, uic
import sys


class SessionDataList(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        # make background black
        self.setStyleSheet("background-color: black")
        self.sessions = []
        
    def add_session(self, session):
        self.sessions.append(session)
        self.layout.addWidget(session, alignment=Qt.AlignmentFlag.AlignLeft)
