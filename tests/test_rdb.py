import json

import pytest

from aozora_data.db.db_rdb import DB
from aozora_data.model import Book, Contributor, Person, Worker


@pytest.fixture()
def input_data():
    with open("tests/data/010003.json") as fp:
        return json.load(fp)


def adb():
    with open("tests/data/adb.json") as fp:
        return json.load(fp)


def test_rdb_book(input_data: dict):
    db = DB()

    book_id = input_data["book_id"]

    book_0 = Book(**input_data)
    db.store_book(book_0.dict())
    book_1 = db.get_book(book_id)

    assert book_0 == book_1


def test_rdb_books(input_data: dict):
    db = DB()

    book_id = input_data["book_id"]

    book_0 = Book(**input_data)
    db.store_book(book_0.dict())
    book_1 = db.get_book(book_id)

    assert book_0 == book_1


def test_rdb_person(input_data: dict):
    db = DB()

    person_id = input_data["person_id"]

    person_0 = Person(**input_data)
    db.store_person(person_0.dict())
    person_1 = db.get_person(person_id)

    assert person_0 == person_1


def test_rdb_contributor(input_data: dict):
    db = DB()

    book_id = input_data["book_id"]
    person_id = input_data["person_id"]

    contributor_0 = Contributor(**input_data)
    db.store_contributor(contributor_0.dict())
    contributor_1 = db.get_contributor(book_id, person_id)

    assert contributor_0 == contributor_1


def test_rdb_worker():
    db = DB()

    input_data = {"worker_id": 1, "name": "worker_001"}
    worker_id = input_data["worker_id"]

    worker_0 = Worker(**input_data)
    db.store_worker(worker_0.dict())
    worker_1 = db.get_worker(worker_id)

    assert worker_0 == worker_1


def test_rdb_error(input_data: dict):
    db = DB()

    book = db.get_book(99999)
    assert book is None

    person = db.get_person(99999)
    assert person is None

    contributor = db.get_contributor(99999, 99999)
    assert contributor is None

    worker = db.get_worker(99999)
    assert worker is None
