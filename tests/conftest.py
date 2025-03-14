from .MockHttpResponse import MockHttpResponse
from mlb_team_schedule import create_app

import pytest
import requests
from dotenv import find_dotenv, load_dotenv
from flask_migrate import downgrade, upgrade

#? `Conftest.py` is used by `pytest` to add reusable test fixtures
#? There isn't any way to share fixtures without `conftest` so beware `autouse` arg

#? Using basic `python-dotenv` rather than `pytest-dotenv` requires the following
#? 'session' scope ensures this test-wide fixture is the highest priority
#? `autouse` sets up the order of how fixtures run by setting up a dependency tree
@pytest.fixture(scope="session", autouse=True)
def load_env(): #? Find the right path to `/tests` & the env file
    env_file = find_dotenv(".env.tests")
    load_dotenv(env_file) #? Returns a bool indicating it successfully loaded the env file

@pytest.fixture
def app():
    # db_fd, db_path = tempfile.mkstemp() #? db_path links to temp db file

    app = create_app({ }) #* Passing an empty Dictionary ensures the TestConfig is used

    with app.app_context():
        upgrade() #? Setup test DB via migrations so can fill tables during tests
    # with app.test_client() as client:
        # yield client

    yield app

    # os.close(db_fd) #? Only purpose of db_fd is to close file/db
    # os.unlink(db_path)
    with app.app_context():
        downgrade(revision="base") #? FULL reset DB, dropping migrations/tables to 'base'


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

#? This fixtures fails ALL tests that try to run HTTP requests, so kinda useless
# @pytest.fixture(autouse=True)
# def no_requests(monkeypatch):
#     monkeypatch.delattr("requests.sessions.Session.request")

#? Example of a fixture that monkeypatches/mocks the `requests` library get() fetch func
@pytest.fixture
def mock_404_response(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockHttpResponse(404)

    monkeypatch.setattr(requests, "get", mock_get)
