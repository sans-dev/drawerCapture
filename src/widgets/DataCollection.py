from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QPushButton, QWidget, QComboBox, QTextEdit, QCompleter, QHBoxLayout, QVBoxLayout, QLineEdit, QListWidget, QDoubleSpinBox, QListWidgetItem, QLabel, QTabWidget, QSpacerItem, QSizePolicy, QDateEdit, QCheckBox
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

from src.widgets.MapWidget import MapWindow
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class SearchableItemListWidget(QWidget):
    def __init__(self, label_text, mandatory):
        super().__init__()
        logger.info(f"Initializing {self.__class__.__name__}")
        self.name = label_text.strip("*")
        self.mandatory = mandatory
        self.init_ui()


    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel(self.name)
        layout.addWidget(self.label)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(self.name)
        self.search_edit.setMaxLength(30)
        layout.addWidget(self.search_edit)

        self.item_list = QListWidget()
        self.item_list.setMaximumHeight(80)
        layout.addWidget(self.item_list)
        self.checkbox = QCheckBox("Keep Data")
        layout.addWidget(self.checkbox)
        self.error_label = QLabel()
        layout.addWidget(self.error_label)
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        logger.info("Key pressed")
        if event.key() == Qt.Key.Key_Down:
            self.item_list.setFocus()
            if self.item_list.currentRow() < self.item_list.count() - 1:
                self.item_list.setCurrentRow(self.item_list.currentRow() + 1)
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            selected_item = self.item_list.currentItem()
            if selected_item is not None:
                self.search_edit.setText(selected_item.text())
                self.search_edit.setFocus()
        
    def show_error(self, message):
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setText(message)

    def hide_error(self):
        self.error_label.clear()

class NonClickableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        # Ignore the mouse press event
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        # Ignore the mouse release event
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        # Ignore the mouse double click event
        event.ignore()

    def mouseMoveEvent(self, event):
        # Ignore the mouse move event
        event.ignore()

class SessionInfoField(QWidget):
    def __init__(self, label_text=None, label_value=None):
        super().__init__()
        self.label_text = label_text
        self.value = None
        hlayout = QVBoxLayout()
        self.label = QLabel(label_text)
        self.value = NonClickableListWidget()
        self.value.addItem(QListWidgetItem(str(label_value)))
        self.value.setFixedHeight(20)
        self.label.setFixedHeight(20)
        self.value.setStyleSheet("color: gray;")
        hlayout.addWidget(self.label)
        hlayout.addWidget(self.value)
        hlayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(hlayout)

    def onClicked(self):
        pass

class SessionInfoWidget(QWidget):
    def init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def set_session_data(self, data):
        self.session_data = data
        _layout = QVBoxLayout()
        _layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for label, value in data.items():
            field = SessionInfoField(label, value)
            field.setFixedHeight(60)
            _layout.addWidget(field)
        self.setLayout(_layout)

    def get_data(self):
        return self.session_data

class GeoDataField(QWidget):
    def __init__(self, label_text, items_file, mandatory):
        super().__init__()
        self.label_text = label_text
        self.items_file = items_file
        self.mandatory = mandatory
        self.init_ui()

        self.map_button.clicked.connect(self.map_button_clicked)

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel(self.label_text)
        self.region_field = RegionField()
        self.geo_coords = GeoCoordinatesField()
        self.map_button = QPushButton("Open Map")
        self.description_field = GeoDescriptionField()
        self.map = MapWindow(search_bar=RegionField)
        self.map.hide()
        layout.addWidget(self.label)
        layout.addWidget(self.region_field)
        layout.addWidget(self.geo_coords)
        layout.addWidget(self.map_button)
        layout.addWidget(self.description_field)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

    def map_button_clicked(self):
        self.map.show()

