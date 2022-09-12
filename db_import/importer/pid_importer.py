# from lxml import html
# from scrapy import Spider


# class PidSpider(Spider):
#     name = "pid_spider"
#     # start_urls = ["http://reception.aozora.gr.jp/widlist.php?page=1&pagerow=-1"]
#     # start_urls = ['file:///Users/ksato/git/py_db_import/pid.html']
#     start_urls = ["http://localhost:9000/pid.html"]

#     def parse(self, response):
#         def _pidnames(trv):
#             tds = trv.xpath("td/text()")
#             return {
#                 "id": int(tds[0].strip()),
#                 "name": tds[1].strip().replace("　", " "),
#             }

#         a = html.fromstring(response.text)
#         for trv in a.cssselect("tr[valign]")[1:]:
#             print(_pidnames(trv))

#         # for trv in response.css("tr[valign]")[1:]:
#         #     print(_pidnames(trv))

#         # count = DB().pid_import_data(_pidnames(trv) for trv in response.css('tr[valign]')[1:])
#         # self.logger.info('%d entries are updated', count)
