import logging
import datetime
from csv import DictReader
from io import BytesIO, StringIO
from typing import TextIO, Any, Dict, Set

import requests

from ..db.firestore import AozoraFirestore

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


def _parse_date(val: str) -> str | None:
    """Return date string as is, or None if empty."""
    # Firestore can store strings or datetime objects.
    # The CSV date format is typically YYYY-MM-DD.
    return val if val else None


def _parse_int(val: str) -> int:
    return int(val) if val else 0


def _parse_bool(val: str) -> bool:
    return val != "なし"


def _parse_role(val: str) -> int:
    # Map Japanese roles to IDs manually if needed, or just store the string?
    # Original model.py had Mapping.
    # AUTHOR = 0, TRANSLATOR = 1, EDITOR = 2, REVISOR = 3, OTHER = 4
    if val == "著者": return 0
    if val == "翻訳者": return 1
    if val == "編者": return 2
    if val == "校訂者": return 3
    if val == "その他": return 4
    return 4


def import_from_csv_url(csv_url: str, db: AozoraFirestore, limit: int = 0) -> None:
    """Import books, persons, and contributors from a CSV file URL."""
    resp = requests.get(csv_url)
    resp.raise_for_status()
    with BytesIO(resp.content) as b_stream:
        # Handling zip files in memory
        from zipfile import ZipFile
        with ZipFile(b_stream) as zipfile:
            # Assuming there is only one file in the zip or we take the first one
            filename = zipfile.namelist()[0]
            with zipfile.open(filename) as z_f:
                # TextIOWrapper to decode
                import io
                stream = io.TextIOWrapper(z_f, encoding="utf-8-sig")
                import_from_csv(stream, db, limit)


def import_from_csv(csv_stream: TextIO, db: AozoraFirestore, limit: int = 0):
    """Import books, persons, and contributors from a CSV file."""
    csv_obj = DictReader(csv_stream, fieldnames=FIELD_NAMES)

    next(csv_obj)  # skip the first row (header in Japanese usually, but we forced fieldnames)

    # We need to skip the ACTUAL header row of the CSV if fieldnames are provided to DictReader
    # The Aozora CSV usually has a header row.
    # 'next(csv_obj)' consumes the first data row if FIELD_NAMES matches the header?
    # No, DictReader consumes the first row as keys if fieldnames is None.
    # If fieldnames IS provided, the first row is read as data.
    # So we must manually skip the header row.

    # Optimization: Cache seen persons in this run to avoid redundant writes/checks for every book.
    seen_persons: Set[str] = set()

    # Pre-fetch existing data in Firestore
    db.prefetch_metadata()

    count = 0
    for row in csv_obj:
        if limit > 0 and count >= limit:
            break

        try:
            # Parse IDs
            book_id = row["book_id"]
            person_id = row["person_id"]

            # Prepare Book Data
            # (Select fields belonging to Book)
            book_data = {
                "book_id": _parse_int(book_id),
                "title": row["title"],
                "title_yomi": row["title_yomi"],
                "title_sort": row["title_sort"],
                "subtitle": row["subtitle"],
                "subtitle_yomi": row["subtitle_yomi"],
                "original_title": row["original_title"],
                "first_appearance": row["first_appearance"],
                "ndc_code": row["ndc_code"],
                "font_kana_type": row["font_kana_type"],
                "copyright": _parse_bool(row["copyright"]),
                "release_date": _parse_date(row["release_date"]),
                "last_modified": _parse_date(row["last_modified"]),
                "card_url": row["card_url"],
                "base_book_1": row["base_book_1"],
                "base_book_1_publisher": row["base_book_1_publisher"],
                # ... include other book fields ...
                "input": row["input"],
                "proofing": row["proofing"],
                "text_url": row["text_url"],
                "text_last_modified": _parse_date(row["text_last_modified"]),
                "text_encoding": row["text_encoding"],
                "text_charset": row["text_charset"],
                "text_updated": _parse_int(row["text_updated"]),
                "html_url": row["html_url"],
                "html_last_modified": _parse_date(row["html_last_modified"]),
                "html_encoding": row["html_encoding"],
                "html_charset": row["html_charset"],
                "html_updated": _parse_int(row["html_updated"]),
            }

            db.upsert_book(book_id, book_data)

            # Prepare Person Data
            if person_id not in seen_persons:
                person_data = {
                    "person_id": _parse_int(person_id),
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "last_name_yomi": row["last_name_yomi"],
                    "first_name_yomi": row["first_name_yomi"],
                    "last_name_sort": row["last_name_sort"],
                    "first_name_sort": row["first_name_sort"],
                    "last_name_roman": row["last_name_roman"],
                    "first_name_roman": row["first_name_roman"],
                    "date_of_birth": row["date_of_birth"],
                    "date_of_death": row["date_of_death"],
                    "author_copyright": _parse_bool(row["author_copyright"]),
                }
                db.upsert_person(person_id, person_data)
                seen_persons.add(person_id)

            # Prepare Contributor Data
            role_id = _parse_role(row["role"])
            contributor_id = f"{book_id}-{person_id}-{role_id}"
            contributor_data = {
                "id": contributor_id,
                "book_id": _parse_int(book_id),
                "person_id": _parse_int(person_id),
                "role": role_id
            }
            db.upsert_contributor(contributor_id, contributor_data)

            count += 1

        except Exception as e:
            logger.error(f"Error processing row {row}: {e}")
            # continue or raise? raise for now to debug
            raise

    # Commit any remaining batch
    db.commit()
