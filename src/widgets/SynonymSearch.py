import json
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QPushButton, QWidget, QComboBox, QTextEdit, QCompleter, QHBoxLayout, QVBoxLayout, QLineEdit, QListWidget, QDoubleSpinBox, QListWidgetItem, QLabel, QTabWidget, QSpacerItem, QSizePolicy, QDateEdit, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class SynonymSearch(QWidget):
    def __init__(self):
        super().__init__()
        self.synonymes = json.load(open('resources/taxonomy/species_synonymes.json'))
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Synonym Search")
        label.setFixedHeight(20)
        self.region_input = QComboBox()
        self.region_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.region_input.setFixedHeight(20)
        region_edit = QLineEdit()
        self.region_input.setLineEdit(region_edit)
        # self.region_input.setEditable(True)
        region_completer = QCompleter(self.regions['name'].to_list())
        region_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        region_completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion)
        region_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        region_completer.setModelSorting(
            QCompleter.ModelSorting.CaseInsensitivelySortedModel)

        self.region_input.addItems(self.regions['name'])
        self.region_input.setCompleter(region_completer)
        self.region_input.currentIndexChanged.connect(self.on_region_changed)
        layout.addWidget(label)
        layout.addWidget(self.region_input)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication