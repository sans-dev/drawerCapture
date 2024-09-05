"""
Module: Validation
This module provides classes and methods for data validation.
Author: Sebastian Sander
"""


from pathlib import Path

class DataValidator:
    @staticmethod
    def validate_project_config(config):
        #TODO implement validation
        return True

    @staticmethod
    def validate_data_from_db(data):
        # Perform validation checks on data received from DB
        # Return True if data is valid, False otherwise
        pass

    @staticmethod
    def validate_image_data(img_dir):
        # Check if image_data is a numpy array
        if not isinstance(img_dir, str):
            return False, "Image data must be a string object"

        if not Path(img_dir).is_file():
            return False, "No image data found in tmp dir"
        # If all checks pass, return True for valid image data
        return True, None
    
    @staticmethod
    def validate_meta_info(meta_info):
        contains_exception = any(isinstance(value, Exception) for value in meta_info.values())
        if contains_exception:
            return False, "Mandatory fields left open"
        else: return True, None 

    @staticmethod
    def validate_museum(museum):
        if not isinstance(museum, dict):
            return False, "Museum information must be a dictionary"
        if 'name' not in museum.keys():
            return False, "Museum information must contain a name field"
        if 'city' not in museum:
            return False, "Museum information must contain a city field"
        if 'street' not in museum:
            return False, "Museum information must contain a street field"
        if 'number' not in museum:
            return False, "Museum information must contain a number field"
        return True, None