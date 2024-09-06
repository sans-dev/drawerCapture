import pytest
import numpy as np
import json
from src.db.DB import FileAgnosticDB, DBAdapter, DummyDB

museum_data = {
    "name": "Senkenberg",
    "city": "Frankfurt",
    "street": "Senckenberganlage",
    "number": "25",
}

session_data = {
    "Session Name" : None,
    "Capturer": 'Thomas',
    "Museum": 'Senkenberg',
    "Collection Name": "Insects",
    'Captures': []
}

project_config ={
        'project_dir': None,
        'num_captures': 0,
        'name': 'foo',
        'description': 'bar',
        'date': '2020-01-01',
        'authors': 'baz'}

@pytest.fixture
def dummy_meta():
    return {
        "sessionName": "session-01",
        "collectionName": "Insect of Afrika",
        "order": "Burdi",
        "family": "Burdeae",
        "genus": "Burdus",
        "species": "Burdus burdulus",
        "museum": "Senkenberg - Frankfurt",
        "capturer": "Toni",
        "directory": "path/to/file.jpg",
        "timestap": None,
        "sessionDir": "dir/to/session/",
        "captureID": 1
    }

@pytest.fixture
def project_dict(tmp_path):
    db = FileAgnosticDB()
    project_config['project_dir'] = str(tmp_path / project_config['name'])
    config = db.create_project(project_config)
    return config

@pytest.fixture
def agnostic_project_dir(tmp_path):
    db = FileAgnosticDB()
    project_config['project_dir'] = str(tmp_path)
    db.create_project(project_config)
    config = db.create_project(project_config)
    return config['project_dir']

@pytest.fixture
def file_agnostic_db(tmp_path):
    db = FileAgnosticDB()
    project_config['project_dir'] = str(tmp_path / project_config['name'])
    db.create_project(project_config)
    return db

@pytest.fixture
def dummy_img():
    img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    return img_array

@pytest.fixture
def dummy_img_dir():
    return 'tests/data/test_img.jpg'



@pytest.fixture
def corrupted_dummy_img():
    pass

@pytest.fixture
def dummy_post(dummy_img_dir, dummy_meta):
    post = {}
    post['img_dir'] = dummy_img_dir
    post['meta_info'] = dummy_meta
    return post

class TestFileAgnosticDB:

    def test_db_creation(self):
        db = FileAgnosticDB()
        assert db is not None

    def test_create_project(self, tmp_path):
        db = FileAgnosticDB()
        project_config['project_dir'] = str(tmp_path)
        config = db.create_project(project_config)
        assert config['project_dir'] == str(tmp_path)
        assert config['num_captures'] == '0'
        assert config['name'] == 'foo'
        assert config['description'] == 'bar'
        assert config['date'] == '2020-01-01'
        assert config['authors'] == 'baz'

    def test_ceate_session(self, file_agnostic_db):
        session_id, _session_data = file_agnostic_db.create_session(session_data)
        assert _session_data['name'] == 'session-001'
        assert _session_data['capturer'] == session_data['capturer']
        assert _session_data['museum'] == session_data['museum']
        assert _session_data['collection_name'] == session_data['collection_name']
        assert _session_data['num_captures'] == 0
        assert _session_data['session_dir'] == (file_agnostic_db.project_root_dir / 'captures' / f"{session_data['name']}").as_posix()
        assert session_id is not None


    def test_create_save_name(self, file_agnostic_db, dummy_meta):
        img_name, meta_name = file_agnostic_db._create_save_name(dummy_meta)

    def test_post_new_image(self, file_agnostic_db, dummy_post):
        sessions = file_agnostic_db.create_session(session_data)
        sid = list(sessions.keys())[-1]
        dummy_post['sid'] = sid
        file_agnostic_db.post_new_image(dummy_post)
        
    def test_post_image_fail(self, file_agnostic_db, dummy_post):
        file_agnostic_db.create_session(session_data)
        file_agnostic_db.project_root_dir = ""
        with pytest.raises(TypeError):
            file_agnostic_db.post_new_image(dummy_post)
        
    def test_load_project(self, agnostic_project_dir):
        db = FileAgnosticDB()
        db.load_project(agnostic_project_dir)
        conf = db.get_project_info()
        assert conf['num_captures'] == '0'
        assert conf['name'] == 'foo'
        assert conf['description'] == 'bar'
        assert conf['date'] == '2020-01-01'
        assert conf['authors'] == 'baz'
    
    def test_load_project_with_session(self, agnostic_project_dir):
        # TODO refactor to loading project with a session
        db = FileAgnosticDB()
        db.load_project(agnostic_project_dir)
        db.create_session(session_data)
        
    def test_add_museum(self, agnostic_project_dir):
        db = FileAgnosticDB()
        db.load_project(agnostic_project_dir)
        with pytest.raises(ValueError):
            db.add_museum('test')
        db.add_museum(museum_data)
        museums = db.get_museums()

    def test_get_ccv_header(self):
        csv_header = FileAgnosticDB._get_csv_header()

    def test_update_captures_csv(self, file_agnostic_db, dummy_meta):
        file_agnostic_db._update_captures_csv(dummy_meta)
        dummy_meta['collectionName'] = None
        file_agnostic_db._update_captures_csv(dummy_meta)

class TestDBAdapter:
    def test_create_project(self, project_dict):
        adapter = DBAdapter(DummyDB())
        response = adapter.create_project(project_dict)
        assert response['name'] == project_dict['name']
        assert response['date'] == project_dict['date']
        with pytest.raises(NotADirectoryError):
            response = adapter.create_project(None)




