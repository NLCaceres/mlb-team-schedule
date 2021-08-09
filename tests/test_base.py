import os
import tempfile

import pytest

from DodgersPromo import create_app

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp() #? db_path links to temp db file
    app = create_app({'TESTING': True, 'DATABASE': db_path})

    with app.test_client() as client:
        # with app.app_context():
            # init_db()
        yield client

    os.close(db_fd) #? Only purpose of db_fd is to close file/db
    os.unlink(db_path)