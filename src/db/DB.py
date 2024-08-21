import yaml
import uuid
import hashlib
from pathlib import Path
import cv2
import csv
from datetime import datetime
from cryptography.fernet import Fernet
import json
import configparser
from PyQt6.QtCore import QObject, pyqtSignal
from src.utils.Validation import DataValidator

import logging
import logging.config
logging.config.fileConfig('configs/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class DBAdapter(QObject):
    put_signal = pyqtSignal(dict)
    get_signal = pyqtSignal(dict)
    create_project_signal = pyqtSignal(dict, str)
    load_project_signal = pyqtSignal(Path)
    validation_error_signal = pyqtSignal(str)
    project_changed_signal = pyqtSignal(dict)
    session_created_signal = pyqtSignal(dict)
    sessions_signal = pyqtSignal(dict)

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

    def create_session(self, session_data):
        sessions = self.db_manager.create_session(session_data)
        self.sessions_signal.emit(sessions)

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
        sessions = self.db_manager.load_sessions()
        self.project_changed_signal.emit(project_info)
        self.sessions_signal.emit(sessions)

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

    def add_user(self, user):
        self.db_manager.add_user(user)
    
    def count_admins(self):
        return self.db_manager.count_admins()
    
    def change_user_role(self, user_to_change, new_role):
        self.db_manager.change_user_role(user_to_change, new_role)

    def remove_user(self, user_to_remove):
        self.db_manager.remove_user(user_to_remove)

    def get_users(self):
        return self.db_manager.get_users()
    
    def get_museums(self):
        return self.db_manager.get_museums()
    
    def get_museum(self, museum):
        return self.db_manager.get_museum(museum)
    
    def add_museum(self, museum):
        return self.db_manager.add_museum(museum)
    
    def remove_museum(self, museum):
        return self.db_manager.remove_museum(museum)
    
    def edit_museum(self, museum_to_edit, updated_museum):
        return self.db_manager.edit_museum(museum_to_edit, updated_museum)
    
    def reset_password(self, username, role, old_password, new_password):
        return self.db_manager.reset_password(username, role, old_password, new_password)
    
    def get_current_user(self):
        return self.db_manager.get_current_user()

class FileAgnosticDB:
    def __init__(self):
        self.project_root_dir = None
        self.current_session = None
        self.fernet = None
        self.current_user = None

    def create_project(self, project_info):
        project_dir = Path(project_info['project_dir'])
        project_dir.mkdir(exist_ok=True)
        
        # Create captures directory and CSV file
        (project_dir / 'captures').mkdir(exist_ok=True)
        self._create_captures_csv(project_dir)
        
        # Create .project directory and files
        project_data_dir = project_dir / '.project'
        project_data_dir.mkdir(exist_ok=True)
        
        (project_data_dir / '.project.ini').touch()
        (project_data_dir / '.sessions.json').write_text('{}')
        (project_data_dir / '.museums.json').write_text('{}')
        
        # Write project info to .project.ini
        config = configparser.ConfigParser()
        config['Project Info'] = project_info
        with (project_data_dir / '.project.ini').open('w') as f:
            config.write(f)
        
        self.project_root_dir = project_dir
        self._initialize_key()
        return self.get_project_info()

    def create_session(self, session_data):
        session_id = str(uuid.uuid4())
        sessions_file = self.project_root_dir / '.project' / '.sessions.json'
        if not sessions_file.is_file():
            raise FileNotFoundError(f"No sessions file found. {sessions_file}")
        sessions = json.loads(sessions_file.read_text())
        n_sessions = len(sessions)
        session_data['name'] = f"session-{str(n_sessions + 1).zfill(3)}"
        session_data['creation_date'] = datetime.now().isoformat()
        session_data['session_dir'] = (Path('captures') / f"{session_data['name']}").as_posix()
        session_data['num_captures'] = 0
        session_data['captures'] = []
        sessions[session_id] = session_data
        sessions_file.write_text(json.dumps(sessions, indent=2))
        Path(self.project_root_dir / session_data['session_dir']).mkdir()
        return sessions

    def load_sessions(self):
        sessions_file = self.project_root_dir / ".project/.sessions.json"
        if not sessions_file.is_file():
            raise FileNotFoundError(f"Session data missing for {sessions_file}")
        with sessions_file.open() as f:
            sessions = json.load(f)
        return sessions
        
    def post_new_image(self, payload):
        image_data = payload.get('image')
        meta_info = payload.get('meta_info')
        
        sessions_file = self.project_root_dir / '.project' / '.sessions.json'
        sessions = json.loads(sessions_file.read_text())
        session = sessions.get(payload['session_id'])
        if not session:
            raise ValueError("Session not found")
        
        session['num_captures'] += 1
        capture_id = session['num_captures']
        img_name, meta_name = self._create_save_name(meta_info, capture_id, session)
        session['captures'].append(str(img_name.relative_to(self.project_root_dir)))

        sessions_file.write_text(json.dumps(sessions, indent=2))
        
        if not cv2.imwrite(str(img_name), image_data):
            raise RuntimeError("Failed to save image")
        
        with meta_name.open('w') as f:
            yaml.dump(meta_info, f)
        
        self._update_captures_csv(meta_info, session)
        
        return self.get_project_info()

    def get_project_info(self):
        config = configparser.ConfigParser()
        project_file = self.project_root_dir / '.project' / '.project.ini'
        if not project_file.is_file():
            raise FileNotFoundError(f"Project INI file missing at {project_file}")
        config.read(project_file)
        return {section: dict(config[section]) for section in config.sections()}

    def is_duplicate_museum(self, museum, museums):
        for _, m in museums.items():
            if m['name'] == museum['name'] and m['city'] == museum['city']:
                return True
        return False
    
    def add_museum(self, museum):
        is_valid, msg = DataValidator.validate_museum(museum)
        if not is_valid:
            raise ValueError(msg)
        museums = self.get_museums()
        new_id = self._create_uuid_from_string(self._create_string_from_dict_values(museum))
        is_duplicate = museums.get(new_id, None)
        if is_duplicate:
            raise ValueError(f"Museum '{museum['name']}' already exists in '{museum['city']}'")
        museums[new_id] = museum
        self.save_musems(museums)
        return True

    def save_musems(self, museums):
        museums_file = self.project_root_dir / '.project' / '.museums.json'
        museums_file.write_text(json.dumps(museums, indent=2))

    def get_museums(self):
        museums_file = self.project_root_dir / '.project' / '.museums.json'
        return json.loads(museums_file.read_text())

    def edit_museum(self, original, updated):
        museums = self.get_museums()
        m_string = self._create_string_from_dict_values(original)
        old_id = self._create_uuid_from_string(m_string)
        del museums[old_id]
        m_string = self._create_string_from_dict_values(original)
        new_id = self._create_uuid_from_string(m_string)
        museums[new_id] = updated
        self.save_musems(museums)

    def remove_museum(self, museum):
        m_id = self._create_uuid_from_string(self._create_string_from_dict_values(museum))
        museums = self.get_museums()
        del museums[m_id]
        self.save_musems(museums)

    def reset_password(self, username, role, old_password, new_password):
        existing_users = self._load_credentials()
        for user in existing_users:
            if user['username'] == username and user['password'] == old_password:
                user['password'] = new_password
                break
        encrypted_data = self.fernet.encrypt(json.dumps(existing_users).encode())
        self._save_credentials(encrypted_data)
        return True

    def count_admins(self):
        users = self.get_users()
        admins = 0
        for user in users:
            if user['role'] == 'admin':
                admins += 1
        return admins

    def change_user_role(self, user_to_change, new_role):
        existing_users = self.get_users()
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
        self.project_root_dir = Path(project_dir)
        project_info = self.get_project_info()
        if not DataValidator.validate_project_config(project_info):
            raise ValueError(f"Project data are not valid for {project_dir}")
        self._initialize_key()
        return project_info
        
    def load_image_and_meta_info(self, data):
        # Validate data received from DB
        if not DataValidator.validate_data_from_db(data):
            # Handle validation error
            return
        # Process and load data from the database

    def add_exif_info(self, image, info):
        pass

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
                    self.current_user = user
                    return {"username": user['username'], "role": user['role']}
        return None
       
    def validate_admin(self, username, password):
        user = self.verify_credentials(username, password)
        if user:
            if user['role'] == 'admin':
                return True
        return False
    
    def get_current_user(self):
        return self.current_user
    
    def add_user(self, new_user):
        self.save_encrypted_users(new_user)

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
        credentials_path = self.project_root_dir / ".project" / ".credentials"
        # Save the encrypted data to the file
        with open(credentials_path, "wb") as f:
            f.write(encrypted_data)

    def _check_duplicate_users(self, existing_users, new_user):
        if any(user['username'] == new_user['username'] for user in existing_users):
                    raise ValueError(f"User '{new_user['username']}' already exists")
        
    def _load_credentials(self):
        existing_users = []
        credentials_path = self.project_root_dir / ".project" / ".credentials"
        if credentials_path.exists():
            try:
                with open(credentials_path, "rb") as f:
                    encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                existing_users = json.loads(decrypted_data.decode())
                return existing_users
            except json.JSONDecodeError: # exption handling need refactoring -> propage errors to gui
                print("Error decoding user data.")
                return []
            except Exception as e:
                print(f"An error occurred: {e}")
                return []
        return existing_users

    def _initialize_key(self):
        key_path = self.project_root_dir / ".project" / ".key"
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
        
    def _create_captures_csv(self, project_dir):
        csv_file = project_dir / 'captures.csv'
        with csv_file.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'session', 'capturer', 'museum', 'order', 'family', 'genus', 'species', 'directory'])

    def _create_save_name(self, meta_info, capture_id, session):
        session_dir = Path(session['session_dir'])
        
        order_name = meta_info['Species Info']['Order'].replace(" ", "-").lower()
        species_name = f"{meta_info['Species Info']['Genus']}.{meta_info['Species Info']['Species']}".lower()
        
        img_name = session_dir / f"{session['name']}_cap-{capture_id:04d}_order-{order_name}_species-{species_name}.jpg"
        meta_name = img_name.with_suffix('.yml')
        
        return img_name, meta_name

    def _update_captures_csv(self, meta_info, session):
        csv_file = self.project_root_dir / 'captures.csv'
        with csv_file.open('a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                session['name'],
                session['capturer'],
                session['museum'],
                meta_info['Species Info']['Order'],
                meta_info['Species Info']['Family'],
                meta_info['Species Info']['Genus'],
                meta_info['Species Info']['Species'],
                session['captures'][-1]
            ])

    def _create_uuid_from_string(self, val: str):
        hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
        return str(uuid.UUID(hex=hex_string))

    def _create_string_from_dict_values(self, dict):
        return ''.join([value for value in dict.values()])

