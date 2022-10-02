import logging

import requests
from lxml import html

from ..model import Worker

logger = logging.getLogger(__name__)


def import_from_pid(pid_url: str, db):
    resp = requests.get(pid_url)
    resp.raise_for_status()

    top = html.fromstring(resp.text)
    for trv in top.cssselect("tr[valign]")[1:]:
        tds = trv.xpath("td/text()")
        worker = Worker(
            worker_id=tds[0].strip(),
            name=tds[1].strip().replace("　", " "),
        )
        db.store_worker(worker.dict())
