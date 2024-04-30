import numpy as np
import yaml
from pathlib import Path
import cv2
import configparser
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
        else: return True, None 

class DBAdapter(QObject):
    put_signal = pyqtSignal(dict)
    get_signal = pyqtSignal(dict)
    create_project_signal = pyqtSignal(dict, Path)
    load_project_signal = pyqtSignal(Path)
    validation_error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def create_project(self, project_info, project_dir):
        self.create_project_signal.emit(project_info, Path(project_dir))

    def load_project(self, project_dir):
        self.load_project_signal.emit(Path(project_dir))

    def send_data_to_db(self, image_data, meta_info):
        logger.info(f"Validating data...")
        is_valid, msg = DataValidator.validate_image_data(image_data)
        if not is_valid:
            print("Invalid image data", msg)
            return False
        is_valid, msg = DataValidator.validate_meta_info(meta_info)
        if not is_valid:
            print("Invalid meta data", msg)
            return False
        logger.info(f"Sending data to DB...")
        payload = {'image': image_data, 'meta_info': meta_info}
        self.put_signal.emit(payload)
        return True

    def receive_data_from_db(self, data):
        if not DataValidator.validate_data_from_db(data):
            self.validation_error_signal.emit("Validation failed: Invalid data received from DB")
            return
        self.get_signal.emit(data)
    

    
class DBManager:
    def __init__(self):
        self.project_root_dir = None
        self.project_info = configparser.ConfigParser()
        self.image_number = None

    def load_project(self, project_dir):
        self.project_info.read((project_dir / 'project.ini'))
        self.image_number = self.project_info.get('VARS', "image-number")
        self.project_root_dir = project_dir

    def save_image_and_meta_info(self, payload):
        image_data = payload.get('image')
        meta_info = payload.get('meta_info')
        # Save data to the database
        logger.info("Saving data")
        img_name, meta_name = self.create_save_name(meta_info)
        cv2.imwrite(img_name.as_posix(),image_data)
        with meta_name.open('w') as f:
            yaml.dump(meta_info, f)
        self.update_project_info()

    def load_image_and_meta_info(self, data):
        # Validate data received from DB
        if not DataValidator.validate_data_from_db(data):
            # Handle validation error
            return
        # Process and load data from the database

    def create_save_name(self, meta_info):
        self.image_number += 1 
        img_name = self.project_root_dir / "images" / f"{str(self.image_number).zfill(4)}-{meta_info['Museum']}-{meta_info['Species'].replace(' ', '_')}.jpg"
        meta_name = self.project_root_dir / "meta_info" / f"{str(self.image_number).zfill(4)}-{meta_info['Museum']}-{meta_info['Species'].replace(' ', '_')}.yaml"
        return img_name, meta_name

    def add_exif_info(self, image):
        pass

    def update_project_info(self):
        self.project_info.set('VARS', 'image-number', self.image_number)
        (self.project_root_dir / 'project.ini').write_text(self.project_info)

    def create_project(self, project_info, project_dir):
        project_dir = project_dir
        project_dir.mkdir(exist_ok=True)
        (project_dir / 'Captures').mkdir(exist_ok=True)
        (project_dir / 'captures.csv').write_text("date, session, museum, order, family, genus, species\n")
        self.create_config_from_dict(project_info)
        with (project_dir / 'project.ini').open('w') as config_file:
            self.project_info.write(config_file)

        self.project_root_dir = project_dir
        self.project_info = project_info

    def connect_db_adapter(self, db_adapter):
        db_adapter.put_signal.connect(self.save_image_and_meta_info)
        db_adapter.get_signal.connect(self.load_image_and_meta_info)
        db_adapter.create_project_signal.connect(self.create_project)
        db_adapter.load_project_signal.connect(self.load_project)

    def create_config_from_dict(self, config_dict):
        for section, options in config_dict.items():
            self.project_info.add_section(section)
            for option, value in options.items():
                self.project_info.set(section, option, str(value))