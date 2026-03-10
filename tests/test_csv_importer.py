import pytest
from requests_mock import Mocker

from aozora_data.db.firestore import AozoraFirestore
from aozora_data.importer.csv_importer import import_from_csv, import_from_csv_url


class FakeFirestore(AozoraFirestore):
    def __init__(self, project_id: str | None = None) -> None:
        # Skip super init to avoid creating real Client
        self.db = None
        self.batch_count = 0
        self.BATCH_LIMIT = 450

        self.watermark: str | None = None

        # Memory checks for test assertions
        self.stored_books: dict[str, dict] = {}
        self.stored_persons: dict[str, dict] = {}
        self.stored_contributors: dict[str, dict] = {}  # Map ID -> Data

    def get_watermark(self) -> str | None:
        return self.watermark

    def save_watermark(self, date_str: str) -> None:
        self.watermark = date_str

    def _flush_batch_if_needed(self, force: bool = False) -> None:
        pass

    def upsert_book(self, book_id: str, data: dict):
        self.stored_books[book_id] = data

    def upsert_person(self, person_id: str, data: dict):
        self.stored_persons[person_id] = data

    def upsert_contributor(self, contributor_id: str, data: dict):
        self.stored_contributors[contributor_id] = data

    def update_book_author(self, book_id: str, data: dict):
        if book_id in self.stored_books:
            self.stored_books[book_id].update(data)
        else:
            self.stored_books[book_id] = data

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
        assert int(book_id) in [db.stored_books[k]["book_id"] for k in db.stored_books]
        # Our stored_books keys are string IDs from CSV, but values are typed.
        # Let's check based on the key
        assert book_id in db.stored_books
        book_data = db.stored_books[book_id]
        assert book_data["book_id"] == 10001

        # Person
        assert person_id in db.stored_persons
        person_data = db.stored_persons[person_id]
        assert person_data["person_id"] == 20001

        # Contributor
        # Contributor ID is composite: book-person-role
        # We need to find the one matching book_10001, person_20001
        # Role 1 is Translator in old Enum?
        # Let's check if there is a contributor for this pair
        found = False
        for _cid, cdata in db.stored_contributors.items():
            if cdata["book_id"] == 10001 and cdata["person_id"] == 20001:
                found = True
                assert cdata["role"] == 1  # Translator
                break
        assert found

        # Author denormalization
        # book 10003 has 著者 (role 0) — primary author stored directly
        assert db.stored_books["10003"]["author_name"] == "last_name_03 first_name_03"
        assert db.stored_books["10003"]["author_id"] == 20003

        # book 10001 has 翻訳者 (role 1) only — falls back to first contributor
        assert db.stored_books["10001"]["author_name"] == "last_name_01 first_name_01"
        assert db.stored_books["10001"]["author_id"] == 20001

        # book 10000 has 編者 (role 2) only — falls back to first contributor
        assert db.stored_books["10000"]["author_name"] == "last_name_00 first_name_00"
        assert db.stored_books["10000"]["author_id"] == 20000

        # book 10002 has 校訂者 (role 3) only — falls back to first contributor
        assert db.stored_books["10002"]["author_name"] == "last_name_02 first_name_02"
        assert db.stored_books["10002"]["author_id"] == 20002


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
        assert book_data["book_id"] == 10003
        assert person_data["person_id"] == 20003


def test_import_from_csv_url_with_limit(db: FakeFirestore, requests_mock: Mocker):
    csv_url = "http://test.csv.zip"
    with open("tests/data/test.csv.zip", "rb") as fp:
        requests_mock.get(csv_url, body=fp)
        import_from_csv_url(csv_url, db, limit=2)

        assert len(db.stored_books) == 2
