import logging
from csv import DictReader
from io import BytesIO, StringIO
from zipfile import ZipFile

import requests

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

# CSV_URL = "https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip"
CSV_URL = "http://localhost:9000/list_person_all_extended_utf8.zip"
# CSV_URL = "http://localhost:9000/xx.zip"


def _get_csv(data: bytes) -> DictReader:
    with ZipFile(BytesIO(data)) as zipfile:
        csv_data: str = zipfile.read(zipfile.namelist()[0]).decode("utf-8-sig")
        return DictReader(
            StringIO(csv_data),
            fieldnames=FIELD_NAMES,
        )


def import_from_csv(db):
    resp = requests.get(CSV_URL)
    resp.raise_for_status()

    csv_obj: DictReader = _get_csv(resp.content)
    logger.debug(csv_obj)
    next(csv_obj)  # skip the first row

    for row in csv_obj:
        try:
            db.store_book(Book(**row).dict())
            db.store_person(Person(**row).dict())
            db.store_contributor(Contributor(**row).dict())
        except Exception as e:
            print(f"ERROR: {e}")
            print(row)
            raise
