import numpy as np
import yaml
from pathlib import Path
import cv2
import copy
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
    create_project_signal = pyqtSignal(dict, str)
    load_project_signal = pyqtSignal(Path)
    validation_error_signal = pyqtSignal(str)
    project_changed_signal = pyqtSignal(dict)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

    def create_session(self, session_data):
        self.project_changed_signal.emit(self.db_manager.create_session(session_data))

    def create_project(self, project_info, project_dir):
        self.project_changed_signal.emit(self.db_manager.create_project(project_info, project_dir))

    def load_project(self, project_dir):
        self.project_changed_signal.emit(self.db_manager.load_project(project_dir))

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
        self.project_changed_signal.emit(self.db_manager.post_new_image(payload))
        return True # control outside behavior

    def receive_data_from_db(self, data):
        if not DataValidator.validate_data_from_db(data):
            self.validation_error_signal.emit("Validation failed: Invalid data received from DB")
            return
        self.get_signal.emit(data)

    
class FileAgnosticDB:
    def __init__(self):
        super().__init__()
        self.project_root_dir = None
        self.current_session = None

    def load_project(self, project_dir):
        self.project_info = configparser.ConfigParser()
        self.project_info.read((Path(project_dir) / 'project.ini'))
        self.image_number = self.project_info.getint('Captures Info', "num_imgs")
        self.project_root_dir = Path(project_dir)
        return self.create_dict_from_config()

    def post_new_image(self, payload):
        image_data = payload.get('image')
        meta_info = payload.get('meta_info')
        # Save data to the database
        logger.info("Saving data")
        old_conf = copy.deepcopy(self.project_info)
        try:
            project_options = {
                'num_captures' : self.project_info.getint('Project Info', "num_captures") + 1
            }
            self.update_project_config(section="Project Info", options=project_options)
            
            session_options = {
                'num_captures' : self.project_info.getint(f"Session {self.current_session_id}", "num_captures") + 1
            }
            self.update_project_config(section=f"Session {self.current_session_id}", options=session_options)

            self.write_project_config()
            img_name, meta_name = self.create_save_name(meta_info)
            img_name.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(img_name.as_posix(),image_data)
            with meta_name.open('w') as f:
                yaml.dump(meta_info, f)
            return self.create_dict_from_config()
        
        except FileNotFoundError as e:
            logger.error(e)
            self.project_info = old_conf
            # delete image and meta file
            Path(img_name).unlink()
            Path(meta_name).unlink()

            return self.create_dict_from_config()
        
        except Exception as e:
            logger.error(e)
            self.project_info = old_conf
            Path(img_name).unlink()
            Path(meta_name).unlink()
            return self.create_dict_from_config()

    def update_project_config(self, section, options):
        if section not in self.project_info.sections():
            self.project_info.add_section(section)
        
        for option, value in options.items():
            self.project_info.set(section, option, str(value))
        
    def write_project_config(self):
        with open(self.project_root_dir / 'project.ini', 'w') as configfile:
            self.project_info.write(configfile)

    def get_project_config(self):
        return self.project_info
    
    def load_image_and_meta_info(self, data):
        # Validate data received from DB
        if not DataValidator.validate_data_from_db(data):
            # Handle validation error
            return
        # Process and load data from the database

    def create_save_name(self, meta_info):
        session_name = f"session_{self.current_session_id}"
        img_id = self.project_info.getint('Project Info', "num_captures")
        img_name = self.project_root_dir / "captures" / session_name / f"{str(img_id).zfill(4)}-{meta_info['Museum']}-{meta_info['Species'].replace(' ', '_')}.jpg"
        meta_name = self.project_root_dir / "captures" / session_name / f"{str(img_id).zfill(4)}-{meta_info['Museum']}-{meta_info['Species'].replace(' ', '_')}.yaml"
        return img_name, meta_name

    def add_exif_info(self, image, info):
        pass

    def create_project(self, project_info, project_dir):
        self.project_info = configparser.ConfigParser()
        project_dir = Path(project_dir)
        project_dir.mkdir(exist_ok=True)
        (project_dir / 'captures').mkdir(exist_ok=True)
        (project_dir / 'captures.csv').write_text("date, session, museum, order, family, genus, species\n")
        self.create_config_from_dict(project_info)
        with (project_dir / 'project.ini').open('w') as config_file:
            self.project_info.write(config_file)

        self.project_root_dir = project_dir
        return self.create_dict_from_config()

    def create_config_from_dict(self, config_dict):
        for section, options in config_dict.items():
            self.project_info.add_section(section)
            for option, value in options.items():
                self.project_info.set(section, option, str(value))

    def create_dict_from_config(self):
        config_dict = {}
        for section in self.project_info.sections():
            config_dict[section] = {}
            for option in self.project_info.options(section):
                config_dict[section][option] = self.project_info.get(section, option)
        return config_dict

    def create_session(self, session_name, session_data):
        if self.project_info:
            section = session_name
            self.update_project_config(section, session_data)
            self.current_session_id = session_data['id']
            self.write_project_config()
            return self.create_dict_from_config()
        else:
            raise ValueError('No project info available')