import logging

from .db.db_rdb import DB
from .importer.csv_importer import import_from_csv

# logging.basicConfig(level=logging.WARN)
# from .importer.pid_importer import import_from_pid

# CSV_URL = "https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip"
CSV_URL = "http://localhost:9000/list_person_all_extended_utf8.zip"
# CSV_URL = "http://localhost:9000/xx.zip"


def main():
    db = DB("sqlite:///./test.db")
    import_from_csv(CSV_URL, db)
    # import_from_pid(db)


if __name__ == "__main__":
    main()
