import numpy as np
import yaml
from pathlib import Path
import cv2
import copy
from cryptography.fernet import Fernet
import json
import configparser
from PyQt6.QtCore import QObject, pyqtSignal

import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

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

class DBAdapter(QObject):
    put_signal = pyqtSignal(dict)
    get_signal = pyqtSignal(dict)
    create_project_signal = pyqtSignal(dict, str)
    load_project_signal = pyqtSignal(Path)
    validation_error_signal = pyqtSignal(str)
    project_changed_signal = pyqtSignal(dict)
    session_created_signal = pyqtSignal(dict)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

    def create_session(self, session_data):
        self.project_changed_signal.emit(self.db_manager.create_session(session_data))
        self.session_created_signal.emit(session_data)

    def create_project(self, project_info):

        try:
            response = self.db_manager.create_project(project_info)
            self.project_changed_signal.emit(response)
            return response
        except Exception as e:
            logger.info(f"{e}")
            raise e

    def save_encrypted_users(self, user):
        self.db_manager.save_encrypted_users(user)

    def verify_credentials(self, username, password):
        return self.db_manager.verify_credentials(username, password)

    def load_project(self, project_dir):
        project_info = self.db_manager.load_project(project_dir)
        if project_info:
            self.project_changed_signal.emit(self.db_manager.load_project(project_dir))
            return True
        else: return False

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

    def validate_admin(self, username, password):
        return self.db_manager.validate_admin(username, password)

    def add_users(self, users):
        self.db_manager.save_encrypted_users(users)
    
    def count_admins(self):
        return self.db_manager.count_admins()
    
    def change_user_role(self, user_to_change, new_role):
        self.db_manager.change_user_role(user_to_change, new_role)

    def remove_user(self, user_to_remove):
        self.db_manager.remove_user(user_to_remove)

    def get_users(self):
        return self.db_manager.get_users()

