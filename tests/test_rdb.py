import json

import pytest
from db_import.db.db_rdb import DB
from db_import.model import Book, Contributor, Person


@pytest.fixture()
def input_data():
    with open("tests/data/010003.json") as fp:
        return json.load(fp)


def test_rdb(input_data: dict):
    db = DB()

    book_id = 10003
    person_id = 20003

    book_0 = Book(**input_data)
    db.store_book(book_0.dict())
    book_1 = db.get_book(book_id)

    assert book_0 == book_1

    person_0 = Person(**input_data)
    db.store_person(person_0.dict())
    person_1 = db.get_person(person_id)

    assert person_0 == person_1

    contributor_0 = Contributor(**input_data)
    db.store_contributor(contributor_0.dict())
    contributor_1 = db.get_contributor(book_id, person_id)

    assert contributor_0 == contributor_1


def test_rdb_error(input_data: dict):
    db = DB()

    book_id = 20003
    person_id = 30003

    book = db.get_book(book_id)
    assert book == None

    person = db.get_person(person_id)
    assert person == None

    contributor = db.get_contributor(book_id, person_id)
    assert contributor == None
