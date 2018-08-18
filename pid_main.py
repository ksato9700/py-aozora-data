#!/usr/bin/env python
import logging
from scrapy.http import TextResponse
from db_import.spiders.pid_spider import PidSpider


def main():
    logging.basicConfig(level=logging.DEBUG)

    with open('pid.html', 'rb') as rfp:
        pid_spider = PidSpider()
        pid_spider.parse(TextResponse('', body=rfp.read()))


if __name__ == '__main__':
    main()
