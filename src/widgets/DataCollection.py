import json
import pandas as pd
import numpy as np
from argparse import ArgumentParser
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QListWidget,
                             QListWidgetItem, QLabel, QTabWidget, QSpacerItem,
                             QSizePolicy, QDateEdit, QCheckBox, QPushButton, QComboBox,
                             QCompleter, QHBoxLayout, QTextEdit, QDoubleSpinBox, QStackedWidget)

from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QPalette,QColor
from src.configs.DataCollection import *

from src.widgets.MapWidget import MapWindow
import logging
import logging.config
logging.config.fileConfig('configs/logging/logging.conf',
                          disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class ListWidget(QWidget):
    def __init__(self, info_type=None):
        self.info_type = info_type
        super().__init__()
        self.error_label = QLabel()

    def show_error(self, message):
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setText(message)

    def hide_error(self):
        self.error_label.clear()


class SearchableItemListWidget(ListWidget):
    def __init__(self, mandatory, info_type):
        super().__init__()
        logger.info(f"Initializing {self.__class__.__name__}")
        self.mandatory = mandatory
        self.info_type = info_type

        self.init_ui()

    def init_ui(self):
        self.place_holder = "search"
        layout = QVBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(self.place_holder)
        self.search_edit.setMaxLength(30)
        self.item_list = QListWidget()
        self.item_list.setMaximumHeight(60)

        layout.addWidget(self.search_edit)
        layout.addWidget(self.item_list)
        layout.addWidget(self.error_label)

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

    def set_value(self, new_value):
        self.value.clear()
        self.value.addItem(QListWidgetItem(str(new_value)))

    def get_label_text(self):
        return self.label.text()

class SessionInfoWidget(ListWidget):
    def __init__(self):
        super().__init__("Session Info")
        self.fields = {}

    def set_session_data(self, data): # error when session data is updated, because layout already exists
        self.session_data = data
        if not self.fields: # no layout was set
            _layout = QVBoxLayout()
            _layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            for label, value in data.items():
                l = label.capitalize().replace("_", " ")
                field = SessionInfoField(l, value)
                field.setFixedHeight(60)
                _layout.addWidget(field)
                self.fields[l] = field
            self.setLayout(_layout)
        else:
            for label, value in data.items():
                l = label.capitalize().replace("_", " ")
                self.fields[l].set_value(value)

    def get_data(self):
        return self.session_data


class GeoDataField(ListWidget):
    def __init__(self, label_text, region_data, mandatory=True):
        super().__init__('Collection Info')
        self.mandatory = mandatory
        if self.mandatory:
            self.label_text = f"{label_text}*"
        self.region_data = region_data
        
        self.init_ui()
        self.name = 'Geo Info'

        self.map_button.clicked.connect(self.map_button_clicked)
        #self.map.new_coords_signal.connect(self.geo_coords.set_coords)
        #self.map.new_coords_signal.connect(
        #    self.region_field.get_country_by_coords)

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel(self.label_text)
        self.region_field = RegionField(self.region_data)
        self.geo_coords = GeoCoordinatesField()
        self.map_button = QPushButton("Open Map")
        self.map_button.setEnabled(False)
        self.description_field = GeoDescriptionField()
        # self.map = MapWindow(search_bar=RegionField, region_data=self.region_data)
        # self.map.hide()

        layout.addWidget(self.label)
        layout.addWidget(self.error_label)
        layout.addWidget(self.region_field)
        layout.addWidget(self.geo_coords)
        layout.addWidget(self.map_button)
        layout.addWidget(self.description_field)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        #self.region_field.region_changed.connect(
        #    self.map.search_bar.set_region)
        #self.map.search_bar.region_changed.connect(
        #    self.region_field.set_region)

    def map_button_clicked(self):
        self.map.show()

    def get_data(self):
        data = {}
        data = {
            'Country': self.region_field.get_data(),
            'Coordinates': self.geo_coords.get_data(),
            'Description': self.description_field.get_data()
        }
        return data


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

    def get_data(self):
        return self.description_field.toPlainText()


class RegionField(QWidget):
    region_changed = pyqtSignal(str)

    def __init__(self, region_data):
        super().__init__()
        # TODO: irgendwo anders angeben...
        self.regions = pd.read_csv(
            region_data, delimiter=',')
        self.init_ui()
        self.set_region("Germany")

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

    def on_region_changed(self):
        region = self.region_input.currentText()
        self.region_changed.emit(region)

    def set_region(self, region):
        self.region_input.currentIndexChanged.disconnect(
            self.on_region_changed)
        self.region_input.setCurrentText(region)
        self.region_input.currentIndexChanged.connect(self.on_region_changed)

    def get_data(self):
        return self.region_input.currentText()

    def get_country_by_coords(self, coords):
        min_long = self.regions['bbox'].apply(
            lambda x: float(x.split()[0])).values
        max_long = self.regions['bbox'].apply(
            lambda x: float(x.split()[2])).values
        min_lat = self.regions['bbox'].apply(
            lambda x: float(x.split()[1])).values
        max_lat = self.regions['bbox'].apply(
            lambda x: float(x.split()[3])).values

        closest_idx = ((min_long <= coords[0]) & (max_long >= coords[0]) & (
            min_lat <= coords[1]) & (max_lat >= coords[1])).argmax()
        region = self.regions.loc[closest_idx, 'name']
        self.set_region(region)
        return region


class GeoCoordinatesField(QWidget):
    def __init__(self, mandatory=True):
        super().__init__()
        self.mandatory = mandatory
        self.type = None
        self.init_ui()

    def init_ui(self):
        geo_layout = QVBoxLayout()
        longitude_layout = QHBoxLayout()
        lattitude_layout = QHBoxLayout()
        longitude_label = QLabel("Longitude (-180, 180)")
        radius_layout = QHBoxLayout()
        longitude_label.setFixedHeight(20)
        self.longitude_input = QDoubleSpinBox()
        self.longitude_input.setFixedHeight(20)
        self.longitude_input.setDecimals(5)
        self.longitude_input.setRange(-180, 180)
        self.longitude_input.clear()
        longitude_layout.addWidget(longitude_label)
        longitude_layout.addWidget(self.longitude_input)
        lattitude_label = QLabel("Lattitude (-90, 90)")
        lattitude_label.setFixedHeight(20)
        self.lattitude_input = QDoubleSpinBox()
        self.lattitude_input.setFixedHeight(20)
        self.lattitude_input.setDecimals(5)
        self.lattitude_input.setRange(-90, 90)
        self.lattitude_input.clear()
        lattitude_layout.addWidget(lattitude_label)
        lattitude_layout.addWidget(self.lattitude_input)
        self.radius_label = QLabel('Collection Radius (km)')
        self.radius_input = QDoubleSpinBox()
        self.radius_input.setFixedHeight(20)
        self.radius_input.setDecimals(1)
        self.radius_input.setRange(0, 50)
        radius_layout.addWidget(self.radius_label)
        radius_layout.addWidget(self.radius_input)
        geo_layout.addLayout(longitude_layout)
        geo_layout.addLayout(lattitude_layout)
        geo_layout.addLayout(radius_layout)
        self.setLayout(geo_layout)

    def get_data(self):
        if self.mandatory:
            if self.longitude_input.text() == '' or self.lattitude_input.text() == '':
                self.longitude_input.clear()
                self.lattitude_input.clear()
                raise ValueError("Geocoordinates are mandatory.")
        longitude = float(self.longitude_input.text().replace(",","."))
        lattitude = float(self.lattitude_input.text().replace(",", "."))
        radius = float(self.radius_input.text().replace(",", "."))
        bbox = self.calculate_bbox(longitude,lattitude, radius)
        for key, data in bbox.items():
            bbox[key] = [f'{value:.5f}' for value in data]
        data = {
            'longitude': longitude,
            'lattitude': lattitude,
            'radius': radius,
            'bbox': bbox, 
            'type': self.type
        }

        return data

    def set_coords(self, coords):
        self.longitude_input.setValue(coords[0])
        self.lattitude_input.setValue(coords[1])

    def km_to_deg_lat(self, km):
        return km / 111.32

    def km_to_deg_lon(self, km, lat):
        return km / (111.32 * np.cos(np.radians(lat)))

    def normalize_longitude(self, lon):
        return ((lon + 180) % 360) - 180

    def normalize_latitude(self, lat):
        return np.clip(lat, -90, 90)

    def calculate_bbox(self, lon, lat, radius_km):
        lat_diff = self.km_to_deg_lat(radius_km)
        lon_diff = self.km_to_deg_lon(radius_km, lat)
        
        upper_left_lat = self.normalize_latitude(lat + lat_diff)
        upper_left_lon = self.normalize_longitude(lon - lon_diff)
        lower_right_lat = self.normalize_latitude(lat - lat_diff)
        lower_right_lon = self.normalize_longitude(lon + lon_diff)
        
        bbox = {
            "upper_left": [upper_left_lat, upper_left_lon],
            "lower_right": [lower_right_lat, lower_right_lon]
        }
        
        return bbox
class SynonymSearch(QWidget):
    name_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.name_str = None
        self.tool_tipp_text = "\
            This search tool allows to search accepted taxonomy names based on synonymes.\n \
            \n \
            The synonym format differs in case of the historic taxonomic classification:\n \
                ------------------------------------------------------------------------\n \
                ? <species suffix> :                    | genus not described, species described\n \
                ? <nr>-<species suffix> :               | genus not described, species ambigious\n \
                <genus prefix> 12-<species suffix> :    | genus described, species ambigious\n \
                <genus prefix> <species suffix> :       | genus and species described"
        self.tool_tipp_text = """
                This search tool allows to search accepted taxonomy names based on synonymes.
                The synonym format differs in case of the historic taxonomic classification:
        
                        - ? <species suffix>: genus not described, species described
                        - ? <nr>-<species suffix>: genus not described, species ambiguous
                        - <genus prefix> 12-<species suffix>: genus described, species ambiguous
                        - <genus prefix> <species suffix>: genus and species described
                    """
        
        self.setToolTip(self.tool_tipp_text)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        head_layout = QHBoxLayout()
        label = QLabel("Synonym Search")
        label.setFixedHeight(20)
        result_label = QLabel("Accepted Name")
        self.accept_button = QPushButton("Accept")
        self.close_button = QPushButton("Close")
        self.tool_tip_button = QPushButton("?")
        self.tool_tip_button.setFixedHeight(20)
        self.tool_tip_button.setFixedWidth(20)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.close_button)
        self.syn_input = QComboBox()
        self.syn_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.syn_input.setFixedHeight(20)
        syn_edit = QLineEdit()
        self.syn_input.setLineEdit(syn_edit)
        self.tool_label = QLabel(self.tool_tipp_text)
        self.name = NonClickableListWidget()
        self.name.setFixedHeight(20)
        head_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        head_layout.addWidget(label)
        head_layout.addWidget(self.tool_tip_button)
        layout.addLayout(head_layout)
        layout.addWidget(self.syn_input)
        layout.addWidget(result_label)
        layout.addWidget(self.name)
        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)
        self.syn_input.currentTextChanged.connect(self.on_syn_changed)

        self.close_button.clicked.connect(self.close)
        self.accept_button.clicked.connect(self.accept_name)

        self.tool_tip_button.clicked.connect(self.on_tool_button_clicked)

    def on_tool_button_clicked(self):
        self.tool_label.show()

    def load_synonym_data(self, synonym_dir):
        if not synonym_dir:
            self.synonymes = {}
            return
        self.synonymes = json.load(
            open(synonym_dir))

    def accept_name(self):
        self.name_signal.emit(self.name_str)

    def on_syn_changed(self, synonyme):
        self.name.clear()
        try:
            name = self.synonymes[synonyme]
            self.name_str = name
            self.name.addItem(QListWidgetItem(str(name)))
        except KeyError:
            self.name_str = ""

    def populate_ui(self):
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
        self.syn_input.clear()
        self.syn_input.setCompleter(syn_completer)


