import pytest
from dotenv import load_dotenv, find_dotenv
from flask_migrate import upgrade, downgrade
from .. import create_app

#? `Conftest.py` is used by `Pytest` to create fixtures that can be easily reused across all tests

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

    app = create_app({}) #* Passing an empty Dictionary ensures the TestConfig is used

    with app.app_context():
        upgrade() #? Setup TestDB by creating the tables then running migrations on them

    # with app.test_client() as client:
        # yield client

    yield app

    # os.close(db_fd) #? Only purpose of db_fd is to close file/db
    # os.unlink(db_path)
    with app.app_context():
        downgrade() #? Reset the TestDB by removing the migrations and deleting the tables


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
