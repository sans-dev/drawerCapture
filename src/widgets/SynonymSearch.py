import json
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QPushButton, QWidget, QComboBox, QTextEdit, QCompleter, QHBoxLayout, QVBoxLayout, QLineEdit, QListWidget, QDoubleSpinBox, QListWidgetItem, QLabel, QTabWidget, QSpacerItem, QSizePolicy, QDateEdit, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression


from DataCollection import NonClickableListWidget # will be cyclic import when integrated into app
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class SynonymSearch(QWidget):
    name_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.synonymes = json.load(open('resources/taxonomy/species_synonymes.json'))
        self.name_str = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Synonym Search")
        label.setFixedHeight(20)
        result_label = QLabel("Accepted Name")
        self.accept_button = QPushButton("Accept")
        self.close_button = QPushButton("Close")
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.close_button)
        self.syn_input = QComboBox()
        self.syn_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.syn_input.setFixedHeight(20)
        syn_edit = QLineEdit()
        self.syn_input.setLineEdit(syn_edit)
        synonyme_names = list(self.synonymes.keys())
        synonyme_names.sort()
        syn_completer = QCompleter(synonyme_names)
        syn_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        syn_completer.setCompletionMode(
            QCompleter.CompletionMode.InlineCompletion)
        syn_completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        syn_completer.setModelSorting(
            QCompleter.ModelSorting.CaseInsensitivelySortedModel)

        self.syn_input.addItems(synonyme_names)
        self.syn_input.setCompleter(syn_completer)
       

        self.name = NonClickableListWidget()
        self.name.setFixedHeight(20)

        layout.addWidget(label)
        layout.addWidget(self.syn_input)
        layout.addWidget(result_label)
        layout.addWidget(self.name)
        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout) 
        self.syn_input.currentTextChanged.connect(self.on_syn_changed)
        
        self.close_button.clicked.connect(self.close)
        self.accept_button.clicked.connect(self.accept_name)

        self.on_syn_changed(self.syn_input.currentText())

    def accept_name(self):
        self.name_signal.emit(self.name_str)
    
    def on_syn_changed(self, synonyme):
        self.name.clear()
        try:
            name = self.synonymes[synonyme]
            self.name_str = name
            self.name.addItem(QListWidgetItem(str(name)))
        except KeyError:
            pass




def handle_species_signal(species):
    print(species)

def main():
    app = QApplication(sys.argv)
    window = SynonymSearch()
    window.name_signal.connect(handle_species_signal)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    main()