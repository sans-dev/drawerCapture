import numpy as np

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
    def validate_image_data(image_data):
        # Check if image_data is a numpy array
        if not isinstance(image_data, np.ndarray):
            return False, "Image data must be a numpy array"

        # Check if image_data has the correct shape (height, width, channels)
        if len(image_data.shape) != 3:
            return False, "Image data must have three dimensions (height, width, channels)"

        # Check if image_data has at least 3 channels (RGB or BGR)
        if image_data.shape[2] < 3:
            return False, "Image data must have at least 3 channels (RGB or BGR)"

        # Check if bit depth of image_data is 8 or 16
        if image_data.dtype!= np.uint8 and image_data.dtype!= np.uint16:
            return False, "Image data must be of type uint8 or uint16"
        # Additional checks can be added as needed

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