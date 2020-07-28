import threading
import time
import re
import requests
from common.logger import get_logger

logger = get_logger('producer')


class SiteChecker(object):
    """ Web site checker
        It checks periodicaly site for availability and
        checks response for expected content with regular expressions.
        It performs checks in a background thread.

        Arguments:
            site(Site): site to check
            check_interval(int): interval in seconds between checks
    """
    def __init__(self, site, check_interval):
        self.site = site
        self.check_interval = check_interval
        self.thread = None
        self.stopping = threading.Event()

    def start(self, on_url_check_completed_cb):
        self.stopping.clear()
        self.thread = threading.Thread(target=self.execute,
                                       args=(on_url_check_completed_cb,))
        self.thread.start()
        logger.debug("Started checker {url}".format(url=self.site.url))

    def stop(self):
        logger.debug("Stopping checker {url}".format(url=self.site.url))
        self.stopping.set()
        self.thread.join()
        self.thread = None

    def execute(self, on_url_check_completed_cb):
        while not self.stopping.isSet():
            try:
                logger.debug("Checking [{site_id}]{url}".format(
                    site_id=self.site.id, url=self.site.url))
                start = time.time()
                resp = requests.get(self.site.url)
                end = time.time()
                failed_regexps = []
                for regexp in self.site.regexps:
                    if re.match(regexp.regexp, resp.text) is None:
                        failed_regexps.append(regexp.id)
                on_url_check_completed_cb(self.site.id,
                                          resp.status_code,
                                          int((end-start) * 1000),
                                          failed_regexps)
            except Exception as ex:
                logger.exception(ex)
            self.stopping.wait(self.check_interval)
