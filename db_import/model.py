from datetime import date
from enum import Enum

from pydantic import BaseModel, HttpUrl, validator


class Role(Enum):
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


class Book(BaseModel):
    book_id: int
    title: str
    title_yomi: str
    title_sort: str
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
        return val != "なし"

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
        return val != "なし"


# def main():
#     book_data = {
#         "book_id": "059898",
#         "title": "ウェストミンスター寺院",
#         "title_yomi": "ウェストミンスターじいん",
#         "title_sort": "うえすとみんすたあしいん",
#         "subtitle": "",
#         "subtitle_yomi": "",
#         "original_title": "",
#         "first_appearance": "",
#         "ndc_code": "NDC 933",
#         "font_kana_type": "新字新仮名",
#         "copyright": "なし",
#         "release_date": "2020-04-03",
#         "last_modified": "2020-03-28",
#         "card_url": "https://www.aozora.gr.jp/cards/001257/card59898.html",
#         "person_id": "001257",
#         "last_name": "アーヴィング",
#         "first_name": "ワシントン",
#         "last_name_yomi": "アーヴィング",
#         "first_name_yomi": "ワシントン",
#         "last_name_sort": "ああういんく",
#         "first_name_sort": "わしんとん",
#         "last_name_roman": "Irving",
#         "first_name_roman": "Washington",
#         "role": "著者",
#         "date_of_birth": "1783-04-03",
#         "date_of_death": "1859-11-28",
#         "author_copyright": "なし",
#         "base_book_1": "スケッチ・ブック",
#         "base_book_1_publisher": "新潮文庫、新潮社",
#         "base_book_1_1st_edition": "1957（昭和32）年5月20日",
#         "base_book_1_edition_input": "2000（平成12）年2月20日33刷改版",
#         "base_book_1_edition_proofing": "2000（平成12）年2月20日33刷改版",
#         "base_book_1_parent": "",
#         "base_book_1_parent_publisher": "",
#         "base_book_1_parent_1st_edition": "",
#         "base_book_2": "",
#         "base_book_2_publisher": "",
#         "base_book_2_1st_edition": "",
#         "base_book_2_edition_input": "",
#         "base_book_2_edition_proofing": "",
#         "base_book_2_parent": "",
#         "base_book_2_parent_publisher": "",
#         "base_book_2_parent_1st_edition": "",
#         "input": "えにしだ",
#         "proofing": "砂場清隆",
#         "text_url": "https://www.aozora.gr.jp/cards/001257/files/59898_ruby_70679.zip",
#         "text_last_modified": "2020-03-28",
#         "text_encoding": "ShiftJIS",
#         "text_charset": "JIS X 0208",
#         "text_updated": "0",
#         "html_url": "https://www.aozora.gr.jp/cards/001257/files/59898_70731.html",
#         "html_last_modified": "2020-03-28",
#         "html_encoding": "ShiftJIS",
#         "html_charset": "JIS X 0208",
#         "html_updated": "0",
#     }
#     book = Book(**book_data)
#     print(book)


# if __name__ == "__main__":
#     main()