class GeoDescriptionField(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Description")
        self.label.setFixedHeight(20)
        self.description_field = QTextEdit()
        self.description_field.setFixedHeight(200)
        layout.addWidget(self.label)
        layout.addWidget(self.description_field)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

class RegionField(QWidget):
    region_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Region")
        label.setFixedHeight(20)
        self.region_input = QComboBox()
        self.region_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.region_input.setFixedHeight(20)
        region_edit = QLineEdit()
        self.region_input.setLineEdit(region_edit)
        # self.region_input.setEditable(True)
        self.regions = ["Africa", "Asia", "Europe", "North America", "South America"]
        region_completer = QCompleter(self.regions)
        region_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        region_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        region_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        region_completer.setModelSorting(QCompleter.ModelSorting.CaseInsensitivelySortedModel)

        self.region_input.addItems(self.regions)
        self.region_input.setCompleter(region_completer)
        self.region_input.currentIndexChanged.connect(self.on_region_changed)
        layout.addWidget(label)
        layout.addWidget(self.region_input)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)
        
    def on_region_changed(self):
        region = self.region_input.currentText()
        self.region_changed.emit(region)

class GeoCoordinatesField(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        geo_layout = QVBoxLayout()
        longitude_layout = QHBoxLayout()
        lattitude_layout = QHBoxLayout()
        longitude_label = QLabel("Longitude")
        longitude_label.setFixedHeight(20)
        longitude_input = QDoubleSpinBox()
        longitude_input.setFixedHeight(20)
        longitude_input.decimals = 5
        longitude_input.setRange(-180, 180)
        longitude_layout.addWidget(longitude_label)
        longitude_layout.addWidget(longitude_input)
        lattitude_label = QLabel("Lattitude")
        lattitude_label.setFixedHeight(20)
        lattitude_input = QDoubleSpinBox()
        lattitude_input.setFixedHeight(20)
        lattitude_input.decimals = 5
        lattitude_input.setRange(-90, 90)
        lattitude_layout.addWidget(lattitude_label)
        lattitude_layout.addWidget(lattitude_input)
        geo_layout.addLayout(longitude_layout)
        geo_layout.addLayout(lattitude_layout)
        self.setLayout(geo_layout)
        
    def filter_items(self, text):
        logger.info("Filtering items for preview list")
        self.item_list.clear()
        if text.strip():  # Check if search text is not empty
            # Replace this with your actual list of items
            filtered_items = [item for item in self.items if text.lower() in item.lower()]
            self.item_list.addItems(filtered_items)
        else:
            self.item_list.addItems(self.items)

    def get_data(self):
        logger.info("Preparing data for saving")
        if self.mandatory and self.item_list.count() != 1:
                 raise ValueError(f"{self.name} is a mandatory field. Please provide valid info.")
        if not self.mandatory and self.item_list.count() != 1:
            return ""
        else: 
            return self.item_list.item(0).text().strip()
        
    def item_clicked(self, item: QListWidgetItem):
        text = item.text()
        if not self.item_list.findItems(text, Qt.MatchFlag.MatchExactly):
            raise ValueError(f"Item '{text}' not found in the list.")
        else:
            self.item_list.clearSelection()
            self.item_list.clearFocus()
            self.item_list.clear()
            self.item_list.addItems([text])
            self.search_edit.setText(text)

    def _load_items(self, item_file):
        with open(item_file, 'r') as f:
            self.items = f.readlines()

class TaxonomyField(SearchableItemListWidget):
    parents_signal = pyqtSignal(list)
    clear_child_signal = pyqtSignal()
    def __init__(self, label_text, taxonomy, level, mandatory):
        super().__init__(label_text, mandatory)
        super().init_ui()
        self.taxonomy = taxonomy
        self.item_list.itemClicked.connect(self.item_clicked)
        if isinstance(level, int):
            self.level = level
        else:
            raise ValueError("level must be an integer")
        self.search_edit.textEdited.connect(self.filter_items)

    def filter_items(self, text):
        logger.info("Filter list entry suggestions")
        self.item_list.clear()
        if text.strip():  # Check if search text is not empty
            # Replace this with your actual list of items
            filtered_items = self.taxonomy.prefix_search(self.level, text)
            self.item_list.addItems(filtered_items)
        else:
            self.item_list.clear()

    def get_data(self):
        if self.mandatory and self.item_list.count() != 1:
                 raise ValueError(f"{self.name} is a mandatory field. Please provide valid info.")
        if not self.mandatory and self.item_list.count() != 1:
            return ""
        else: 
            return self.item_list.item(0).text().strip()
        
    def item_clicked(self, item: QListWidgetItem):
        logger.info(f"Searching for parents of {item.text()}: level = {self.name}")
        text = item.text()
        parents = self.taxonomy.get_parents(text)
        self.item_list.clearSelection()
        self.item_list.clearFocus()
        self.item_list.clear()
        self.item_list.addItems([text])
        self.search_edit.setText(text)
        self.parents_signal.emit(parents)
        self.clear_child_signal.emit()

    def set_text(self, parents):
        logger.info("Setting parent text")
        parent = parents.pop()
        if parent == 'root':
            return
        self.item_list.clear()
        self.item_list.addItems([parent])
        self.search_edit.setText(parent)
        self.parents_signal.emit(parents)

    def clear_text(self):
        logger.info(f"Clearing text in {self.name}")
        self.search_edit.setText(self.name)
        self.item_list.clear()
        self.clear_child_signal.emit()

        
class DateInputWidget(QWidget):
    def __init__(self, label_text : str):
        super().__init__()
        logger.info(f"Initializing {self.__class__.__name__}")
        self.name = label_text.strip("*")
        self.init_ui(label_text)

    def init_ui(self, label_text):
        layout = QVBoxLayout()

        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat('dd.MM.yyyy')
        self.date_edit.setMaximumDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)  # Enable calendar popup for date selection
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.date_edit)
        self.checkbox = QCheckBox("Keep Data")
        layout.addWidget(self.checkbox)
        self.error_label = QLabel()
        layout.addWidget(self.error_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

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

    def __init__(self, taxonomy):
        super().__init__()
        self.taxonomy = taxonomy
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create tab widget 
        tab_widget = QTabWidget()

        # Create forms for each tab
        session_info_form = QWidget()
        session_info_layout = QVBoxLayout(session_info_form)
        self.session_widget = SessionInfoWidget()
        session_info_layout.addWidget(self.session_widget)
        tab_widget.addTab(session_info_form, "Session Info")  

        collection_info_form = QWidget()
        collection_info_layout = QVBoxLayout(collection_info_form)
        self.collection_date_widget = DateInputWidget("Collection Date*")
        collection_info_layout.addWidget(self.collection_date_widget)
        self.collection_location_widget = GeoDataField("Geo Information*", 'resources/meta_info_lists/regions.txt', mandatory=True)
        collection_info_layout.addWidget(self.collection_location_widget)
        collection_info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        tab_widget.addTab(collection_info_form, "Collection Info")

        specimen_info_form = QWidget()
        specimen_info_layout = QVBoxLayout(specimen_info_form)
        self.order_widget = TaxonomyField("Order", self.taxonomy, level=int(1), mandatory=False)
        specimen_info_layout.addWidget(self.order_widget)
        self.family_widget = TaxonomyField("Family", self.taxonomy, level=int(2), mandatory=False)
        specimen_info_layout.addWidget(self.family_widget)
        self.genus_widget = TaxonomyField("Genus", self.taxonomy, level=int(3), mandatory=False)
        specimen_info_layout.addWidget(self.genus_widget)
        self.species_widget = TaxonomyField("Species*", self.taxonomy, level=int(4), mandatory=True)
        specimen_info_layout.addWidget(self.species_widget)
        tab_widget.addTab(specimen_info_form, "Specimen Info")

        self.widgets = [
                    self.session_widget, 
                    self.collection_date_widget,
                    self.collection_location_widget, 
                    self.order_widget, 
                    self.family_widget,
                    self.genus_widget, 
                    self.species_widget]

        layout.addWidget(tab_widget)

        self.species_widget.parents_signal.connect(self.genus_widget.set_text)
        self.genus_widget.parents_signal.connect(self.family_widget.set_text)
        self.family_widget.parents_signal.connect(self.order_widget.set_text)
        
        self.order_widget.clear_child_signal.connect(self.family_widget.clear_text)
        self.family_widget.clear_child_signal.connect(self.genus_widget.clear_text)
        self.genus_widget.clear_child_signal.connect(self.species_widget.clear_text)
        # spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        # layout.addItem(spacer)
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
    
    def set_session_data(self, data):
        self.session_widget.set_session_data(data)
        
def handle_data(dict):
    print('Received Data', dict)

def main():
    app = QApplication(sys.argv)
    taxonomy = init_taxonomy("tests/data/taxonomy_test.json")
    window = DataCollection(taxonomy)
    window.meta_signal.connect(handle_data)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from src.utils.searching import init_taxonomy
    main()
