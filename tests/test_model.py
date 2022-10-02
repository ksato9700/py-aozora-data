import json
from datetime import date

import pytest
from pydantic import ValidationError

from aozora_data.model import Book, Contributor, Person, Role, Worker


def test_contributor():
    # normal case
    for idx, role_str in enumerate(("著者", "翻訳者", "編者", "校訂者", "その他")):
        contributor_data = {
            "book_id": 10000 + idx,
            "person_id": 20000 + idx,
            "role": role_str,
        }
        contributor = Contributor(**contributor_data)
        assert contributor.book_id == contributor_data["book_id"]
        assert contributor.person_id == contributor_data["person_id"]
        assert contributor.role == Role(idx)

    # reimport case
    contributor_data = {"book_id": 30000, "person_id": 40000, "role": "著者"}
    contributor_0 = Contributor(**contributor_data)
    contributor_1 = Contributor(**(contributor_0.dict()))
    assert contributor_0 == contributor_1

    # initialize by integer
    contributor_data = {"book_id": 30000, "person_id": 40000, "role": 3}
    contributor = Contributor(**contributor_data)
    assert contributor.role == Role.REVISOR

    # invalid case
    contributor_data = {"book_id": 30000, "person_id": 40000, "role": "画家"}
    with pytest.raises(ValidationError) as error:
        Contributor(**contributor_data)

    assert (
        str(error.value)
        == "1 validation error for Contributor\nrole\n  画家 (type=value_error)"
    )

    contributor_data = {"book_id": 30000, "person_id": 40000, "role": 10}
    with pytest.raises(ValidationError) as error:
        Contributor(**contributor_data)

    assert (
        str(error.value)
        == "1 validation error for Contributor\nrole\n  10 (type=value_error)"
    )


@pytest.fixture()
def input_data():
    with open("tests/data/010003.json") as fp:
        return json.load(fp)


def test_model(input_data: dict):
    book = Book(**input_data)
    person = Person(**input_data)

    book_str_keys = (
        "base_book_1",
        "base_book_1_1st_edition",
        "base_book_1_edition_input",
        "base_book_1_edition_proofing",
        "base_book_1_parent",
        "base_book_1_parent_1st_edition",
        "base_book_1_parent_publisher",
        "base_book_1_publisher",
        "base_book_2",
        "base_book_2_1st_edition",
        "base_book_2_edition_input",
        "base_book_2_edition_proofing",
        "base_book_2_parent",
        "base_book_2_parent_1st_edition",
        "base_book_2_parent_publisher",
        "base_book_2_publisher",
        "card_url",
        "first_appearance",
        "font_kana_type",
        "html_charset",
        "html_encoding",
        "html_url",
        "input",
        "ndc_code",
        "original_title",
        "proofing",
        "subtitle",
        "subtitle_yomi",
        "text_charset",
        "text_encoding",
        "text_url",
        "title",
        "title_sort",
        "title_yomi",
    )
    book_int_keys = (
        "book_id",
        "text_updated",
        "html_updated",
    )
    book_date_keys = (
        "html_last_modified",
        "release_date",
        "last_modified",
        "text_last_modified",
    )
    book_bool_keys = ("copyright",)
    person_str_keys = (
        "date_of_birth",
        "date_of_death",
        "first_name",
        "first_name_roman",
        "first_name_sort",
        "first_name_yomi",
        "last_name",
        "last_name_roman",
        "last_name_sort",
        "last_name_yomi",
    )
    person_int_keys = ("person_id",)
    person_bool_keys = ("author_copyright",)

    for key in book_str_keys:
        assert getattr(book, key) == input_data[key]

    for key in book_int_keys:
        assert getattr(book, key) == int(input_data[key])

    for key in book_date_keys:
        assert getattr(book, key) == date.fromisoformat(input_data[key])

    for key in book_bool_keys:
        assert getattr(book, key) == (input_data[key] != "なし")

    for key in person_str_keys:
        assert getattr(person, key) == input_data[key]

    for key in person_int_keys:
        assert getattr(person, key) == int(input_data[key])

    for key in person_bool_keys:
        assert getattr(person, key) == (input_data[key] != "なし")

    assert set(
        book_str_keys
        + book_int_keys
        + book_date_keys
        + book_bool_keys
        + person_str_keys
        + person_int_keys
        + person_bool_keys
        + ("role",)
    ) == set(input_data.keys())

    # reimport case

    book2 = Book(**book.dict())
    assert book == book2

    person2 = Person(**person.dict())
    assert person == person2


def test_worker():
    data = {"worker_id": 1, "name": "worker_001"}
    worker = Worker(**data)
    assert worker.worker_id == data["worker_id"]
    assert worker.name == data["name"]

    worker2 = Worker(**worker.dict())
    assert worker == worker2
