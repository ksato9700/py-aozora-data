from .db.db_rdb import DB
from .importer.csv_importer import import_from_csv
from .importer.pid_importer import import_from_pid

CSV_URL = "https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip"
# CSV_URL = "http://localhost:9000/list_person_all_extended_utf8.zip"

PID_URL = "http://reception.aozora.gr.jp/widlist.php?page=1&pagerow=-1"
# PID_URL = "http://localhost:9000/pid.html"


def main():
    db = DB("sqlite:///./test.db")
    import_from_csv(CSV_URL, db)
    import_from_pid(PID_URL, db)


if __name__ == "__main__":
    main()
