import logging
from csv import DictReader
from io import BytesIO, StringIO
from typing import TextIO
from zipfile import ZipFile

import requests

from ..db.db_rdb import DB
from ..model import Book, Contributor, Person

logger = logging.getLogger(__name__)

FIELD_NAMES = (
    "book_id",
    "title",
    "title_yomi",
    "title_sort",
    "subtitle",
    "subtitle_yomi",
    "original_title",
    "first_appearance",
    "ndc_code",
    "font_kana_type",
    "copyright",
    "release_date",
    "last_modified",
    "card_url",
    "person_id",
    "last_name",
    "first_name",
    "last_name_yomi",
    "first_name_yomi",
    "last_name_sort",
    "first_name_sort",
    "last_name_roman",
    "first_name_roman",
    "role",
    "date_of_birth",
    "date_of_death",
    "author_copyright",
    "base_book_1",
    "base_book_1_publisher",
    "base_book_1_1st_edition",
    "base_book_1_edition_input",
    "base_book_1_edition_proofing",
    "base_book_1_parent",
    "base_book_1_parent_publisher",
    "base_book_1_parent_1st_edition",
    "base_book_2",
    "base_book_2_publisher",
    "base_book_2_1st_edition",
    "base_book_2_edition_input",
    "base_book_2_edition_proofing",
    "base_book_2_parent",
    "base_book_2_parent_publisher",
    "base_book_2_parent_1st_edition",
    "input",
    "proofing",
    "text_url",
    "text_last_modified",
    "text_encoding",
    "text_charset",
    "text_updated",
    "html_url",
    "html_last_modified",
    "html_encoding",
    "html_charset",
    "html_updated",
)


def import_from_csv_url(csv_url: str, db: DB, limit: int = 0) -> TextIO:
    """Import books, persons, and contributors from a CSV file URL."""
    resp = requests.get(csv_url)
    resp.raise_for_status()
    with ZipFile(BytesIO(resp.content)) as zipfile:
        stream = StringIO(zipfile.read(zipfile.namelist()[0]).decode("utf-8-sig"))
        return import_from_csv(stream, db, limit)


def import_from_csv(csv_stream: TextIO, db: DB, limit: int = 0):
    """Import books, persons, and contributors from a CSV file."""
    csv_obj = DictReader(csv_stream, fieldnames=FIELD_NAMES)

    logger.debug(csv_obj)
    next(csv_obj)  # skip the first row

    for idx, row in enumerate(csv_obj):
        if limit > 0 and idx >= limit:
            break
        try:
            db.store_book(Book(**row).model_dump())
            db.store_person(Person(**row).model_dump())
            db.store_contributor(Contributor(**row).model_dump())
        except Exception as e:
            print(f"ERROR: {e}")
            print(row)
            raise
