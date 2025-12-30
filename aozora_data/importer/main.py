import os

from ..db.firestore import AozoraFirestore
from .csv_importer import import_from_csv_url

CSV_URL = os.environ.get(
    "AOZORA_CSV_URL",
    "https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip",
)
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")


def main():
    """Import data from CSV to Firestore."""
    db = AozoraFirestore(project_id=PROJECT_ID)
    if CSV_URL:
        import_from_csv_url(CSV_URL, db)


if __name__ == "__main__":
    main()
