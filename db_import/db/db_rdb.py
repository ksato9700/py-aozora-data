import logging

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    create_engine,
    update,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"
    book_id = Column("book_id", Integer, primary_key=True)
    title = Column("title", String)
    title_yomi = Column("title_yomi", String)
    title_sort = Column("title_sort", String)
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


class Person(Base):
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


class Contributor(Base):
    __tablename__ = "contributors"
    contributor_id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.book_id"))
    person_id = Column(Integer, ForeignKey("persons.person_id"))
    role = Column("role", Integer)


class DB:
    def __init__(self, engine: str = "sqlite+pysqlite:///:memory:"):
        engine = create_engine(engine, echo=False, future=True)
        Base.metadata.create_all(bind=engine)
        self.db = sessionmaker(autocommit=False, autoflush=False, bind=engine)()

    def __del__(self):
        self.db.close()

    def store_book(self, data: dict):
        book = self.db.query(Book).filter(Book.book_id == data["book_id"]).first()
        if book:
            pass
            # stmt = update(Book).where(Book.book_id == data["book_id"]).values(**data)
            # self.db.execute(stmt)
        else:
            self.db.add(Book(**data))
            self.db.commit()

    def store_person(self, data: dict):
        person = (
            self.db.query(Person).filter(Person.person_id == data["person_id"]).first()
        )
        if person:
            pass
        else:
            self.db.add(Person(**data))
            self.db.commit()

    def store_contributor(self, data: dict):
        contributor = (
            self.db.query(Contributor)
            .filter(
                (Contributor.book_id == data["book_id"]),
                (Contributor.person_id == data["person_id"]),
                (Contributor.role == data["role"].value),
            )
            .first()
        )
        if contributor:
            print(f"{data['book_id']=}, {data['person_id']=}, {data['role']=}")
            pass
        else:
            if data["book_id"] == 4583:
                print(data)
                a = 0 / 1
            data["role"] = data["role"].value
            self.db.add(Contributor(**data))
            self.db.commit()
