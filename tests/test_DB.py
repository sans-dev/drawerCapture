import pytest
import numpy as np
from configparser import ConfigParser
from src.db.DB import FileAgnosticDB

@pytest.fixture
def file_agnostic_db(tmp_path):
    db = FileAgnosticDB()
    project_dir = tmp_path / "test"
    project_dir.mkdir()
    test_info = {}
    test_info['Project Info'] = {
            'num_captures': 0}
    
    db.create_project(test_info, project_dir=project_dir)
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
        assert conf.getint('Test', 'Test1') == 1

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
        assert conf.getint(session_name, 'num_captures') == 1
        assert conf.getint("Project Info", 'num_captures') == 1