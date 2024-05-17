import pytest
import numpy as np
from configparser import ConfigParser
from src.db.DB import FileAgnosticDB, DBAdapter, DummyDB

@pytest.fixture
def project_dict(tmp_path):
    project_dir = tmp_path / "test"
    config = dict()
    config['Project Info'] = {
            'project_dir' : str(project_dir),
            'num_captures': 0,
            'name' : 'foo',
            'description' : 'bar',
            'date' : '2020-01-01',
            'authors' : 'baz',
    }
    return config

@pytest.fixture
def agnostic_project_dir(tmp_path):
    project_dir = tmp_path / "test"
    project_dir.mkdir()
    config = dict()
    # create project ini
    config['Project Info'] = {
            'project_dir' : str(project_dir),
            'num_captures': 0,
            'name' : 'foo',
            'description' : 'bar',
            'date' : '2020-01-01',
            'authors' : 'baz',
    }
    db = FileAgnosticDB()
    db.create_project(config)
    return project_dir

@pytest.fixture
def file_agnostic_db(tmp_path):
    db = FileAgnosticDB()
    project_dir = tmp_path / "test"
    project_dir.mkdir()
    test_info = {}
    test_info['Project Info'] = {
            'project_dir' : str(project_dir),
            'num_captures': 0}
    
    db.create_project(test_info)
    return db

@pytest.fixture
def dummy_img():
    img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    return img_array

@pytest.fixture
def dummy_meta():
    meta_infos = {}
    meta_infos = {
            'Order': "Test",
            'Family': "Test2",
            'Museum': 'test',
            'Species': 'species'}
    return meta_infos

@pytest.fixture
def corrupted_dummy_img():
    pass

@pytest.fixture
def dummy_post(dummy_img, dummy_meta):
    post = {}
    post['image'] = dummy_img
    post['meta_info'] = dummy_meta
    return post

@pytest.fixture
def dummy_session():
    session_name = "Session 1"
    session_data = {
        "id": 1,
        "num_captures" : 0
    }
    return session_name, session_data

class TestFileAgnosticDB:
    def test_update_project_config(self, file_agnostic_db):
        file_agnostic_db.update_project_config("Test", options={"Test1": 3})
        conf = file_agnostic_db.get_project_config()
        assert conf.getint('Test', 'Test1') == 3

    def test_write_project_config(self, file_agnostic_db):
        project_dir = file_agnostic_db.project_root_dir
        file_agnostic_db.write_project_config()
        conf = ConfigParser()
        conf.read(project_dir / "project.ini")
        assert conf.getint('Project Info', 'num_captures') == 0

    def test_ceate_session(self, file_agnostic_db, dummy_session):
        session_name, session_data = dummy_session
        file_agnostic_db.create_session(session_name, session_data)
        conf = file_agnostic_db.get_project_config()
        assert conf.getint(session_name, 'num_captures') == 0
        assert conf.getint(session_name, 'id') == 1

    def test_post_new_image(self, file_agnostic_db, dummy_post, dummy_session):
        session_name, session_data = dummy_session
        file_agnostic_db.create_session(session_name, session_data)
        file_agnostic_db.post_new_image(dummy_post)
        conf = file_agnostic_db.get_project_config()
        img_name, meta_name = file_agnostic_db.create_save_name(dummy_post['meta_info'])
        assert img_name.is_file()
        assert meta_name.is_file()
        assert conf.getint(session_name, 'num_captures') == 1
        assert conf.getint("Project Info", 'num_captures') == 1
        
    def test_post_image_fail(self, file_agnostic_db, dummy_post, dummy_session):
        session_name, session_data = dummy_session
        file_agnostic_db.create_session(session_name, session_data)
        file_agnostic_db.project_root_dir = ""
        with pytest.raises(TypeError):
            file_agnostic_db.post_new_image(dummy_post)
        
    def test_load_project(self, agnostic_project_dir):
        db = FileAgnosticDB()
        db.load_project(agnostic_project_dir)
        conf = db.get_project_config()
        assert conf.getint('Project Info', 'num_captures') == 0
        assert conf.get("Project Info", "date") == "2020-01-01"
        assert conf.get("Project Info", "authors") == "baz"
        assert conf.get("Project Info", "name") == "foo"
        assert conf.get("Project Info", "description") == "bar"
    
    def test_load_project_with_session(self, agnostic_project_dir, dummy_session):
        db = FileAgnosticDB()
        db.load_project(agnostic_project_dir)
        db.create_session(dummy_session[0], dummy_session[1])
        conf = db.get_project_config()
        assert conf.getint('Project Info', 'num_captures') == 0
        assert conf.get("Project Info", "date") == "2020-01-01"
        assert conf.get("Project Info", "authors") == "baz"
        assert conf.get("Project Info", "name") == "foo"
        assert conf.get("Project Info", "description") == "bar"
        assert conf.getint(dummy_session[0], 'num_captures') == 0
        assert conf.getint(dummy_session[0], 'id') == 1
        
class TestDBAdapter:
    def test_create_project(self, project_dict):
        adapter = DBAdapter(DummyDB())
        response = adapter.create_project(project_dict)
        assert response['Project Info']['name'] == project_dict['Project Info']['name']
        assert response['Project Info']['date'] == project_dict['Project Info']['date']
        with pytest.raises(NotADirectoryError):
            response = adapter.create_project(None)




