import logging

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..model import Book, Contributor, Person, Worker

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

Base = declarative_base()


class DbBook(Base):
    __tablename__ = "books"
    book_id = Column("book_id", Integer, primary_key=True)
    title = Column("title", String)
    title_yomi = Column("title_yomi", String)
    title_sort = Column("title_sort", String)
    subtitle = Column("subtitle", String)
    subtitle_yomi = Column("subtitle_yomi", String)
    original_title = Column("original_title", String)
    first_appearance = Column("first_appearance", String)
    ndc_code = Column("ndc_code", String)
    font_kana_type = Column("font_kana_type", String)
    copyright = Column("copyright", Boolean)
    release_date = Column("release_date", Date)
    last_modified = Column("last_modified", Date)
    card_url = Column("card_url", String)
    base_book_1 = Column("base_book_1", String)
    base_book_1_publisher = Column("base_book_1_publisher", String)
    base_book_1_1st_edition = Column("base_book_1_1st_edition", String)
    base_book_1_edition_input = Column("base_book_1_edition_input", String)
    base_book_1_edition_proofing = Column("base_book_1_edition_proofing", String)
    base_book_1_parent = Column("base_book_1_parent", String)
    base_book_1_parent_publisher = Column("base_book_1_parent_publisher", String)
    base_book_1_parent_1st_edition = Column("base_book_1_parent_1st_edition", String)
    base_book_2 = Column("base_book_2", String)
    base_book_2_publisher = Column("base_book_2_publisher", String)
    base_book_2_1st_edition = Column("base_book_2_1st_edition", String)
    base_book_2_edition_input = Column("base_book_2_edition_input", String)
    base_book_2_edition_proofing = Column("base_book_2_edition_proofing", String)
    base_book_2_parent = Column("base_book_2_parent", String)
    base_book_2_parent_publisher = Column("base_book_2_parent_publisher", String)
    base_book_2_parent_1st_edition = Column("base_book_2_parent_1st_edition", String)
    input = Column("input", String)
    proofing = Column("proofing", String)
    text_url = Column("text_url", String)
    text_last_modified = Column("text_last_modified", Date)
    text_encoding = Column("text_encoding", String)
    text_charset = Column("text_charset", String)
    text_updated = Column("text_updated", Integer)
    html_url = Column("html_url", String)
    html_last_modified = Column("html_last_modified", Date)
    html_encoding = Column("html_encoding", String)
    html_charset = Column("html_charset", String)
    html_updated = Column("html_updated", Integer)


class DbPerson(Base):
    __tablename__ = "persons"
    person_id = Column("person_id", Integer, primary_key=True)
    first_name = Column("first_name", String)
    last_name = Column("last_name", String)
    last_name_yomi = Column("last_name_yomi", String)
    first_name_yomi = Column("first_name_yomi", String)
    last_name_sort = Column("last_name_sort", String)
    first_name_sort = Column("first_name_sort", String)
    last_name_roman = Column("last_name_roman", String)
    first_name_roman = Column("first_name_roman", String)
    date_of_birth = Column("date_of_birth", String)
    date_of_death = Column("date_of_death", String)
    author_copyright = Column("author_copyright", Boolean)


class DbContributor(Base):
    __tablename__ = "contributors"
    contributor_id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.book_id"))
    person_id = Column(Integer, ForeignKey("persons.person_id"))
    role = Column("role", Integer)


class DbWorker(Base):
    __tablename__ = "workers"
    worker_id = Column(Integer, primary_key=True)
    name = Column("name", String)


class DB:
    def __init__(self, engine: str = "sqlite+pysqlite:///:memory:"):
        engine = create_engine(engine, echo=False, future=True)
        Base.metadata.create_all(bind=engine)
        self.db = sessionmaker(autocommit=False, autoflush=False, bind=engine)()

    def __del__(self):
        self.db.close()

    def _get_books(self, limit=100) -> DbBook:
        return self.db.query(DbBook).limit(limit)

    def _get_book(self, book_id: int) -> DbBook:
        return self.db.query(DbBook).filter(DbBook.book_id == book_id).first()

    def _get_person(self, person_id: int) -> DbPerson:
        return self.db.query(DbPerson).filter(DbPerson.person_id == person_id).first()

    def _get_contributor(self, book_id: int, person_id: int) -> DbContributor:
        return (
            self.db.query(DbContributor)
            .filter(
                DbContributor.book_id == book_id, DbContributor.person_id == person_id
            )
            .first()
        )

    def _get_worker(self, worker_id: int) -> DbWorker:
        return self.db.query(DbWorker).filter(DbWorker.worker_id == worker_id).first()

    def get_books(self) -> list[Book]:
        return [Book(**(book.__dict__)) for book in self._get_books()]

    def get_book(self, book_id: int) -> Book | None:
        book = self._get_book(book_id)
        if book:
            book_dict = book.__dict__
            return Book(**book_dict)
        else:
            return None

    def get_person(self, person_id: int) -> Person | None:
        person = self._get_person(person_id)
        if person:
            person_dict = person.__dict__
            return Person(**person_dict)
        else:
            return None

    def get_contributor(self, book_id: int, person_id: int) -> Contributor | None:
        contributor = self._get_contributor(book_id, person_id)
        if contributor:
            contributor_dict = contributor.__dict__
            return Contributor(**contributor_dict)
        else:
            return None

    def get_worker(self, worker_id: int) -> Worker | None:
        worker = self._get_worker(worker_id)
        if worker:
            worker_dict = worker.__dict__
            return Worker(**worker_dict)
        else:
            return None

    def store_book(self, data: dict):
        book = self._get_book(data["book_id"])

        if book:
            pass
            # stmt = update(Book).where(Book.book_id == data["book_id"]).values(**data)
            # self.db.execute(stmt)
        else:
            self.db.add(DbBook(**data))
            self.db.commit()

    def store_person(self, data: dict):
        person = (
            self.db.query(DbPerson)
            .filter(DbPerson.person_id == data["person_id"])
            .first()
        )
        if person:
            pass
        else:
            self.db.add(DbPerson(**data))
            self.db.commit()

    def store_contributor(self, data: dict):
        contributor = (
            self.db.query(DbContributor)
            .filter(
                (DbContributor.book_id == data["book_id"]),
                (DbContributor.person_id == data["person_id"]),
                (DbContributor.role == data["role"].value),
            )
            .first()
        )
        if not contributor:
            data["role"] = data["role"].value
            self.db.add(DbContributor(**data))
            self.db.commit()

    def store_worker(self, data: dict):
        worker = (
            self.db.query(DbWorker)
            .filter(DbWorker.worker_id == data["worker_id"])
            .first()
        )
        if worker:
            pass
        else:
            self.db.add(DbWorker(**data))
            self.db.commit()
