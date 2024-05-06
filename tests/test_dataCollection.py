import pytest

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QListWidgetItem
from src.widgets.DataCollection import SearchableItemListWidget, CollectionField, TaxonomyField, DateInputWidget, LabeledTextField, DataCollection
from src.utils.searching import init_taxonomy

def test_searchable_item_list_widget(qtbot):
    widget = SearchableItemListWidget("Test Label", True)
    qtbot.addWidget(widget)
    assert widget.name == "Test Label"
    assert widget.mandatory == True

def test_collection_field(qtbot):
    widget = CollectionField("Test Label", 'resources/meta_info_lists/museums.txt', True)
    qtbot.addWidget(widget)
    assert widget.name == "Test Label"
    assert widget.mandatory == True

def test_taxonomy_field(qtbot):
    taxonomy = init_taxonomy("resources/taxonomy/taxonomy_test.json")
    widget = TaxonomyField("Test Label", taxonomy, 1, True)
    qtbot.addWidget(widget)
    assert widget.name == "Test Label"
    assert widget.mandatory == True

def test_date_input_widget(qtbot):
    widget = DateInputWidget("Test Label")
    qtbot.addWidget(widget)
    assert widget.name == "Test Label"
    assert widget.get_date() == QDate.currentDate().toString("yyyy-MM-dd")

def test_labeled_text_field(qtbot):
    widget = LabeledTextField("Test Label")
    qtbot.addWidget(widget)
    assert widget.name == "Test Label"

def test_data_collection(qtbot):
    widget = DataCollection()
    qtbot.addWidget(widget)
    assert widget.taxonomy is not None
    assert len(widget.widgets) == 7

def test_get_data_exception(qtbot):
    widget = DataCollection()
    qtbot.addWidget(widget)
    data = widget.get_data()
    assert isinstance(data, dict)
    assert len(data) == 7

def test_taxonomy_integrety(qtbot):
    taxonomy = init_taxonomy("resources/taxonomy/taxonomy_test.json")
    widget = DataCollection(taxonomy)
    qtbot.addWidget(widget)
    item = QListWidgetItem()
    item.setText("Dasyleptus artinskianus")
    widget.species_widget.item_clicked(item)
    data = widget.get_data()

    expected = {
            "order": "Archaeognatha",
            "family": "Dasyleptidae",
            "genus": "Dasyleptus",
            "species": "Dasyleptus artinskianus",
        }
    assert data.get("Order") == expected.get("order")
    assert data.get("Family") == expected.get("family")
    assert data.get("Genus") == expected.get("genus")
    assert data.get("Species") == expected.get("species")