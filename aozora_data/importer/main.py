import os

from ..db.db_rdb import DB
from .csv_importer import import_from_csv
from .pid_importer import import_from_pid

CSV_URL = os.environ.get(
    "AOZORA_CSV_URL",
    "https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip",
)
PID_URL = os.environ.get(
    "AOZORA_PID_URL",
    "http://reception.aozora.gr.jp/widlist.php?page=1&pagerow=-1",
)


def main():
    db = DB("sqlite:///./test.db")
    import_from_csv(CSV_URL, db)
    import_from_pid(PID_URL, db)


if __name__ == "__main__":
    main()
