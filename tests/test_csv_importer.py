import pytest
import requests_mock
from requests_mock import Mocker

from aozora_data.importer.csv_importer import import_from_csv, import_from_csv_url
from aozora_data.db.firestore import AozoraFirestore

class FakeFirestore(AozoraFirestore):
    def __init__(self, project_id=None):
        # Skip super init to avoid creating real Client
        self.db = None
        self.batch_count = 0
        self.BATCH_LIMIT = 450

        self.existing_books = {}
        self.existing_persons = {}
        self.existing_contributors = set()

        # Memory checks for test assertions
        self.stored_books = {}
        self.stored_persons = {}
        self.stored_contributors = {} # Map ID -> Data

    def prefetch_metadata(self):
        pass

    def _flush_batch_if_needed(self, force: bool = False):
        pass

    def upsert_book(self, book_id: str, data: dict):
        self.stored_books[book_id] = data

    def upsert_person(self, person_id: str, data: dict):
        self.stored_persons[person_id] = data

    def upsert_contributor(self, contributor_id: str, data: dict):
        self.stored_contributors[contributor_id] = data
        self.existing_contributors.add(contributor_id)

    def commit(self):
        pass


@pytest.fixture()
def db():
    return FakeFirestore()


def test_import_from_csv(db: FakeFirestore):
    with open("tests/data/test.csv") as fp:
        import_from_csv(fp, db)

        assert len(db.stored_books) == 4

        # In the test CSV (assumed same as before), we check specific data
        book_id = "10001"
        person_id = "20001"

        # Ensure data is stored
        assert int(book_id) in [db.stored_books[k]['book_id'] for k in db.stored_books]
        # Our stored_books keys are string IDs from CSV, but values are typed.
        # Let's check based on the key
        assert book_id in db.stored_books
        book_data = db.stored_books[book_id]
        assert book_data['book_id'] == 10001

        # Person
        assert person_id in db.stored_persons
        person_data = db.stored_persons[person_id]
        assert person_data['person_id'] == 20001

        # Contributor
        # Contributor ID is composite: book-person-role
        # We need to find the one matching book_10001, person_20001
        # Role 1 is Translator in old Enum?
        # Let's check if there is a contributor for this pair
        found = False
        for cid, cdata in db.stored_contributors.items():
            if cdata['book_id'] == 10001 and cdata['person_id'] == 20001:
                found = True
                assert cdata['role'] == 1 # Translator
                break
        assert found


def test_import_from_csv_url(db: FakeFirestore, requests_mock: Mocker):
    csv_url = "http://test.csv.zip"
    with open("tests/data/test.csv.zip", "rb") as fp:
        requests_mock.get(csv_url, body=fp)
        import_from_csv_url(csv_url, db)

        assert len(db.stored_books) == 4

        book_id = "10003"
        person_id = "20003"

        assert book_id in db.stored_books
        book_data = db.stored_books[book_id]

        assert person_id in db.stored_persons
        person_data = db.stored_persons[person_id]

        # Check integrity
        assert book_data['book_id'] == 10003
        assert person_data['person_id'] == 20003


def test_import_from_csv_url_with_limit(db: FakeFirestore, requests_mock: Mocker):
    csv_url = "http://test.csv.zip"
    with open("tests/data/test.csv.zip", "rb") as fp:
        requests_mock.get(csv_url, body=fp)
        import_from_csv_url(csv_url, db, limit=2)

        assert len(db.stored_books) == 2
