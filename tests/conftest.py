from .MockHttpResponse import MockHttpResponse
from mlb_team_schedule import create_app, db as sa

import pytest
import requests
from dotenv import find_dotenv, load_dotenv
from flask_migrate import downgrade, upgrade
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError
import os

#? `Conftest.py` is used by `pytest` to add reusable test fixtures
#? There isn't any way to share fixtures without `conftest` so beware `autouse` arg

#? Using basic `python-dotenv` rather than `pytest-dotenv` requires the following
#? 'session' scope ensures this test-wide fixture is the highest priority
#? `autouse` sets up the order of how fixtures run by setting up a dependency tree
@pytest.fixture(scope="session", autouse=True)
def load_env(): #? Find the right path to `/tests` & the env file
    env_file = find_dotenv(".env.tests")
    load_dotenv(env_file) #? Returns a bool indicating it successfully loaded the env file

@pytest.fixture(scope="session")
def database():
    url = make_url(os.environ["TEST_DATABASE_URL"])
    engine = create_engine(url, isolation_level="AUTOCOMMIT")
    rootURL = url._replace(database="postgres")
    rootEngine = create_engine(rootURL, isolation_level="AUTOCOMMIT")
    try:
        print(f"Trying to connect to database called = {url.database}")
        with engine.connect() as db:
            print(f"Found database called = {url.database}")
    except OperationalError:
        print(f"Creating new database called {url.database}")
        with rootEngine.begin() as db:
            statement = text(f"CREATE DATABASE {url.database} ENCODING 'utf8'")
            db.execute(statement)

    yield

    with rootEngine.begin() as db:
        print(f"Dropping database = {url.database}")
        statement = text(f"DROP DATABASE {url.database}")
        db.execute(statement)

@pytest.fixture
def app(database):
    # db_fd, db_path = tempfile.mkstemp() #? db_path links to temp db file

    os.environ["SECRET_KEY"] = f"{os.urandom(24)}"
    app = create_app({ }) #* Passing an empty Dictionary ensures the TestConfig is used
    app.config.from_mapping({"SECRET_KEY": os.environ["SECRET_KEY"]})

    with app.app_context():
        upgrade() #? Setup test DB via migrations so can fill tables during tests
    # with app.test_client() as client:
        # yield client

    yield app

    # os.close(db_fd) #? Only purpose of db_fd is to close file/db
    # os.unlink(db_path)
    with app.app_context():
        print("Downgrading and disposing")
        downgrade(revision="base") #? FULL reset DB, dropping migrations/tables to 'base'
        sa.engine.dispose() # Disconnect from DB. `upgrade` reforms connection later


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
