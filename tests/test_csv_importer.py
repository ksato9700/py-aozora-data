import pytest

imporet requests
from ..db_import.importer.csv_importer import import_from_csv


class TestDB:
    def __init__(self):
        self.books = {}
        self.persons = {}
        self.contributors = []

    def store_book(self, data: dict):
        self.books[data["book_id"]] = data

    def store_person(self, data: dict):
        self.persons[data["person_id"]] = data

    def store_contributor(self, data: dict):
        self.contributors.append(data)

@pytest.fixture()
def db():
    return TestDB()


def test_import_from_csv(db: TestDB):
    csv_url = "file:///"
    import_from_csv(csv_url, db)
