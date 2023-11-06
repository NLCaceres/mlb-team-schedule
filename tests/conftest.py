import pytest
import requests
from dotenv import load_dotenv, find_dotenv
from flask_migrate import upgrade, downgrade
from .. import create_app
from .MockHttpResponse import MockHttpResponse

#? `Conftest.py` is used by `Pytest` to create fixtures that can be easily reused across all tests
#? Unfortunately, there isn't any other way to share fixtures across tests, so MUST be careful w/ 'autouse'

#? Using basic `python-dotenv` rather than `pytest-dotenv` requires the following
#? 'session' scope ensures this test-wide fixture is the highest priority
#? 'autouse' tells `pytest` to run this fixture first (configuring an order based on a dependency tree of fixtures)
@pytest.fixture(scope='session', autouse=True)
def load_env():
    env_file = find_dotenv('.env.tests') #? Finds the correct path to this 'tests' directory and its specific env file
    load_dotenv(env_file) #? Returns a boolean indicating it successfully loaded the env file

@pytest.fixture
def app():
    # db_fd, db_path = tempfile.mkstemp() #? db_path links to temp db file

    app = create_app({ }) #* Passing an empty Dictionary ensures the TestConfig is used

    with app.app_context():
        upgrade() #? Setup the test DB by running migrations so tables are created for tests to fill with mocks

    # with app.test_client() as client:
        # yield client

    yield app

    # os.close(db_fd) #? Only purpose of db_fd is to close file/db
    # os.unlink(db_path)
    with app.app_context():
        downgrade(revision='base') #? FULLY reset the DB by removing all migrations via 'base', so ALL tables are dropped


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

#? The following fixture comes at the cost of failing ALL tests that try to run HTTP requests making it kinda useless
# @pytest.fixture(autouse=True)
# def no_requests(monkeypatch):
#     monkeypatch.delattr("requests.sessions.Session.request")

#? Example of a fixture that monkeypatches/mocks the `requests` library get() fetch func
@pytest.fixture
def mock_404_response(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockHttpResponse(404)

    monkeypatch.setattr(requests, "get", mock_get)
