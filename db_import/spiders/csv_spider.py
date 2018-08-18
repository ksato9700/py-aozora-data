from io import BytesIO, StringIO
from zipfile import ZipFile
import csv

from scrapy import Spider

from db_import.spiders import get_logger, DB

URL_BASE = 'https://www.aozora.gr.jp/index_pages/'
CSV_FILE = 'list_person_all_extended_utf8.zip'


def _get_csv(data):
    with ZipFile(BytesIO(data)) as zipfile:
        csvdata = zipfile.read(zipfile.namelist()[0]).decode('utf-8-sig')
        return csv.reader(StringIO(csvdata))


class CSVSpider(Spider):
    name = 'csv_spider'
    start_urls = [URL_BASE + CSV_FILE]

    def parse(self, response):
        dbc = DB()
        refresh = False
        updated = dbc.csv_updated(_get_csv(response.body), refresh)
        logger = get_logger('CSVSpider::parse')
        updated = list(updated)
        logger.debug(updated)
        count = dbc.csv_import_data(updated)
        logger.info('%d entries are updated', count)