class FileAgnosticDB:
    def __init__(self):
        super().__init__()
        self.project_root_dir = None
        self.current_session = None
        self.fernet = None
        
    def count_admins(self):
        users = self.get_users()
        admins = 0
        for user in users:
            if user['role'] == 'admin':
                admins += 1
        return admins

    def change_user_role(self, user_to_change, new_role):
        existing_users = self._load_credentials()
        for user in existing_users:
            if user['username'] == user_to_change:
                user['role'] = new_role
                break
        encrypted_data = self.fernet.encrypt(json.dumps(existing_users).encode())
        self._save_credentials(encrypted_data)

    def remove_user(self, user_to_remove):
        existing_users = self._load_credentials()
        for idx, user in enumerate(existing_users):
            if user['username'] == user_to_remove:
                existing_users.pop(idx)
                break
        encrypted_data = self.fernet.encrypt(json.dumps(existing_users).encode())
        self._save_credentials(encrypted_data)

    def load_project(self, project_dir):
        self.project_info = configparser.ConfigParser()
        self.project_info.read((Path(project_dir) / 'project.ini'))
        if DataValidator.validate_project_config(self.project_info):
            self.project_root_dir = Path(project_dir)
            self._initialize_key()
            return self.create_dict_from_config()
        else: return False

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
            raise e
        except TypeError as e:
            logger.error(e)
            self.project_info = old_conf
            raise e
        except Exception as e:
            logger.error(e)
            self.project_info = old_conf
            Path(img_name).unlink()
            Path(meta_name).unlink()
            raise e
        
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
        session_name = meta_info['Session Info']['name'].replace(" ","-").lower()
        img_id = "cap-" + str(self.project_info.getint('Project Info', "num_captures")).zfill(4)
        museum = meta_info['Session Info']['museum'].replace(" ","-").lower()
        species_name = f"{meta_info['Species Info']['Genus']}_{meta_info['Species Info']['Species']}"

        img_name = self.project_root_dir / "captures" / session_name / f"{img_id}_{museum}_{species_name}.jpg"
        meta_name = self.project_root_dir / "captures" / session_name / f"{img_id}_{museum}_{species_name}.yml"
        return img_name, meta_name

    def add_exif_info(self, image, info):
        pass

    def create_project(self, project_info):
        self.project_info = configparser.ConfigParser()
        project_dir = Path(project_info['Project Info']['project_dir'])
        project_dir.mkdir(exist_ok=True)
        (project_dir / 'captures').mkdir(exist_ok=True)
        (project_dir / 'captures.csv').write_text("date, session, museum, order, family, genus, species\n")
        self.create_config_from_dict(project_info)
        with (project_dir / 'project.ini').open('w') as config_file:
            self.project_info.write(config_file)

        self.project_root_dir = project_dir
        self._initialize_key()
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

    def create_session(self, session_data):
        if self.project_info:
            section = session_data['name']
            self.update_project_config(section, session_data)
            self.current_session_id = session_data['id']
            self.write_project_config()
            return self.create_dict_from_config()
        else:
            raise ValueError('No project info available')

    def get_users(self):
        """
        Retrieve all users from the encrypted credentials file.
        Returns a list of dictionaries, each containing user information.
        """
        users = self._load_credentials()
        # Return user info without passwords
        return [{"username": user['username'], "role": user['role']} for user in users]

    def verify_credentials(self, username, password):
        existing_users = self._load_credentials()
        # Verify the credentials
        for user in existing_users:
            if user['username'] == username:
                if user['password'] == password:
                    return {"username": user['username'], "role": user['role']}
            return None
       
    def validate_admin(self, username, password):
        user = self.verify_credentials(username, password)
        if user:
            if user['role'] == 'admin':
                return True
        return False
    
    def save_encrypted_users(self, new_user):
        # Load and decrypt existing users
        existing_users = self._load_credentials() 
        # Check if user already exists
        self._check_duplicate_users(existing_users, new_user)
        # Add the new user to the existing users
        existing_users.append(new_user)
        # Encrypt the updated users list
        encrypted_data = self.fernet.encrypt(json.dumps(existing_users).encode())
        self._save_credentials(encrypted_data)
        
    def _save_credentials(self, encrypted_data):
        credentials_path = self.project_root_dir / ".credentials"
        # Save the encrypted data to the file
        with open(credentials_path, "wb") as f:
            f.write(encrypted_data)

    def _check_duplicate_users(self, existing_users, new_user):
        if any(user['username'] == new_user['username'] for user in existing_users):
                    raise ValueError(f"User '{new_user['username']}' already exists")
        
    def _load_credentials(self):
        existing_users = []
        credentials_path = self.project_root_dir / ".credentials"
        if credentials_path.exists():
            try:
                with open(credentials_path, "rb") as f:
                    encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                existing_users = json.loads(decrypted_data.decode())
                return existing_users
            except json.JSONDecodeError:
                print("Error decoding user data.")
                return []
            except Exception as e:
                print(f"An error occurred: {e}")
                return []

    def _initialize_key(self):
        key_path = self.project_root_dir / ".key"
        if key_path.exists():
            self._load_key(key_path)
        else:
            self._create_key(key_path)

    def _load_key(self, key_path):
        try:
            with open(key_path, "rb") as key_file:
                key = key_file.read()
            self.fernet = Fernet(key)
        except Exception as e:
            raise RuntimeError(f"Failed to load encryption key: {str(e)}")

    def _create_key(self, key_path):
        try:
            key = Fernet.generate_key()
            with open(key_path, "wb") as key_file:
                key_file.write(key)
            self.fernet = Fernet(key)
        except Exception as e:
            raise RuntimeError(f"Failed to create encryption key: {str(e)}")
        
class DummyDB:
   def create_session(self, payload):
       pass

   def create_project(self, payload):
       if not payload:
           raise NotADirectoryError("Wrong request format.")
       else:
           return payload

   def load_project(self, payload):
       pass

   def post_new_image(self, payload):
       print(payload)
       return payload