import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class DataValidator:
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

        # Additional checks can be added as needed

        # If all checks pass, return True for valid image data
        return True, None
    
    @staticmethod
    def validate_meta_data(meta_data):
        contains_exception = any(isinstance(value, Exception) for value in meta_data.values())
        if contains_exception:
            return False, "Mandatory fields left open"

class DBAdapter(QObject):
    put_signal = pyqtSignal(dict)
    get_signal = pyqtSignal(dict)
    validation_error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def send_data_to_db(self, image_data, meta_info):
        logger.info(f"Sending data to DB...")
        print(meta_info)
        payload = {'image': image_data, 'meta_info': meta_info}
        self.put_signal.emit(payload)

    def receive_data_from_db(self, data):
        if not self.validator.validate_data_from_db(data):
            self.validation_error_signal.emit("Validation failed: Invalid data received from DB")
            return
        self.get_signal.emit(data)

class DBManager:
    def save_image_and_meta_info(self, payload):
        image_data = payload.get('image')
        meta_info = payload.get('meta_info')
        is_valid, msg = DataValidator.validate_image_data(image_data)
        if not is_valid:
            print("Invalid image data", msg)
            return
        is_valid, msg = DataValidator.validate_meta_data(meta_info)
        if not is_valid:
            print("Invalid image data", msg)
            return
        # Save data to the database
        logger.info("Saving data")

    def load_image_and_meta_info(self, data):
        # Validate data received from DB
        if not self.validator.validate_data_from_db(data):
            # Handle validation error
            return
        # Process and load data from the database

    def connect_db_adapter(self, db_adapter):
        db_adapter.put_signal.connect(self.save_image_and_meta_info)
        db_adapter.get_signal.connect(self.load_image_and_meta_info)
