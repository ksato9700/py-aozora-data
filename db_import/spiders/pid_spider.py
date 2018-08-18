from scrapy import Spider
from db_import.spiders import get_logger, DB


class PidSpider(Spider):
    name = 'pid_spider'
    start_urls = ['http://reception.aozora.gr.jp/widlist.php?page=1&pagerow=-1']
    # start_urls = ['file:///Users/ksato/git/py_db_import/pid.html']

    def parse(self, response):
        def _pidnames(trv):
            tds = trv.xpath('td/text()').extract()
            return {
                'id': int(tds[0].strip()),
                'name': tds[1].strip().replace('　', ' '),
            }

        count = DB().pid_import_data(_pidnames(trv) for trv in response.css('tr[valign]')[1:])
        get_logger('PidSpider::parse').info('%d entries are updated', count)
