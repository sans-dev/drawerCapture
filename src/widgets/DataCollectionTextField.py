import logging
import logging.config

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QSizePolicy
import sys

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
        self.initUI()

    def initUI(self):
        logger.info("initializing data collection text field UI")
        mainLayout = QVBoxLayout()
        
        for label_name in self.label_names:
            label = QLabel(label_name)
            text_input = QLineEdit()
            text_input.setPlaceholderText(label_name)
            # text_input.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout = QHBoxLayout()
            # layout.setContentsMargins(5, 15, 15, 5)
            #layout.setSpacing(5)
            layout.addWidget(label)
            layout.addWidget(text_input)
            mainLayout.addLayout(layout)
            text_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        #mainLayout.setContentsMargins(10, 10, 10, 10)
        #mainLayout.setSpacing(10)

        self.setLayout(mainLayout)

    def _loadLabelNames(self):
        labelDir = 'resources/meta_text_field_labels.txt'
        self.label_names = []
        try:
            with open(labelDir, 'r') as f:
                for line in f:
                    self.label_names.append(line.strip()) if line.strip() != '' else None
        except:
            raise Exception("Error: Could not load label names from file")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dataCollectionTextField = DataCollectionTextField()
    dataCollectionTextField.show()
    sys.exit(app.exec())
