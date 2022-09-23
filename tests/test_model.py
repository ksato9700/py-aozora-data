import json
from datetime import date

import pytest
from db_import.model import Book, Person


@pytest.fixture()
def book_data():
    with open("tests/data/book_059898.json") as fp:
        return json.load(fp)


def test_import_from_csv(book_data: dict):
    book = Book(**book_data)
    person = Person(**book_data)

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
        assert getattr(book, key) == book_data[key]

    for key in book_int_keys:
        assert getattr(book, key) == int(book_data[key])

    for key in book_date_keys:
        assert getattr(book, key) == date.fromisoformat(book_data[key])

    for key in book_bool_keys:
        assert getattr(book, key) == (book_data[key] != "なし")

    for key in person_str_keys:
        assert getattr(person, key) == book_data[key]

    for key in person_int_keys:
        assert getattr(person, key) == int(book_data[key])

    for key in person_bool_keys:
        assert getattr(person, key) == (book_data[key] != "なし")

    assert set(
        book_str_keys
        + book_int_keys
        + book_date_keys
        + book_bool_keys
        + person_str_keys
        + person_int_keys
        + person_bool_keys
        + ("role",)
    ) == set(book_data.keys())
