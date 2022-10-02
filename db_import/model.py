from datetime import date
from enum import IntEnum
from xml.dom import ValidationErr

from pydantic import BaseModel, HttpUrl, validator


class Role(IntEnum):
    AUTHOR = 0
    TRANSLATOR = 1
    EDITOR = 2
    REVISOR = 3
    OTHER = 4


class Contributor(BaseModel):
    book_id: int
    person_id: int
    role: Role

    @validator("role", pre=True)
    def validate_role(val):
        match val:
            case Role(val):
                return val
            case int(val):
                if val in Role.__members__.values():
                    return Role(val)
                else:
                    raise ValueError(f"{val}")
            case str(val):
                match val:
                    case "著者":
                        return Role.AUTHOR
                    case "翻訳者":
                        return Role.TRANSLATOR
                    case "編者":
                        return Role.EDITOR
                    case "校訂者":
                        return Role.REVISOR
                    case "その他":
                        return Role.OTHER
                    case _:
                        raise ValueError(f"{val}")
            case _:
                raise ValueError(f"{val}")


class Book(BaseModel):
    book_id: int
    title: str
    title_yomi: str
    title_sort: str
    subtitle: str
    subtitle_yomi: str
    original_title: str
    first_appearance: str
    ndc_code: str
    font_kana_type: str
    copyright: bool
    release_date: date
    last_modified: date
    card_url: HttpUrl
    base_book_1: str
    base_book_1_publisher: str
    base_book_1_1st_edition: str
    base_book_1_edition_input: str
    base_book_1_edition_proofing: str
    base_book_1_parent: str
    base_book_1_parent_publisher: str
    base_book_1_parent_1st_edition: str
    base_book_2: str
    base_book_2_publisher: str
    base_book_2_1st_edition: str
    base_book_2_edition_input: str
    base_book_2_edition_proofing: str
    base_book_2_parent: str
    base_book_2_parent_publisher: str
    base_book_2_parent_1st_edition: str
    input: str
    proofing: str
    text_url: HttpUrl | None
    text_last_modified: date | None
    text_encoding: str
    text_charset: str
    text_updated: int
    html_url: HttpUrl | None
    html_last_modified: date | None
    html_encoding: str
    html_charset: str
    html_updated: int

    @validator("copyright", pre=True)
    def validate_copyright(cls, val) -> bool:
        match val:
            case bool(val):
                return val
            case str(val):
                return val != "なし"
            case _:
                ValidationErr(f"{val}")

    @validator(
        "text_url", "text_last_modified", "html_url", "html_last_modified", pre=True
    )
    def validate_str_nullable(cls, val) -> str | None:
        return None if val == "" else val

    @validator("text_updated", "html_updated", pre=True)
    def validate_text_updated(cls, val) -> int:
        return 0 if val == "" else int(val)


class Person(BaseModel):
    person_id: int
    first_name: str
    last_name: str
    last_name_yomi: str
    first_name_yomi: str
    last_name_sort: str
    first_name_sort: str
    last_name_roman: str
    first_name_roman: str
    date_of_birth: str
    date_of_death: str
    author_copyright: bool

    @validator("author_copyright", pre=True)
    def validate_copyright(cls, val) -> bool:
        match val:
            case bool(val):
                return val
            case str(val):
                return val != "なし"
            case _:
                ValidationErr(f"{val}")


class Worker(BaseModel):
    worker_id: int
    name: str


# def main():
#     book = Book(**book_data)
#     print(book)


# if __name__ == "__main__":
#     main()
