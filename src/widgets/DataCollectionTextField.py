from PyQt6.QtWidgets import  QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
import sys

class DataCollectionTextField(QWidget):
    def __init__(self):
        super().__init__()
        nLayouts = 5
        # Create a vertical layout to arrange the labels and text input fields
        mainLayout = QVBoxLayout()
        subLayouts = [QHBoxLayout() for i in range(nLayouts)]

        labels = []
        text_inputs = []

        # Create museum name label and text input field
        labels.append(QLabel("Museum Name"))
        text_inputs.append(QLineEdit())

        # Create collection name label and text input field
        labels.append(QLabel("Collection Name"))
        text_inputs.append(QLineEdit())

        # Create location label and text input field
        labels.append(QLabel("Location"))
        text_inputs.append(QLineEdit())

        # create collection date label and text input field
        labels.append(QLabel("Collection Date"))
        text_inputs.append(QLineEdit())

        # create species name label and text input field
        labels.append(QLabel("Species Name"))
        text_inputs.append(QLineEdit())


        # Add the labels and text input fields to the sub layouts
        for subLayout in subLayouts:
            # adjust spacing between widgets
            subLayout.setContentsMargins(15,5,15,5)
            subLayout.setSpacing(5)
            subLayout.addWidget(labels.pop(0), alignment=Qt.AlignmentFlag.AlignLeft)
            subLayout.addWidget(text_inputs.pop(0), alignment=Qt.AlignmentFlag.AlignCenter)

        # Add the sub layouts to the main layout
        for subLayout in subLayouts:
            mainLayout.addLayout(subLayout) 
        
        mainLayout.setContentsMargins(10,10,10,10)
        mainLayout.setSpacing(10)

        self.setLayout(mainLayout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dataCollectionTextField = DataCollectionTextField()
    dataCollectionTextField.show()
    sys.exit(app.exec())