class DummyDB:
    def __init__(self):
        self.museums = [
            {'name': 'NHM', 'city': 'London', 'street': 'Kings Lane', 'number': '1'},
            {'name':'Senkenberg', 'city':'Frankfurt', 'street': 'Sachsen Strasse', 'number': '1'}
        ]
        self.users = [
            {'username': 'Peter', 'role': 'user', 'password': 'password1'},
            {'username': 'Seb', 'role': 'admin', 'password': 'password2'}
        ]
        self.current_user = None
        self.project_info = {}

    def create_session(self, payload):
        return {'Project Info': {}, 'Session': payload}

    def create_project(self, payload):
        if not payload:
            raise NotADirectoryError("Wrong request format.")
        else:
            self.project_info = payload
            return payload

    def load_project(self, project_dir):
        # Simulate loading a project
        self.project_info = {
            'Project Info': {'project_dir': project_dir, 'num_captures': 0},
            'Session 1': {'name': 'Sample Session', 'num_captures': 0}
        }
        return self.project_info

    def post_new_image(self, payload):
        print(payload)
        # Simulate updating capture counts
        self.project_info['Project Info']['num_captures'] += 1
        self.project_info['Session 1']['num_captures'] += 1
        return self.project_info

    def get_users(self):
        return [{'username': user['username'], 'role': user['role']} for user in self.users]

    def get_museums(self):
        return self.museums

    def get_museum(self, museum):
        for m in self.museums:
            if m['name'] == museum['name'] and m['city'] == museum['city']:
                return m

    def get_current_user(self):
        return self.current_user or {'username': 'Peter', 'role': 'user'}

    def add_museum(self, museum):
        self.museums.append(museum)
        return True

    def edit_museum(self, museum_to_edit, updated_museum):
        for m in self.museums:
            if m['name'] == museum_to_edit['name'] and m['city'] == museum_to_edit['city']:
                m['name'] = updated_museum['name']
                m['city'] = updated_museum['city']
                m['street'] = updated_museum['street']
                m['number'] = updated_museum['number']
                return True
        return False  

    def remove_museum(self, museum):
        for idx, m in enumerate(self.museums):
            if m['name'] == museum['name'] and m['city'] == museum['city']:
                self.museums.pop(idx)
                return True
        return False

    def reset_password(self, username, role, old_password, new_password):
        for user in self.users:
            if user['username'] == username and user['password'] == old_password:
                user['password'] = new_password
                return True
        return False

    def count_admins(self):
        return sum(1 for user in self.users if user['role'] == 'admin')

    def change_user_role(self, user_to_change, new_role):
        for user in self.users:
            if user['username'] == user_to_change:
                user['role'] = new_role
                return True
        return False

    def remove_user(self, user_to_remove):
        for idx, user in enumerate(self.users):
            if user['username'] == user_to_remove:
                self.users.pop(idx)
                return True
        return False

    def verify_credentials(self, username, password):
        for user in self.users:
            if user['username'] == username and user['password'] == password:
                self.current_user = {'username': user['username'], 'role': user['role']}
                return self.current_user
        return None

    def validate_admin(self, username, password):
        user = self.verify_credentials(username, password)
        return user and user['role'] == 'admin'

    def save_encrypted_users(self, new_user):
        if any(user['username'] == new_user['username'] for user in self.users):
            raise ValueError(f"User '{new_user['username']}' already exists")
        self.users.append(new_user)

    def update_project_config(self, section, options):
        if section not in self.project_info:
            self.project_info[section] = {}
        self.project_info[section].update(options)

    def write_project_config(self):
        # In a real implementation, this would write to a file
        pass

    def get_project_config(self):
        return self.project_info

    def load_image_and_meta_info(self, data):
        # Simulate loading image and meta info
        return {'image': 'dummy_image_data', 'meta_info': data}

    def create_save_name(self, meta_info):
        # Simulate creating save names
        return 'dummy_image_name.jpg', 'dummy_meta_name.yml'

    def add_exif_info(self, image, info):
        # Simulate adding EXIF info
        pass   