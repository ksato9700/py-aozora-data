#!/usr/bin/env python
import logging
from scrapy.http import Response
from db_import.spiders.csv_spider import CSVSpider


def main():
    logging.basicConfig(level=logging.DEBUG)

    with open('list_person_all_extended_utf8.zip', 'rb') as rfp:
        csv_spider = CSVSpider()
        csv_spider.parse(Response('', body=rfp.read()))


if __name__ == '__main__':
    main()
