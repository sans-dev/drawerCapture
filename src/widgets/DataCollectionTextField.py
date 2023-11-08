import sys
import logging
import logging.config

import json

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QValidator, QIntValidator
from PyQt6.QtWidgets import QApplication, QSizePolicy

logging.config.fileConfig('configs/logging.conf',
                          disable_existing_loggers=False)

logger = logging.getLogger(__name__)


class DataCollectionTextField(QWidget):
    """
    A widget that displays an image and allows for image processing and saving.
        Properties:
            label_names: A list of label names for the text fields.
            text_inputs: A list of text input fields.
        Methods:
            _loadLabelNames: Loads the label names from a file.
    """

    def __init__(self, emitter=None):
        """
        Initializes the ImagePanel widget.
        """
        logger.debug("initializing preview panel")
        self._loadLabelNames()
        super().__init__()
        self.emitter = emitter
        self.inputFields = {}
        self.initUI()
        self.intValidator = QIntValidator()
        self.dateValidator = DateValidator()
        self.nonNumericValidator = NonNumericValidator()
        self.intValidator.changed.connect(self.onValidate)
        self.dateValidator.changed.connect(self.onValidate)
        self.nonNumericValidator.changed.connect(self.onValidate)

    def initUI(self):
        logger.info("initializing data collection text field UI")
        self.mainLayout = QVBoxLayout()
        self._buildTextFieldLayout()
        self._buildButtonLayout()
        self.setLayout(self.mainLayout)
        
    def _buildButtonLayout(self):
        """
        Builds the layout for the buttons.
        """
        logger.info("building button layout")
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save)
        self.logout_button = QPushButton("Logout")
        self.button_layout.addWidget(self.save_button)
        self.mainLayout.addLayout(self.button_layout)

    def _buildTextFieldLayout(self):
        """
        Builds the layout for the text fields.
        """
        logger.info("building text field layout")
        self.inputFields = self.label_names.copy()
        for outerLabel, innerLabels in self.label_names.items():
            label = QLabel(outerLabel)
            # change font size and weight
            label.setStyleSheet("font: 20pt")
            # incease the space above the label
            label.setContentsMargins(0, 15, 0, 5)

            self.mainLayout.addWidget(label)

            for label_name, input_type in innerLabels.items():
                label = QLabel(label_name)
                
                text_input = QLineEdit()
                if input_type == "YYYY/MM/DD":
                    text_input.setValidator(DateValidator())
                    text_input.setPlaceholderText(str(input_type))
                if input_type == 12387123:
                    text_input.setValidator(QIntValidator())
                    text_input.setPlaceholderText(str(input_type))
                if input_type == "text":
                    text_input.setValidator(NonNumericValidator())
                    text_input.setPlaceholderText(label_name)
                if input_type == "combobox":
                    text_input = MuseumWidget(emitter=self.emitter)

                self.inputFields[outerLabel][label_name] = text_input

                text_input.setAlignment(Qt.AlignmentFlag.AlignRight)
                layout = QHBoxLayout()
                layout.addWidget(label)
                layout.addWidget(text_input)
                self.mainLayout.addLayout(layout)
                text_input.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # mainLayout.setContentsMargins(10, 10, 10, 10)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red")
        self.mainLayout.addWidget(self.error_label)
        self.mainLayout.setSpacing(20)

    def save(self):
        logger.info("saving data")
        data = self.inputFields.copy()
        for outerLabel, innerLabels in self.inputFields.items():
            for label_name, input_field in innerLabels.items():
                data[outerLabel][label_name] = input_field.text()
        self.emitter.textChanged.emit(data)

    def onValidate(self, state):
        if state == QValidator.State.Invalid:
            self.error_label.setText("Invalid input")
        else:
            self.error_label.setText("")


    def _loadLabelNames(self):
        labelDir = 'resources/meta_text_field_labels.json'
        try:
            self.label_names = json.load(open(labelDir))
        except:
            raise Exception("Error: Could not load label names from file")
        
class MuseumWidget(QWidget):
    def __init__(self, emitter=None):
        super().__init__()
        self.emitter = emitter
        self.initUI()
        self.connectSignals()

    def initUI(self):
        self.comboBox = QComboBox()
        self.addMuseumButton = QPushButton("Add Museum")
        self.addMuseumButton.clicked.connect(self.addMuseum)
        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.comboBox)
        self.mainLayout.addWidget(self.addMuseumButton)
        self.setLayout(self.mainLayout)

    def addMuseum(self):
        # freeze all buttons and text fields
        pass

    def connectSignals(self):
        self.emitter.museumsChanged.connect(self.updateMuseums)

    def updateMuseums(self, museums):
        for museum in museums:
            self.comboBox.addItem(museum.name)
    
    def setAlignment(self, alignment):
        pass




class DateValidator(QValidator):
    def __init__(self):
        super().__init__()
        self.regex = QRegularExpression("^[0-9/]*$")

    def validate(self, input_text, pos):
        # Überprüfe, ob der Eingabetext dem gewünschten Format entspricht
        print(input_text)
        if self.regex.match(input_text).hasMatch():
            return QValidator.State.Acceptable, input_text, pos
        return QValidator.State.Invalid, input_text, pos
        

class NonNumericValidator(QValidator):
    def __init__(self):
        super().__init__()
        self.regex = QRegularExpression("[^0-9]*")  # Akzeptiere alle Zeichen außer Ziffern

    def validate(self, input_text, pos):
        if self.regex.match(input_text).hasMatch():
            return QValidator.State.Acceptable, input_text, pos
        return QValidator.State.Invalid, input_text, pos


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dataCollectionTextField = DataCollectionTextField()
    dataCollectionTextField.show()
    sys.exit(app.exec())
