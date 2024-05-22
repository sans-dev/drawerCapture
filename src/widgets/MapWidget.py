import sys
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
import PyQt6.QtCore as QtCore

class MapWindow(QWidget):
    def __init__(self, server_api='http://localhost:3650/api/maps/', map_id='openmapbasic', search_bar=None):
        super().__init__()
        self.setWindowTitle("Offline World Map")
        self.server_api = server_api
        self.map_id = map_id
        self.initUI(search_bar)
        self.load_country_data()

    def initUI(self, search_bar):  
        # Create layout
        layout = QVBoxLayout()
        
        # Create search bar layout
        search_layout = QHBoxLayout()
        
        # Create search bar
        if search_bar is not None:
            self.search_bar = search_bar()
        else:
            self.search_bar = QLineEdit()
            self.search_bar.setPlaceholderText("Enter a country name...")
        
        # Create search button
        self.search_button = QPushButton("Search")
        self.search_button.setFixedHeight(20)
        self.search_button.clicked.connect(self.search_country)
        
        # Add search bar and button to search layout
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_button)
        # Add search layout to main layout
        layout.addLayout(search_layout)
        
        # Create web view
        self.web_view = QWebEngineView()
        api_address = f'{self.server_api}{self.map_id}'
        self.web_view.load(QUrl(api_address))
        
        # Add web view to main layout
        layout.addWidget(self.web_view)
        
        # Set layout to central widget
        self.setLayout(layout)
        
        self.show()

    def load_country_data(self):
        # Load country data from CSV
        self.country_data = pd.read_csv('resources/countries/administrative-level-0.csv', delimiter=',')

    def search_country(self):
        country_name = self.search_bar.text()
        if country_name:
            coordinates = self.get_country_bounding_box(country_name)
            if coordinates:
                self.update_map(coordinates)

    def get_country_bounding_box(self, country_name):
        # Fetch bounding box for the given country name
        country_row = self.country_data[self.country_data['name'].str.contains(country_name, case=False)]
        if not country_row.empty:
            bbox_str = country_row.iloc[0]['bbox']
            bbox = [float(coord) for coord in bbox_str.split()]
            return bbox
        return None

    def update_map(self, bbox):
        west, south, east, north = bbox
        center_lat = (north + south) / 2
        center_lon = (west + east) / 2
        bounds = [[south, west], [north, east]]
        zoom_start = self.calc_start_zoom(bounds)
        api_address = f'{self.server_api}{self.map_id}#{zoom_start:.2f}/{center_lat:.5f}/{center_lon:.5f}'
        print(api_address)
        self.web_view.load(QUrl(api_address))

    def calc_start_zoom(self, bounds):
        bounds = [coord for bound in bounds for coord in bound]
        world_height = bounds[3] - bounds[1]
        window_height = self.web_view.height()

        world_width = bounds[2] - bounds[0]
        window_width = self.web_view.width()
        zoom_height = np.log2(window_height / world_height)
        zoom_width = np.log2(window_width / world_width)

        return min(zoom_height, zoom_width)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and self.search_bar.hasFocus():
            print('Enter pressed')
            self.search_country()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    api_address = 'http://localhost:3650/api/maps/'
    window = MapWindow(api_address, 'openmapbasic')
    window.show()
    sys.exit(app.exec())
