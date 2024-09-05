"""
Module for downloading OpenStreetMap tiles.

Author: Sebastian Sander

This module provides functions for downloading OpenStreetMap tiles within a specified area and zoom levels.
The `download_tiles` function takes the minimum and maximum zoom levels, latitude and longitude boundaries, and an output directory as parameters.
It creates the necessary directory structure and downloads the tiles using the `download_tile` function.

Example usage:
"""

import os
import requests
from tqdm import tqdm

def download_tile(z, x, y, save_path):
    url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

def download_tiles(min_zoom, max_zoom, min_lat, max_lat, min_lon, max_lon, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for z in range(min_zoom, max_zoom + 1):
        lat_step = (max_lat - min_lat) / (2 ** z)
        lon_step = (max_lon - min_lon) / (2 ** z)
        for x in tqdm(range(int((min_lon + 180) / lon_step), int((max_lon + 180) / lon_step))):
            for y in range(int((min_lat + 90) / lat_step), int((max_lat + 90) / lat_step)):
                tile_dir = os.path.join(output_dir, str(z), str(x))
                os.makedirs(tile_dir, exist_ok=True)
                tile_path = os.path.join(tile_dir, f"{y}.png")
                if not os.path.exists(tile_path):
                    download_tile(z, x, y, tile_path)

# Define your area and zoom levels
min_zoom = 0
max_zoom = 5
min_lat = -85.0511  # Near the South Pole
max_lat = 85.0511   # Near the North Pole
min_lon = -180
max_lon = 180
output_dir = "resources/osm/tiles"

# Start downloading
download_tiles(min_zoom, max_zoom, min_lat, max_lat, min_lon, max_lon, output_dir)