class TaxonomyField(ListWidget):
    parents_signal = pyqtSignal(list)
    clear_child_signal = pyqtSignal()

    def __init__(self, label_text, taxonomy, level, mandatory):
        super().__init__()
        self.mandatory = mandatory
        if self.mandatory:
            self.label_text = f"{label_text}*"
        else:
            self.label_text = label_text
        self.taxonomy = taxonomy
        self.info_type = 'Specimen Info'
        self.level = level
        self.name = label_text
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.search_widget = QStackedWidget()
        self.direct_search = SearchableItemListWidget(
            self.mandatory, "Specimen Info")
        spacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.label = QLabel(self.label_text)
        self.syn_search = SynonymSearch()
        syn_file = SYNONYMES.get(self.name, None)
        self.syn_search.load_synonym_data(syn_file)
        self.syn_search.populate_ui()
        
        self.syn_search_button = QPushButton("Synonyme Search")
        if self.name != 'Species':
            self.syn_search_button.setEnabled(False)
            self.syn_search_button.hide()
        self.search_widget.addWidget(self.direct_search)
        self.search_widget.addWidget(self.syn_search)
        layout.addWidget(self.label)
        layout.addWidget(self.error_label)
        layout.addWidget(self.syn_search_button)
        layout.addWidget(self.search_widget)
        layout.addItem(spacer)
        self.setLayout(layout)

        self.direct_search.item_list.itemClicked.connect(self.item_clicked)
        if isinstance(self.level, int):
            self.level = self.level
        else:
            raise ValueError("level must be an integer")
        self.direct_search.search_edit.textEdited.connect(self.filter_items)
        
        self.syn_search_button.clicked.connect(self.on_syn_botton_clicked)
        self.syn_search.name_signal.connect(self.on_syn_accepted)
        self.syn_search.close_button.clicked.connect(self.on_syn_search_close)
        self.syn_search.accept_button.clicked.connect(self.on_syn_search_close)


    def on_syn_botton_clicked(self):
        if self.search_widget.currentIndex != -1 and self.search_widget.currentIndex != 1:
            self.search_widget.setCurrentIndex(1)

    def on_syn_search_close(self):
        if self.search_widget.currentIndex != -1 and self.search_widget.currentIndex != 0:
            self.search_widget.setCurrentIndex(0)
     
    def on_syn_accepted(self, text):
        if text:
            if text == self.direct_search.search_edit.text():
                return
            self.filter_items(text)
            self.direct_search.search_edit.setText(text)
            parents = self.taxonomy.get_parents(text)
            if parents:
                self.parents_signal.emit(self.taxonomy.get_parents(text))
        else:
            return

    def filter_items(self, text):
        logger.info("Filter list entry suggestions")
        self.direct_search.item_list.clear()
        if text.strip():  # Check if search text is not empty
            # Replace this with your actual list of items
            filtered_items = self.taxonomy.prefix_search(self.level, text)
            self.direct_search.item_list.addItems(filtered_items)
        else:
            self.direct_search.item_list.clear()

    def get_data(self):
        if self.mandatory and self.direct_search.item_list.count() != 1:
            raise ValueError(
                f"{self.name} is a mandatory field. Please provide valid info.")
        if not self.mandatory and self.direct_search.item_list.count() != 1:
            return self.name
        else:
            return self.direct_search.item_list.item(0).text().strip()

    def item_clicked(self, item: QListWidgetItem):
        logger.info(
            f"Searching for parents of {item.text()}: level = {self.name}")
        text = item.text()
        parents = self.taxonomy.get_parents(text)
        self.direct_search.item_list.clearSelection()
        self.direct_search.item_list.clearFocus()
        self.direct_search.item_list.clear()
        self.direct_search.item_list.addItems([text])
        self.direct_search.search_edit.setText(text)
        self.parents_signal.emit(parents)
        self.clear_child_signal.emit()

    def set_text(self, parents):
        logger.info("Setting parent text")
        parent = parents.pop()
        if parent == 'root':
            return
        self.direct_search.item_list.clear()
        self.direct_search.item_list.addItems([parent])
        self.direct_search.search_edit.setText(parent)
        self.parents_signal.emit(parents)

    def clear_text(self):
        logger.info(f"Clearing text in {self.name}")
        self.direct_search.item_list.clear()
        self.direct_search.search_edit.clear()
        self.direct_search.search_edit.setPlaceholderText(self.name)
        self.clear_child_signal.emit()


