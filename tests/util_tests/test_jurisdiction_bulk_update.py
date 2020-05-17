from util.jurisdiction_bulk_update import bulk_update_jurisdictions
from arlo_server.models import (
    Election,
    Jurisdiction,
    JurisdictionAdministration,
    Organization,
    User,
)
import arlo_server
import pytest
import uuid


@pytest.fixture(scope="session")
def db():
    with arlo_server.app.app_context():
        # arlo_server.db.drop_all()
        arlo_server.db.create_all()

    yield arlo_server.db

    # arlo_server.db.session.rollback()


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


def test_first_update(session):
    org = Organization(id=str(uuid.uuid4()), name="Test Org")
    election = Election(
        id=str(uuid.uuid4()),
        audit_name="Test Audit",
        organization=org,
        is_multi_jurisdiction=True,
    )
    new_admins = bulk_update_jurisdictions(
        session, election, [("Jurisdiction #1", "bob.harris@ca.gov")]
    )
    session.commit()

    assert [(admin.jurisdiction.name, admin.user.email) for admin in new_admins] == [
        ("Jurisdiction #1", "bob.harris@ca.gov")
    ]

    assert User.query.count() == 1
    assert Jurisdiction.query.count() == 1
    assert JurisdictionAdministration.query.count() == 1


def test_idempotent(session):
    org = Organization(id=str(uuid.uuid4()), name="Test Org")
    election = Election(
        id=str(uuid.uuid4()),
        audit_name="Test Audit",
        organization=org,
        is_multi_jurisdiction=True,
    )

    # Do it once.
    bulk_update_jurisdictions(
        session, election, [("Jurisdiction #1", "bob.harris@ca.gov")]
    )
    session.commit()

    user = User.query.one()
    jurisdiction = Jurisdiction.query.one()

    # Do the same thing again.
    bulk_update_jurisdictions(
        session, election, [("Jurisdiction #1", "bob.harris@ca.gov")]
    )

    assert User.query.one() == user
    assert Jurisdiction.query.one() == jurisdiction


def test_remove_outdated_jurisdictions(session):
    org = Organization(id=str(uuid.uuid4()), name="Test Org")
    election = Election(
        id=str(uuid.uuid4()),
        audit_name="Test Audit",
        organization=org,
        is_multi_jurisdiction=True,
    )

    # Add jurisdictions.
    bulk_update_jurisdictions(
        session, election, [("Jurisdiction #1", "bob.harris@ca.gov")]
    )
    session.commit()

    # Delete jurisdictions.
    new_admins = bulk_update_jurisdictions(session, election, [])

    assert new_admins == []
    assert User.query.count() == 1  # keep the user
    assert Jurisdiction.query.count() == 0
    assert JurisdictionAdministration.query.count() == 0
