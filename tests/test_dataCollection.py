import json

import pytest

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QListWidgetItem
from src.widgets.DataCollection import SearchableItemListWidget, CollectionField, TaxonomyField, DateInputWidget, LabeledTextField, DataCollection
from src.utils.searching import init_taxonomy


taxonomy_data = [
    {
        "key": 1234567,
        "order": "Ephemeroptera",
        "family": "Baetidae",
        "genus": "Baetis",
        "species": "Baetis rhodani",
        "parent": "Baetis",
        "scientificName": "Baetis rhodani (Pictet, 1843)",
        "canonicalName": "Baetis rhodani",
        "class": "Insecta"
    },
    {
        "key": 7654321,
        "order": "Ephemeroptera",
        "family": "Heptageniidae",
        "genus": "Epeorus",
        "species": "Epeorus vitreus",
        "parent": "Epeorus",
        "scientificName": "Epeorus vitreus (Walker, 1853)",
        "canonicalName": "Epeorus vitreus",
        "class": "Insecta"
    },
    {
        "key": 2468013,
        "order": "Plecoptera",
        "family": "Nemouridae",
        "genus": "Amphinemura",
        "species": "Amphinemura sulcicollis",
        "parent": "Amphinemura",
        "scientificName": "Amphinemura sulcicollis (Stephens, 1836)",
        "canonicalName": "Amphinemura sulcicollis",
        "class": "Insecta"
    },
    {
        "key": 8024689,
        "order": "Plecoptera",
        "family": "Perlidae",
        "genus": "Acroneuria",
        "species": "Acroneuria abnormis",
        "parent": "Acroneuria",
        "scientificName": "Acroneuria abnormis (Newman, 1838)",
        "canonicalName": "Acroneuria abnormis",
        "class": "Insecta"
    },
    {
        "key": 3691582,
        "order": "Trichoptera",
        "family": "Hydropsychidae",
        "genus": "Hydropsyche",
        "species": "Hydropsyche pellucidula",
        "parent": "Hydropsyche",
        "scientificName": "Hydropsyche pellucidula (Curtis, 1834)",
        "canonicalName": "Hydropsyche pellucidula",
        "class": "Insecta"
    }
]

@pytest.fixture
def taxonomy(tmpdir):
    p = tmpdir.mkdir("taxonomy")
    taxonomy_data_dir = p.join("taxonomy.json")
    with taxonomy_data_dir.open("w") as f:
        json.dump(taxonomy_data, f,indent=2)
    return init_taxonomy(taxonomy_data_dir)

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
    @pytest.mark.parametrize("test_input,expected", [
        ('Hydropsyche pellucidula', ['Trichoptera', 'Hydropsychidae', 'Hydropsyche', 'Hydropsyche pellucidula']),
        ('Baetis rhodani', ['Ephemeroptera', 'Baetidae', 'Baetis', 'Baetis rhodani']),
        ('Amphinemura sulcicollis', ['Plecoptera', 'Nemouridae', 'Amphinemura', 'Amphinemura sulcicollis']),
        # Add more test cases as needed
    ])
    def test_set_species_name(self, qtbot, taxonomy, test_input, expected):
        widget = DataCollection(taxonomy)
        qtbot.addWidget(widget)
        item = QListWidgetItem()
        item.setText(test_input)
        widget.species_widget.item_clicked(item)
        data = widget.get_data()


        assert data.get("Order") == expected[0]
        assert data.get("Family") == expected[1]
        assert data.get("Genus") == expected[2]
        assert data.get("Species") == expected[3]
        
    def test_get_data(self, qtbot, taxonomy):
        widget = DataCollection(taxonomy)
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
        
    def test_set_museum(self, qtbot, taxonomy):
        widget = DataCollection(taxonomy)
        qtbot.addWidget(widget)
        item = QListWidgetItem()
        item.setText("Museum of Natural History")
        with pytest.raises(ValueError):
            widget.museum_widget.item_clicked(item)