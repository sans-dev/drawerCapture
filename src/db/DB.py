import numpy as np
import yaml
from pathlib import Path
import cv2
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
    def validate_meta_info(meta_info):
        contains_exception = any(isinstance(value, Exception) for value in meta_info.values())
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
    def __init__(self, project_root_dir, project_info=None):
        self.project_root_dir = project_root_dir
        if not project_info:
            self.load_project()
        else:
            self.init_project(project_info)

    def init_project(project_info):
        pass

    def load_project(self):
        project_info_file = self.project_root_dir / ".project_info.yaml"
        self.project_info = yaml.safe_load(project_info_file.read_text())
        self.image_number = self.project_info['image_number']

    def save_image_and_meta_info(self, payload):
        image_data = payload.get('image')
        meta_info = payload.get('meta_info')
        is_valid, msg = DataValidator.validate_image_data(image_data)
        if not is_valid:
            print("Invalid image data", msg)
            return
        is_valid, msg = DataValidator.validate_meta_info(meta_info)
        if not is_valid:
            print("Invalid meta data", msg)
            return
        # Save data to the database
        logger.info("Saving data")
        img_name, meta_name = self.create_save_name(meta_info)

        # save data
        img_name.parent.mkdir(exist_ok=True, parents=True)
        meta_name.parent.mkdir(exist_ok=True, parents=True)

        cv2.imwrite(img_name.as_posix(),image_data)
        with meta_name.open('w') as f:
            yaml.dump(meta_info, f)
        self.update_project_info()

        # update project info file and its representation
        # logic if saving failes (resetting of image number...)

    def load_image_and_meta_info(self, data):
        # Validate data received from DB
        if not DataValidator.validate_data_from_db(data):
            # Handle validation error
            return
        # Process and load data from the database

    def create_save_name(self, meta_info):
        self.image_number += 1 
        img_name = self.project_root_dir / "images" / f"img_{self.image_number}-{meta_info['museum']}-{meta_info['species'].replace(" ", "_")}.jpg"
        meta_name = self.project_root_dir / "meta_info" / f"img_{self.image_number}-{meta_info['museum']}-{meta_info['species'].replace(" ", "_")}.yaml"
        return img_name, meta_name

    def add_exif_info(self, image):
        pass

    def update_project_info(self):
        self.project_info['image_number'] = self.image_number
        with self.project_root_dir.open('w'):
            json.dump(self.project_info)

    def connect_db_adapter(self, db_adapter):
        db_adapter.put_signal.connect(self.save_image_and_meta_info)
        db_adapter.get_signal.connect(self.load_image_and_meta_info)
