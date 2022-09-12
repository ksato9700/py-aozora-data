import logging

from .db.db_rdb import DB
from .importer.csv_importer import import_from_csv

logging.basicConfig(level=logging.WARN)
# from .importer.pid_importer import import_from_pid


def main():
    db = DB("sqlite:///./test.db")
    import_from_csv(db)
    # import_from_pid(db)


if __name__ == "__main__":
    main()
