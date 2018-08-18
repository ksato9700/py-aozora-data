# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import os
import logging
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient, ReplaceOne
from dateutil import parser

load_dotenv(find_dotenv(), override=True)

MONGO_URL = 'mongodb://{}{}:{}'.format(
    os.environ.get('AOZORA_MONGODB_CREDENTIAL', ''),
    os.environ.get('AOZORA_MONGODB_HOST', 'localhost'),
    os.environ.get('AOZORA_MONGODB_PORT', '27017'),
    )

ROLE_MAP = {
    '著者': 'authors',
    '翻訳者': 'translators',
    '編者': 'editors',
    '校訂者': 'revisers',
}

FIELD_NAMES = (
    'book_id',
    'title',
    'title_yomi',
    'title_sort',
    'subtitle',
    'subtitle_yomi',
    'original_title',
    'first_appearance',
    'ndc_code',
    'font_kana_type',
    'copyright',
    'release_date',
    'last_modified',
    'card_url',
    'person_id',
    'last_name',
    'first_name',
    'last_name_yomi',
    'first_name_yomi',
    'last_name_sort',
    'first_name_sort',
    'last_name_roman',
    'first_name_roman',
    'role',
    'date_of_birth',
    'date_of_death',
    'author_copyright',
    'base_book_1',
    'base_book_1_publisher',
    'base_book_1_1st_edition',
    'base_book_1_edition_input',
    'base_book_1_edition_proofing',
    'base_book_1_parent',
    'base_book_1_parent_publisher',
    'base_book_1_parent_1st_edition',
    'base_book_2',
    'base_book_2_publisher',
    'base_book_2_1st_edition',
    'base_book_2_edition_input',
    'base_book_2_edition_proofing',
    'base_book_2_parent',
    'base_book_2_parent_publisher',
    'base_book_2_parent_1st_edition',
    'input',
    'proofing',
    'text_url',
    'text_last_modified',
    'text_encoding',
    'text_charset',
    'text_updated',
    'html_url',
    'html_last_modified',
    'html_encoding',
    'html_charset',
    'html_updated',
)


def _type_conversion(key, val):
    if key in ('copyright', 'author_copyright'):
        return val != 'なし'

    elif key in ('book_id', 'person_id', 'text_updated', 'html_updated'):
        return -1 if val == '' else int(val)

    elif key in ('release_date', 'last_modified', 'text_last_modified', 'html_last_modified'):
        return None if val == '' else parser.parse(val)

    elif key == 'role':
        return ROLE_MAP.get(val, 'others')

    else:
        return val


def _create_objs(row):
    book = {}
    person = {}
    for idx, key in enumerate(FIELD_NAMES):
        val = _type_conversion(key, row[idx])

        if key in ('person_id', 'first_name', 'last_name', 'last_name_yomi', 'first_name_yomi',
                   'last_name_sort', 'first_name_sort', 'last_name_roman', 'first_name_roman',
                   'date_of_birth', 'date_of_death', 'author_copyright'):
            person[key] = val

        elif key == 'role':
            role = val

        else:
            book[key] = val

    return book, person, role


class DB:
    def __init__(self):
        self.db_client = MongoClient(MONGO_URL + '/aozora').aozora

    def csv_updated(self, data, refresh):
        next(data)
        logger = get_logger('__init__.csv_updated')
        if refresh:
            return data
        books = self.db_client.books
        the_latest_item = books.find_one({},
                                         projection={'release_date': 1},
                                         sort=[('release_date', -1)])
        logger.debug('the_latest_item: %s', the_latest_item)
        if the_latest_item:
            last_release_date = str(the_latest_item['release_date'].date())
            logger.debug('last_release_date: %s', last_release_date)

            def _compare_date(date_a, date_b):
                if date_a < date_b:
                    logger.debug('_compare_date: %s < %s', date_a, date_b)
                return date_a < date_b

            return filter(lambda e: _compare_date(last_release_date, e[11]), data)
        else:
            return data

    def _store_books(self, books_batch):
        bulk_ops = [ReplaceOne({'book_id': book_id},
                               books_batch[book_id],
                               upsert=True) for book_id in books_batch]

        if bulk_ops:
            return self.db_client.books.bulk_write(bulk_ops, ordered=False)
        else:
            return None

    def _store_persons(self, persons_batch):
        bulk_ops = [ReplaceOne({'person_id': person_id},
                               persons_batch[person_id],
                               upsert=True) for person_id in persons_batch]

        if bulk_ops:
            return self.db_client.persons.bulk_write(bulk_ops, ordered=False)
        else:
            return None

    def csv_import_data(self, updated):
        books_batch = {}
        persons_batch = {}
        for book, person, role in map(_create_objs, updated):
            book_id = book['book_id']
            if book_id not in books_batch:
                # book['persons'] = []
                books_batch[book_id] = book

            if role not in books_batch[book_id]:
                books_batch[book_id][role] = []

            person_id = person['person_id']
            last_name = person['last_name']
            first_name = person['first_name']
            books_batch[book_id][role].append({
                'person_id': person_id,
                'last_name': last_name,
                'first_name': first_name,
            })

            # books_batch[book_id]['persons'].append({
            #     'person_id': person_id,
            #     'last_name': last_name,
            #     'first_name': first_name,
            #     'role': role
            # })
            if person_id not in persons_batch:
                persons_batch[person_id] = person

        res = (self._store_books(books_batch), self._store_persons(persons_batch))
        return res[0].upserted_count + res[0].modified_count if res[0] else 0

    def pid_import_data(self, data):
        bulk_ops = [ReplaceOne({'id': item['id']}, item, upsert=True) for item in data]

        if bulk_ops:
            res = self.db_client.workers.bulk_write(bulk_ops, ordered=False)
            return res.upserted_count
        else:
            return 0


def get_logger(name):
    level = logging.root.getEffectiveLevel()
    level = logging.INFO if level == logging.NOTSET else level
    from scrapy.utils.log import get_scrapy_root_handler
    root_handler = get_scrapy_root_handler()
    if root_handler:
        root_handler.setLevel(level)

    logging.getLogger('scrapy').setLevel(logging.WARNING)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
