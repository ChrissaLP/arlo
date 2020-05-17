import datetime
import pytest
import uuid
from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError

import arlo_server
from arlo_server.models import File
from util.process_file import process_file


@pytest.fixture(scope="session")
def db():
    with arlo_server.app.app_context():
        #        arlo_server.db.drop_all()
        arlo_server.db.create_all()

    yield arlo_server.db


#    arlo_server.db.session.rollback()


@pytest.fixture(scope="function")
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


def test_success(session):
    file = File(
        id=str(uuid.uuid4()),
        name="Test File",
        contents="abcdefg",
        uploaded_at=datetime.datetime.utcnow(),
    )
    session.add(file)
    session.commit()

    def process():
        pass

    assert file.processing_started_at is None
    assert file.processing_completed_at is None
    assert file.processing_error is None

    process_file(session, file, process)

    assert isinstance(file.processing_started_at, datetime.datetime)
    assert isinstance(file.processing_completed_at, datetime.datetime)
    assert file.processing_error is None


def test_error(session):
    file = File(
        id=str(uuid.uuid4()),
        name="Test File",
        contents="abcdefg",
        uploaded_at=datetime.datetime.utcnow(),
    )
    session.add(file)
    session.commit()

    def process():
        raise Exception("NOPE")

    assert file.processing_started_at is None
    assert file.processing_completed_at is None
    assert file.processing_error is None

    try:
        process_file(session, file, process)
    except Exception as error:
        assert str(error) == "NOPE"

    assert isinstance(file.processing_started_at, datetime.datetime)
    assert isinstance(file.processing_completed_at, datetime.datetime)
    assert file.processing_error == "NOPE"


def test_session_stuck(session):
    file = File(
        id=str(uuid.uuid4()),
        name="Test File",
        contents="abcdefg",
        uploaded_at=datetime.datetime.utcnow(),
    )
    session.add(file)
    session.commit()

    def process():
        # We do something here that renders a db session unable to commit,
        # specifically trying to violate a db constraint. Note that we're not
        # using the models here because doing so makes sqlalchemy notice the
        # conflict before it even gets to the db.
        session.execute(
            insert(File.__table__).values(
                id=file.id,
                name="Test File2",
                contents="abcdefg",
                uploaded_at=datetime.datetime.utcnow(),
            )
        )

    try:
        process_file(session, file, process)
    except SQLAlchemyError as error:
        pass

    assert isinstance(file.processing_started_at, datetime.datetime)
    assert isinstance(file.processing_completed_at, datetime.datetime)
