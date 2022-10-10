import pytest

from aozora_data.importer.csv_importer import import_from_csv
from aozora_data.model import Book, Contributor, Person, Role


class FakeDB:
    def __init__(self):
        self.books: dict[int, Book] = {}
        self.persons: dict[int, Person] = {}
        self.contributors: list[Contributor] = []

    def get_book(self, book_id: int) -> Book | None:
        return self.books.get(book_id, None)

    def get_person(self, person_id: int) -> Person | None:
        return self.persons.get(person_id, None)

    def get_contributor(self, book_id, person_id) -> Contributor | None:
        for contributor in self.contributors:
            if contributor.book_id == book_id and contributor.person_id == person_id:
                return contributor
        return None

    def store_book(self, data: dict):
        book = Book(**data)
        self.books[book.book_id] = book

    def store_person(self, data: dict):
        person = Person(**data)
        self.persons[person.person_id] = person

    def store_contributor(self, data: dict):
        contributor = Contributor(**data)
        self.contributors.append(contributor)


@pytest.fixture()
def db():
    return FakeDB()


def test_import_from_csv(db: FakeDB, requests_mock):
    csv_url = "http://test.csv.zip"
    with open("tests/data/test.csv.zip", "rb") as fp:
        requests_mock.get(csv_url, body=fp)
        import_from_csv(csv_url, db)

        assert len(db.books) == 4

        book_id = 10003
        person_id = 20003

        book_03 = db.get_book(book_id)
        person_03 = db.get_person(person_id)
        contributor_03 = db.get_contributor(book_id, person_id)

        assert book_03.book_id == book_id
        assert person_03.person_id == person_id
        assert contributor_03.role == Role(0)

        assert len(db.persons) == 4
        assert len(db.contributors) == 4
