import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel, QTabWidget, QSpacerItem, QSizePolicy, QDateEdit, QCheckBox, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QDate
import string

class TextInputWidget(QWidget):
    def __init__(self, label_text : str, mandatory=False): 
        self.mandatory = mandatory
        self.max_input_length = 30
        self.allowed_characters = string.ascii_letters + string.digits + "_"
        self.init_ui(label_text)
        self.name = label_text.strip("*")

    def init_ui(self, label_text : str):
        layout = QVBoxLayout()
        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText("Collection Name")
        self.edit.textChanged.connect(self.limit_text_length)
        self.edit.textChanged.connect(self.escape_invalid_chars)
        self.checkbox = QCheckBox("Keep Data")
        layout.addWidget(self.checkbox)
        self.error_label = QLabel()
        layout.addWidget(self.error_label)
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        self.setLayout(layout)

    def get_data(self):
        text = self.edit.text().strip()
        if self.mandatory and not text:
                 raise ValueError(f"{self.name} is a mandatory field. Please provide valid info.")
        else: 
            return text
        
    def limit_text_length(self, text):
        if len(text) > self.max_input_length:
            self.edit.setText(self.old_text)
        else:
            self.old_text = text

    def escape_invalid_chars(self, text):
        if len(text) > 0:
            if text[-1] not in self.allowed_characters:
                self.edit.setText(self.old_text)

    def show_error(self, message):
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setText(message)

    def hide_error(self):
        self.error_label.clear()

class SearchableItemListWidget(QWidget):
    def __init__(self, label_text : str, item_file : str, mandadory=False):
        super().__init__()
        self.mandatory = mandadory
        self.max_input_length = 30
        self.allowed_characters = string.ascii_letters + string.digits + "_"
        self._load_items(item_file)

        self.init_ui(label_text)
        self.name = label_text.strip("*")

    def init_ui(self, label_text : str):
        layout = QVBoxLayout()
        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self.limit_text_length)
        self.search_edit.textChanged.connect(self.escape_invalid_chars)
        self.search_edit.textChanged.connect(self.filter_items)
        layout.addWidget(self.search_edit)

        self.item_list = QListWidget()
        self.item_list.setMaximumHeight(80)
        self.item_list.itemClicked.connect(self.item_clicked)
        # populate item list
        self.item_list.addItems(self.items)
        layout.addWidget(self.item_list)
        self.checkbox = QCheckBox("Keep Data")
        layout.addWidget(self.checkbox)
        self.error_label = QLabel()
        layout.addWidget(self.error_label)
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        self.setLayout(layout)

    def limit_text_length(self, text):
        if len(text) > self.max_input_length:
            self.search_edit.setText(self.old_text)
        else:
            self.old_text = text

    def escape_invalid_chars(self, text):
        if len(text) > 0:
            if text[-1] not in self.allowed_characters:
                self.search_edit.setText(self.old_text)

    def filter_items(self, text):
        self.item_list.clear()
        if text.strip():  # Check if search text is not empty
            # Replace this with your actual list of items
            filtered_items = [item for item in self.items if text.lower() in item.lower()]
            self.item_list.addItems(filtered_items)
        else:
            self.item_list.addItems(self.items)

    def item_clicked(self, item : QListWidgetItem):
        self.search_edit.setText(item.text())

    def _load_items(self, item_file):
        with open(item_file, 'r') as f:
            self.items = f.readlines()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down:
            self.item_list.setFocus()
            if self.item_list.currentRow() < self.item_list.count() - 1:
                self.item_list.setCurrentRow(self.item_list.currentRow() + 1)
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            selected_item = self.item_list.currentItem()
            if selected_item is not None:
                self.search_edit.setText(selected_item.text())
                self.search_edit.setFocus()

    def get_data(self):
        if self.mandatory and self.item_list.count() != 1:
                 raise ValueError(f"{self.name} is a mandatory field. Please provide valid info.")
        if not self.mandatory and self.item_list.count() != 1:
            return ""
        else: 
            return self.item_list.item(0).text().strip()
        
    def show_error(self, message):
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setText(message)

    def hide_error(self):
        self.error_label.clear()
            
