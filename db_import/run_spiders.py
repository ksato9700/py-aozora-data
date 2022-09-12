import logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

from db_import.spiders.csv_spider import CSVSpider
from db_import.spiders.pid_spider import PidSpider


def main():
    configure_logging({"LOG_LEVEL": logging.WARNING})
    # CSVSpider.custom_settings = {'LOG_LEVEL': logging.WARNING}
    # PidSpider.custom_settings = {'LOG_LEVEL': logging.WARNING}

    process = CrawlerProcess()
    # process.crawl(CSVSpider)
    process.crawl(PidSpider)
    process.start()


if __name__ == "__main__":
    main()
