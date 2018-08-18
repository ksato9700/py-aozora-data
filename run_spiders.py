from scrapy.crawler import CrawlerProcess
from db_import.spiders.csv_spider import CSVSpider
from db_import.spiders.pid_spider import PidSpider


def main():
    process = CrawlerProcess()
    process.crawl(CSVSpider)
    process.crawl(PidSpider)
    process.start()


if __name__ == '__main__':
    main()