class DateInputWidget(QWidget):
    def __init__(self, label_text : str):
        super().__init__()
        self.name = label_text.strip("*")
        self.init_ui(label_text)

    def init_ui(self, label_text):
        layout = QVBoxLayout()

        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)  # Enable calendar popup for date selection
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit)
        self.checkbox = QCheckBox("Keep Data")
        layout.addWidget(self.checkbox)
        self.error_label = QLabel()
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def get_date(self):
        return self.date_edit.date().toString("yyyy-MM-dd")
    
    def get_data(self):
        date = self.get_date()
        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        if date == current_date:
            raise ValueError(f"{self.name} is mandatory. Please select a valid date of collection.")
        return date
    
    def show_error(self, message):
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setText(message)

    def hide_error(self):
        self.error_label.clear()
    

class LabeledTextField(QWidget):
    def __init__(self, label_text : str):
        super().__init__()
        self.name = label_text.strip("*")
        self.init_ui(label_text)

    def init_ui(self, label_text):
        layout = QVBoxLayout()

        self.label = QLabel(label_text)
        layout.addWidget(self.label)

        self.text_field = QLineEdit()
        layout.addWidget(self.text_field)
        self.checkbox = QCheckBox("Remember")
        layout.addWidget(self.checkbox)
        self.setLayout(layout)  

class DataCollection(QWidget):
    meta_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create tab widget
        tab_widget = QTabWidget()

        # Create forms for each tab
        collection_info_form = QWidget()
        collection_info_layout = QVBoxLayout(collection_info_form)
        self.museum_widget = SearchableItemListWidget("Museum*", 'resources/assets/museums.txt', mandadory=True)
        collection_info_layout.addWidget(self.museum_widget)
        self.collection_name_widget = TextInputWidget("Collection Name")
        collection_info_layout.addWidget(self.collection_name_widget)
        self.collection_date_widget = DateInputWidget("Collection Date*")
        collection_info_layout.addWidget(self.collection_date_widget)
        self.collection_location_widget = SearchableItemListWidget("Collection Location*", 'src/examples/gui_examples/test_items.txt', mandadory=True)
        collection_info_layout.addWidget(self.collection_location_widget)
        tab_widget.addTab(collection_info_form, "Collection Info")

        specimen_info_form = QWidget()
        specimen_info_layout = QVBoxLayout(specimen_info_form)
        self.order_widget = SearchableItemListWidget("Order", 'src/examples/gui_examples/test_items.txt')
        specimen_info_layout.addWidget(self.order_widget)
        self.family_widget = SearchableItemListWidget("Family", 'src/examples/gui_examples/test_items.txt')
        specimen_info_layout.addWidget(self.family_widget)
        self.genus_widget = SearchableItemListWidget("Genus", 'src/examples/gui_examples/test_items.txt')
        specimen_info_layout.addWidget(self.genus_widget)
        self.species_widget = SearchableItemListWidget("Species*", 'src/examples/gui_examples/test_items.txt', mandadory=True)
        specimen_info_layout.addWidget(self.species_widget)
        tab_widget.addTab(specimen_info_form, "Specimen Info")

        self.widgets = [
                    self.museum_widget, 
                    self.collection_name_widget, 
                    self.collection_date_widget,
                    self.collection_location_widget, 
                    self.order_widget, 
                    self.family_widget,
                    self.genus_widget, 
                    self.species_widget]

        layout.addWidget(tab_widget)

        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        self.setLayout(layout)
        self.setWindowTitle("Data Collection")

    def get_data(self):
        data = {}
        for widget in self.widgets:
            try:
                data[widget.name] = widget.get_data()
                widget.hide_error()
            except ValueError as e:
                widget.show_error(str(e))
                data[widget.name] = e
            except Exception as e:
                print(e)
                raise e
        return data
        
def handle_data(dict):
    print('Received Data', dict)

def main():
    app = QApplication(sys.argv)
    window = DataCollection()
    window.emitter.connect(handle_data)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
