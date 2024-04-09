import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import Qt


class SearchableItemListWidget(QWidget):
    def __init__(self, label_name, item_file):
        super().__init__()

        self.init_ui(label_name)
        self._load_items(item_file)

    def init_ui(self, label_name):
        layout = QVBoxLayout()
        self.label = QLabel(label_name)
        layout.addWidget(self.label)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self.filter_items)
        layout.addWidget(self.search_edit)

        self.item_list = QListWidget()
        self.item_list.setMaximumHeight(50)
        self.item_list.itemClicked.connect(self.item_clicked)
        layout.addWidget(self.item_list)

        self.setLayout(layout)

    def filter_items(self, text):
        self.item_list.clear()
        if text.strip():  # Check if search text is not empty
            # Replace this with your actual list of items
            filtered_items = [item for item in self.items if text.lower() in item.lower()]
            self.item_list.addItems(filtered_items)
        else:
            self.item_list.addItem("")

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
            

class MainForm(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Add multiple searchable item lists vertically
        layout.addWidget(SearchableItemListWidget("Fruits", 'src/examples/gui_examples/test_items.txt'))
        layout.addWidget(SearchableItemListWidget("Vegetables", 'src/examples/gui_examples/test_items.txt'))
        layout.addWidget(SearchableItemListWidget("Colors", 'src/examples/gui_examples/test_items.txt'))

        self.setLayout(layout)
        self.setWindowTitle("Form with Searchable Item Lists")

def main():
    app = QApplication(sys.argv)
    window = MainForm()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()