class DateInputWidget(ListWidget):
    def __init__(self, label_text: str, mandatory=True):
        super().__init__("Collection Info")
        logger.info(f"Initializing {self.__class__.__name__}")
        self.mandatory = mandatory
        if self.mandatory:
            self.name = f"{label_text}"
        self.init_ui(label_text)

    def init_ui(self, label_text):
        layout = QVBoxLayout()
        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        self.date_edit = QDateEdit()
        palette = self.date_edit.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("lightgray"))
        self.date_edit.setPalette(palette)
        self.date_edit.setDisplayFormat('dd.MM.yyyy')
        self.date_edit.setMaximumDate(QDate.currentDate())
        # Enable calendar popup for date selection
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addWidget(self.error_label)
        layout.addWidget(self.date_edit)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setLayout(layout)

    def get_date(self):
        return self.date_edit.date().toString("yyyy-MM-dd")

    def get_data(self):
        date = self.get_date()
        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        if date == current_date:
            raise ValueError(
                f"{self.name} is mandatory.")
        return date


class LabeledTextField(QWidget):
    def __init__(self, label_text: str):
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

    def __init__(self, taxonomy, geo_data_dir):
        super().__init__()
        self.taxonomy = taxonomy
        self.geo_data_dir = geo_data_dir
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create forms for each tab
        session_info_form = QWidget()
        session_info_layout = QVBoxLayout(session_info_form)
        self.session_widget = SessionInfoWidget()
        session_info_layout.addWidget(self.session_widget)
        self.tab_widget.addTab(session_info_form, "Session Info")

        collection_info_form = QWidget()
        collection_info_layout = QVBoxLayout(collection_info_form)
        self.collection_date_widget = DateInputWidget("Collection Date", mandatory=True)
        collection_info_layout.addWidget(self.collection_date_widget)
        self.collection_location_widget = GeoDataField(
            "Geo Information", self.geo_data_dir, mandatory=True)
        collection_info_layout.addWidget(self.collection_location_widget)
        collection_info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tab_widget.addTab(collection_info_form, "Collection Info")

        specimen_info_form = QWidget()
        specimen_info_layout = QVBoxLayout(specimen_info_form)
        self.order_widget = TaxonomyField(
            "Order", self.taxonomy, level=int(1), mandatory=True)
        specimen_info_layout.addWidget(self.order_widget)
        self.family_widget = TaxonomyField(
            "Family", self.taxonomy, level=int(2), mandatory=True)
        specimen_info_layout.addWidget(self.family_widget)
        self.genus_widget = TaxonomyField(
            "Genus", self.taxonomy, level=int(3), mandatory=True)
        specimen_info_layout.addWidget(self.genus_widget)
        self.species_widget = TaxonomyField(
            "Species", self.taxonomy, level=int(4), mandatory=False)
        specimen_info_layout.addWidget(self.species_widget)
        self.tab_widget.addTab(specimen_info_form, "Specimen Info",)

        self.widgets = [
            self.session_widget,
            self.collection_date_widget,
            self.collection_location_widget,
            self.order_widget,
            self.family_widget,
            self.genus_widget,
            self.species_widget]

        layout.addWidget(self.tab_widget)

        self.species_widget.parents_signal.connect(self.genus_widget.set_text)
        self.genus_widget.parents_signal.connect(self.family_widget.set_text)
        self.family_widget.parents_signal.connect(self.order_widget.set_text)

        self.order_widget.clear_child_signal.connect(
            self.family_widget.clear_text)
        self.family_widget.clear_child_signal.connect(
            self.genus_widget.clear_text)
        self.genus_widget.clear_child_signal.connect(
            self.species_widget.clear_text)
        self.setLayout(layout)
        self.setWindowTitle("Data Collection")

    def get_data(self):
        data = {}
        species_info = {}
        collection_info = {}
        for widget in self.widgets:
            try:
                if widget.info_type == "Session Info":
                    data["Session Info"] = widget.get_data()
                if widget.info_type == "Specimen Info":
                    species_info[widget.name.lower()] = widget.get_data()
                elif widget.info_type == "Collection Info":
                    collection_info[widget.name.lower()] = widget.get_data()
                widget.hide_error()
            except ValueError as e:
                tab_idx = self.find_widget_tab(widget)
                widget.show_error(str(e))
                data[widget.name] = e
            except Exception as e:
                print(e)
                raise e
        data['Species Info'] = species_info
        data['Collection Info'] = collection_info
        return data

    def set_session_data(self, data):
        self.session_widget.set_session_data(data)

    def find_widget_tab(self, target_widget):
        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            if self.widget_in_tab(tab, target_widget):
                return index
        return None

    def widget_in_tab(self, tab, target_widget):
        layout = tab.layout()
        for i in range(layout.count()):
            if layout.itemAt(i).widget() == target_widget:
                return True
        return False

def handle_data(dict):
    print('Received Data', dict)


def main():
    parser = ArgumentParser()
    parser.add_argument('--taxonomy', type=str)
    parser.add_argument('--geo-data', choices=['level-0', 'level-1'])
    args = parser.parse_args()
    app = QApplication(sys.argv)
    taxonomy = init_taxonomy(TAXONOMY[args.taxonomy])
    geo_data_dir = GEO[args.geo_data]
    window = DataCollection(taxonomy, geo_data_dir)
    window.meta_signal.connect(handle_data)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from src.utils.searching import init_taxonomy
    main()
