from PyQt6.QtCore import QObject, pyqtSignal

class DataValidator:
    @staticmethod
    def validate_data(image_data, meta_info):
        # Perform validation checks on image_data and meta_info
        # Return True if data is valid, False otherwise
        pass

    @staticmethod
    def validate_data_from_db(data):
        # Perform validation checks on data received from DB
        # Return True if data is valid, False otherwise
        pass

class DBAdapter(QObject):
    put_signal = pyqtSignal(dict)
    get_signal = pyqtSignal(dict)
    validation_error_signal = pyqtSignal(str)

    def __init__(self, validator):
        super().__init__()
        self.validator = validator

    def send_data_to_db(self, image_data, meta_info):
        if not self.validator.validate_data(image_data, meta_info):
            self.validation_error_signal.emit("Validation failed: Invalid data")
            return
        payload = {'image': image_data, 'meta_info': meta_info}
        self.put_signal.emit(payload)

    def receive_data_from_db(self, data):
        if not self.validator.validate_data_from_db(data):
            self.validation_error_signal.emit("Validation failed: Invalid data received from DB")
            return
        self.get_signal.emit(data)

class DBManager:
    def __init__(self, validator):
        self.validator = validator

    def save_image_and_meta_info(self, payload):
        image_data = payload.get('image')
        meta_info = payload.get('meta_info')
        if not self.validator.validate_data(image_data, meta_info):
            # Handle validation error
            return
        # Save data to the database

    def load_image_and_meta_info(self, data):
        # Validate data received from DB
        if not self.validator.validate_data_from_db(data):
            # Handle validation error
            return
        # Process and load data from the database
