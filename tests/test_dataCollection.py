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

class TestTaxonomyFields:
    taxonomy = init_taxonomy("resources/taxonomy/taxonomy_test.json")

    def test_set_species_name(self, qtbot):
        widget = DataCollection(self.taxonomy)
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
        
    def test_get_data(self, qtbot):
        widget = DataCollection(self.taxonomy)
        qtbot.addWidget(widget)
        data = widget.get_data()

        assert isinstance(data, dict)
        assert len(data) == 7
        assert data.get("Order") == ""
        assert data.get("Family") == ""
        assert data.get("Genus") == ""
        assert type(data.get("Species")) == ValueError
        assert type(data.get("Museum")) == ValueError
        assert type(data.get("Collection Date")) == ValueError
        assert type(data.get("Collection Location")) == ValueError
        
    def test_set_museum(self, qtbot):
        widget = DataCollection(self.taxonomy)
        qtbot.addWidget(widget)
        item = QListWidgetItem()
        item.setText("Museum of Natural History")
        with pytest.raises(ValueError):
            widget.museum_widget.item_clicked(item)