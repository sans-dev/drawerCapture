'''
"""
Module: MapWidget.py
Author: Sebastian Sander
This module contains the MapWindow class, which represents a PyQt6 widget for displaying an offline world map. It provides functionality for searching and displaying country data on the map, as well as obtaining coordinates by right-clicking on the map.
Usage:
    To use this module, create an instance of the MapWindow class and pass the necessary parameters. The map will be displayed in a PyQt6 window.
Example:
"""
    """
    A PyQt6 widget for displaying an offline world map and interacting with it.
    Args:
        server_api (str): The API address for the map server. Default is 'http://localhost:3650/api/maps/'.
        map_id (str): The ID of the map to be displayed. Default is 'openmap-basic'.
        region_data (None or dict): Data for regions. Default is None.
        search_bar (None or QLineEdit): The search bar widget for entering country names. Default is None.
    Signals:
        new_coords_signal (tuple): Signal emitted when new coordinates are obtained.
    """
        """
        Initialize the MapWindow widget.
        Args:
            server_api (str): The API address for the map server.
            map_id (str): The ID of the map to be displayed.
            region_data (None or dict): Data for regions.
            search_bar (None or QLineEdit): The search bar widget for entering country names.
        """
        pass
        """
        Initialize the user interface of the MapWindow widget.
        Args:
            search_bar (None or QLineEdit): The search bar widget for entering country names.
        """
        pass
        """
        Event filter for handling right-click events on the map.
        Args:
            source (QObject): The source object that triggered the event.
            event (QEvent): The event object.
        Returns:
            bool: True if the event was handled, False otherwise.
        """
        pass
        """
        Get the coordinates of a point on the map.
        Args:
            position (QPoint): The position of the point.
        """
        pass
        """
        Calculate the height of a map tile in degrees.
        Args:
            lat_deg (float): The latitude in degrees.
            zoom (float): The zoom level.
        Returns:
            float: The height of a map tile in degrees.
        """
        pass
        """
        Convert pixel coordinates to geographic coordinates.
        Args:
            zoom (float): The zoom level.
            pixel_x (int): The x-coordinate of the pixel.
            pixel_y (int): The y-coordinate of the pixel.
            center_lat (float): The latitude of the center of the map.
            center_lon (float): The longitude of the center of the map.
        Returns:
            tuple: The latitude and longitude of the converted coordinates.
        """
        pass
        """
        Load country data from a CSV file.
        """
        pass
        """
        Search for a country and update the map.
        """
        pass
        """
        Get the bounding box coordinates of a country.
        Args:
            country_name (str): The name of the country.
        Returns:
            list or None: The bounding box coordinates if found, None otherwise.
        """
        pass
        """
        Update the map with new bounding box coordinates.
        Args:
            bbox (list): The bounding box coordinates.
        """
        pass
        """
        Calculate the starting zoom level for the map.
        Args:
            bounds (list): The bounding box coordinates.
        Returns:
            float: The starting zoom level.
        """
        pass
        """
        Handle key press events.
        Args:
            event (QKeyEvent): The key event.
        """
        pass

'''
import sys
import pandas as pd
import numpy as np
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout, QMenu
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QEvent, pyqtSignal
from PyQt6.QtGui import QAction



class MapWindow(QWidget):
    new_coords_signal = pyqtSignal(tuple)
    def __init__(self, server_api='http://localhost:3650/api/maps/', map_id='openmap-basic', region_data=None,  search_bar=None):
        super().__init__()
        self.setWindowTitle("Offline World Map")
        self.server_api = server_api
        self.map_id = map_id
        self.region_data = region_data
        self.initUI(search_bar)
        self.load_country_data()
        self.search_country()
    
    def initUI(self, search_bar):  
        layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        
        if search_bar is not None:
            self.search_bar = search_bar(self.region_data)
        else:
            self.search_bar = QLineEdit()
            self.search_bar.setPlaceholderText("Enter a country name...")
        
        self.search_button = QPushButton("Search")
        self.search_button.setFixedHeight(20)
        self.search_button.clicked.connect(self.search_country)
        
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        self.web_view = QWebEngineView()
        self.setMouseTracking(True)
        self.web_view.setMouseTracking(True)
        api_address = f'{self.server_api}{self.map_id}'
        self.web_view.load(QUrl(api_address))
        
        layout.addWidget(self.web_view)
        
        self.setLayout(layout)
        self.show()
        self.web_view.installEventFilter(self)

    def eventFilter(self, source, event):
        if source is self.web_view and event.type() == QEvent.Type.ContextMenu:
            menu = QMenu()
            get_coords_action = QAction("Get Coordinates", self)
            get_coords_action.triggered.connect(lambda: self.get_coordinates(event.pos()))
            menu.addAction(get_coords_action)
            menu.exec(event.globalPos())
            return True
        return False

    def get_coordinates(self, position):
        zoom, center_lat, center_lon = list(map(float,self.web_view.url().toString().split("#")[1].split("/")))
        long, lat = self.pixel_to_geo(zoom, position.x(), position.y(), center_lat, center_lon)
        print(long, lat)
    
    def tile_height_deg(self, lat_deg, zoom):
        lat_rad = np.radians(lat_deg)
        n = np.power(2, zoom)
        tile_height_deg = 360.0 / (n * np.cosh(lat_rad))
        return tile_height_deg

    def pixel_to_geo(self, zoom, pixel_x, pixel_y, center_lat, center_lon):
        n_tiles = np.power(2,zoom)
        tile_width = 360 / n_tiles
        tile_height = self.tile_height_deg(center_lat, zoom)
        
        width = self.web_view.geometry().width()
        height = self.web_view.geometry().height()

        n_tiles_width = width / 512 
        n_tiles_height = height / 512

        lat = center_lat - ((pixel_y - (height / 2)) / height) * (tile_height*n_tiles_height)
        lon = center_lon + ((pixel_x - (width / 2)) / width) * tile_width*n_tiles_width
        url = f'{self.server_api}{self.map_id}#{zoom:.2f}/{lat}/{lon}'
        self.web_view.load(QUrl(url))
        self.new_coords_signal.emit((lon, lat))
        country = self.search_bar.get_country_by_coords((lon, lat))
        self.search_bar.set_region(country)
        return lat, lon
    
    def load_country_data(self):
        self.country_data = pd.read_csv('resources/countries/administrative-level-0.csv', delimiter=',')

    def search_country(self):
        if isinstance(self.search_bar, QLineEdit):
            country_name = self.search_bar.text()
        else:
            country_name = self.search_bar.region_input.currentText()
        if country_name:
            coordinates = self.get_country_bounding_box(country_name)
            if coordinates:
                self.update_map(coordinates)

    def get_country_bounding_box(self, country_name):
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
            self.search_country()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    api_address = 'http://localhost:3650/api/maps/'
    window = MapWindow(api_address, 'openmap-basic')
    window.show()
    sys.exit(app.exec())